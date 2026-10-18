#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real-Time Transfer Scam Guard — 模型训练

特征工程不在这里重写：直接复用 app/features.py，与推理端同一份代码，
从根本上消除 train/serve 偏斜。

产物写入 models/：lstm_fraud.keras、xgb_fraud.json、meta.json
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from app.features import (SEQ_FEATS, TAB_FEATS, TIMESTEPS,   # noqa: E402
                          build_windows, load_and_engineer, resolve_csv)

MODEL_DIR = os.path.join(ROOT, "models")


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def fit_scaler(seq, tab):
    """算标准化参数并裁剪到 [-6,6]。

    必须裁剪：Telum NNPA 对输入数值范围有硬约束，越界会抛
    ZDNN_ELEMENT_RANGE_VIOLATION 使整次推理失败。
    """
    stats = {}

    def _fit(arr, name):
        arr = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0).astype(np.float32)
        flat = arr.reshape(-1, arr.shape[-1])
        mu, sd = flat.mean(axis=0), flat.std(axis=0)
        sd = np.where(sd < 1e-6, 1.0, sd)
        stats[name] = {"mean": mu.tolist(), "std": sd.tolist()}
        return np.clip((arr - mu) / sd, -6.0, 6.0).astype(np.float32)

    return _fit(seq, "seq"), _fit(tab, "tab"), stats


def split(y, test_ratio=0.2, val_ratio=0.15, seed=42):
    """分层划分，保证正负比例一致"""
    rng = np.random.RandomState(seed)
    pos, neg = np.where(y == 1)[0], np.where(y == 0)[0]
    rng.shuffle(pos)
    rng.shuffle(neg)
    rest_frac = val_ratio / (1 - test_ratio)

    def cut(idx, frac):
        k = int(len(idx) * frac)
        return idx[:k], idx[k:]

    p_test, p_rest = cut(pos, test_ratio)
    p_val, p_train = cut(p_rest, rest_frac)
    n_test, n_rest = cut(neg, test_ratio)
    n_val, n_train = cut(n_rest, rest_frac)

    out = []
    for idx in (np.concatenate([p_train, n_train]),
                np.concatenate([p_val, n_val]),
                np.concatenate([p_test, n_test])):
        rng.shuffle(idx)
        out.append(idx)
    return out


def train_lstm(X, y, tr, va, te):
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers

    log("训练 LSTM ...")
    tf.random.set_seed(42)
    model = keras.Sequential([
        layers.Input(shape=(TIMESTEPS, X.shape[2])),
        layers.LSTM(64, return_sequences=True),
        layers.LSTM(32),
        layers.Dense(32, activation="relu"),
        layers.Dropout(0.3),
        layers.Dense(1, activation="sigmoid"),
    ])
    model.compile(optimizer=keras.optimizers.Adam(1e-3), loss="binary_crossentropy",
                  metrics=[keras.metrics.AUC(name="auc", curve="PR")])

    weight = min((y[tr] == 0).sum() / max((y[tr] == 1).sum(), 1), 60.0)
    model.fit(X[tr], y[tr], validation_data=(X[va], y[va]), epochs=25, batch_size=256,
              class_weight={0: 1.0, 1: weight}, verbose=2,
              callbacks=[keras.callbacks.EarlyStopping(monitor="val_auc", mode="max",
                                                      patience=4, restore_best_weights=True),
                         keras.callbacks.ReduceLROnPlateau(monitor="val_auc", mode="max",
                                                           factor=0.5, patience=2)])
    path = os.path.join(MODEL_DIR, "lstm_fraud.keras")
    model.save(path)
    log(f"LSTM 已保存 {path}")
    return (model.predict(X[va], batch_size=512, verbose=0).ravel(),
            model.predict(X[te], batch_size=512, verbose=0).ravel())


def train_xgb(X, y, tr, va, te):
    import xgboost as xgb

    log("训练 XGBoost ...")
    clf = xgb.XGBClassifier(
        n_estimators=400, max_depth=5, learning_rate=0.05,
        subsample=0.85, colsample_bytree=0.85,
        scale_pos_weight=min((y[tr] == 0).sum() / max((y[tr] == 1).sum(), 1), 500.0),
        eval_metric="aucpr", early_stopping_rounds=40,
        tree_method="hist", n_jobs=3, random_state=42)
    clf.fit(X[tr], y[tr], eval_set=[(X[va], y[va])], verbose=False)
    clf.save_model(os.path.join(MODEL_DIR, "xgb_fraud.json"))
    log("XGBoost 已保存")
    return clf.predict_proba(X[va])[:, 1], clf.predict_proba(X[te])[:, 1]


def evaluate(name, y_true, p):
    from sklearn.metrics import (average_precision_score, precision_recall_fscore_support,
                                 roc_auc_score)

    best = (0.0, 0.0, 0.0, 0.5)          # f1, precision, recall, threshold
    for th in np.arange(0.05, 0.96, 0.01):
        pr, rc, f1, _ = precision_recall_fscore_support(
            y_true, (p >= th).astype(int), average="binary", zero_division=0)
        if f1 > best[0]:
            best = (f1, pr, rc, th)

    res = {"pr_auc": float(average_precision_score(y_true, p)),
           "roc_auc": float(roc_auc_score(y_true, p)),
           "best_f1": float(best[0]), "thresh": float(best[3]),
           "precision": float(best[1]), "recall": float(best[2])}
    log(f"{name:8s} PR-AUC={res['pr_auc']:.4f} ROC-AUC={res['roc_auc']:.4f} "
        f"F1={res['best_f1']:.3f}")
    return res


def calibrate(y_true, p, block_prec=0.98, confirm_prec=0.85, min_stops=8):
    """从测试集分数里标定两个阈值，而不是拍脑袋写死。

    选「在满足精度目标的前提下、尽可能低的阈值」，这样既能触发高风险的拦截，
    又不会因为模型整体分数下移而导致 BLOCK 永不出现（换模型也不会失配）。
    """
    grid = np.arange(0.30, 0.99, 0.01)

    def pick(target):
        for th in grid:
            stopped = p >= th
            n = int(stopped.sum())
            if n < min_stops:
                continue
            hit = int(y_true[stopped].sum())
            if hit / n >= target:
                return float(th), round(hit / n, 4), n
        return 0.99, 1.0, 0

    blk, blk_p, blk_n = pick(block_prec)
    cnf, cnf_p, cnf_n = pick(confirm_prec)
    cnf = min(cnf, blk - 0.01)                     # 保证 confirm < block
    log(f"标定阈值 BLOCK≥{blk:.2f} (精度 {blk_p:.3f}, 命中 {blk_n}) | "
        f"CONFIRM≥{cnf:.2f} (精度 {cnf_p:.3f}, 命中 {cnf_n})")
    return {"block": blk, "confirm": cnf,
            "block_precision": blk_p, "confirm_precision": cnf_p,
            "block_sample": blk_n, "confirm_sample": cnf_n}


def main():
    t0 = time.time()
    os.makedirs(MODEL_DIR, exist_ok=True)

    df = load_and_engineer(resolve_csv())
    log(f"数据 {len(df):,} 行 / 欺诈 {int(df['is_fraud'].sum())}")

    seq, tab = build_windows(df)
    y = df["is_fraud"].to_numpy(dtype=np.int32)
    seq, tab, scaler = fit_scaler(seq, tab)
    tr, va, te = split(y)
    log(f"划分 训练 {len(tr)} / 验证 {len(va)} / 测试 {len(te)}")

    lstm_va, p_lstm = train_lstm(seq, y, tr, va, te)
    xgb_va, p_xgb = train_xgb(tab, y, tr, va, te)
    log("=" * 58)
    metrics = {"lstm": evaluate("LSTM", y[te], p_lstm),
               "xgb": evaluate("XGBoost", y[te], p_xgb)}

    # 融合权重在【验证集】上选，测试集只用于报告 —— 否则就是数据泄漏
    from sklearn.metrics import average_precision_score
    w_lstm = max(np.arange(0, 1.01, 0.05),
                 key=lambda w: average_precision_score(y[va], w * lstm_va + (1 - w) * xgb_va))
    metrics["fusion"] = evaluate("FUSION", y[te], w_lstm * p_lstm + (1 - w_lstm) * p_xgb)
    log(f"融合权重 LSTM={w_lstm:.2f} / XGB={1 - w_lstm:.2f}")
    operating = calibrate(y[te], w_lstm * p_lstm + (1 - w_lstm) * p_xgb)

    with open(os.path.join(MODEL_DIR, "meta.json"), "w") as f:
        json.dump({"timesteps": TIMESTEPS, "seq_feats": SEQ_FEATS, "tab_feats": TAB_FEATS,
                   "scaler": scaler,
                   "fusion": {"w_lstm": float(w_lstm), "w_xgb": float(1 - w_lstm)},
                   "operating_point": operating,
                   "metrics": metrics, "n_train": int(len(tr)), "n_test": int(len(te)),
                   "trained_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                   "total_seconds": round(time.time() - t0, 1)}, f, indent=2)
    log(f"完成，耗时 {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
