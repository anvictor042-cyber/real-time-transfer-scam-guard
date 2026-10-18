#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real-Time Transfer Scam Guard — 决策引擎

每一笔转账在授权路径内被打分，输出三种结果：
    APPROVE  放行
    CONFIRM  暂停并要求本人 + 关联家属确认
    BLOCK    直接拦截

同时产出可审计的 reason codes，以及「拦截挽回了多少钱」的业务指标。
"""
import json
import os
import threading
import time
from collections import deque

import numpy as np

from .profiles import profile_for

from .features import resolve_models

MODEL_DIR = os.environ.get("MODEL_DIR") or resolve_models()

# 三档阈值默认值；实际取值来自训练时标定的 operating_point（见 train_all.calibrate）
TH_BLOCK = float(os.environ.get("TH_BLOCK", "0.95"))
TH_CONFIRM = float(os.environ.get("TH_CONFIRM", "0.55"))

# 理由码表：code → (英文标签, 中文标签)
REASONS = {
    "R01": ("Amount far above this account's history", "金额显著高于该账户历史"),
    "R02": ("Several transfers in a very short window", "极短时间内多笔转账"),
    "R03": ("Transfer at an unusual hour", "非正常时段转账"),
    "R04": ("Remote / online channel", "远程线上渠道"),
    "R05": ("Retry after a failed attempt", "失败后重试"),
    "R06": ("Rare or first-time merchant category", "罕见或首次商户类别"),
    "R07": ("Transaction sequence looks abnormal", "交易序列异常（序列模型）"),
    "R08": ("Structured risk profile is elevated", "结构化风险偏高（GBDT）"),
    "R09": ("Amount far above the recent window average", "金额远高于近期窗口均值"),
}


class RiskEngine:
    def __init__(self, model_dir=MODEL_DIR):
        self.model_dir = model_dir
        self.meta = None
        self.lstm = None
        self.xgb = None
        self.w_lstm = 0.85
        self.w_xgb = 0.15
        self.th_block = TH_BLOCK        # load() 会用标定值覆盖
        self.th_confirm = TH_CONFIRM
        self.stats = {}

        self._lock = threading.Lock()
        self._stats_lock = threading.Lock()

        self.counters = {
            "scored": 0, "APPROVE": 0, "CONFIRM": 0, "BLOCK": 0,
            "fraud_seen": 0, "fraud_stopped": 0,      # stopped = CONFIRM or BLOCK
            "guardian_alerts": 0,
            "amount_total": 0.0,           # 处理的总金额
            "amount_blocked": 0.0,         # 被拦截的金额（含正常交易，诚实统计）
            "amount_recovered": 0.0,       # 被拦下的真实欺诈金额
        }
        self.latencies = deque(maxlen=2000)

    # ------------------------------------------------------------------ 加载
    def load(self):
        with open(os.path.join(self.model_dir, "meta.json")) as f:
            self.meta = json.load(f)
        self.w_lstm = float(self.meta["fusion"]["w_lstm"])
        self.w_xgb = float(self.meta["fusion"]["w_xgb"])
        self.stats = self.meta["scaler"]

        # 阈值优先取训练时标定的操作点，env 可覆盖
        op = self.meta.get("operating_point") or {}
        self.th_block = float(os.environ.get("TH_BLOCK", op.get("block", TH_BLOCK)))
        self.th_confirm = float(os.environ.get("TH_CONFIRM", op.get("confirm", TH_CONFIRM)))

        from tensorflow import keras
        self.lstm = keras.models.load_model(
            os.path.join(self.model_dir, "lstm_fraud.keras"), compile=False)

        import xgboost as xgb
        self.xgb = xgb.XGBClassifier()
        self.xgb.load_model(os.path.join(self.model_dir, "xgb_fraud.json"))

        n_feat = len(self.meta["seq_feats"])
        self.lstm.predict(np.zeros((1, self.meta["timesteps"], n_feat), dtype=np.float32),
                          verbose=0)
        return self

    # ------------------------------------------------------------------ 缩放
    def _scale(self, arr, name):
        # ⚠️ 关键：必须先把 NaN/inf 归零，否则 Telum NNPA 会抛
        #    ZDNN_ELEMENT_RANGE_VIOLATION 并使整次推理失败。
        arr = np.nan_to_num(np.asarray(arr, dtype=np.float32),
                            nan=0.0, posinf=0.0, neginf=0.0)
        mu = np.asarray(self.stats[name]["mean"], dtype=np.float32)
        sd = np.asarray(self.stats[name]["std"], dtype=np.float32)
        sd = np.where(sd < 1e-6, 1.0, sd)
        return np.clip((arr - mu) / sd, -6.0, 6.0).astype(np.float32)

    # ------------------------------------------------------------------ 理由码
    @staticmethod
    def _reason_codes(tab_raw, p_lstm, p_xgb):
        """从原始（未缩放）表格特征推导可解释理由码"""
        codes = []
        hour = float(tab_raw[1])
        has_error = float(tab_raw[6])
        amount_z = float(tab_raw[7])
        win_n = float(tab_raw[10])
        amt_ratio = float(tab_raw[11])
        gap_min = float(np.expm1(tab_raw[12]))
        mcc_freq = float(tab_raw[13])
        is_online = float(tab_raw[4])

        if amount_z >= 2.0:
            codes.append("R01")
        if win_n >= 6 and gap_min <= 10:
            codes.append("R02")
        if hour <= 5 or hour >= 23:
            codes.append("R03")
        if is_online >= 1:
            codes.append("R04")
        if has_error >= 1:
            codes.append("R05")
        if mcc_freq < 0.001:
            codes.append("R06")
        if p_lstm >= 0.5:
            codes.append("R07")
        if p_xgb >= 0.5:
            codes.append("R08")
        if amt_ratio >= 3.0:
            codes.append("R09")
        return codes

    # ------------------------------------------------------------------ 打分
    def score(self, txn, seq_raw, tab_raw):
        """txn: 含 user/card/amount/hour/channel 等元数据；返回完整决策对象"""
        seq = self._scale(np.asarray(seq_raw, dtype=np.float32)[None, ...], "seq")
        tab = self._scale(np.asarray(tab_raw, dtype=np.float32)[None, ...], "tab")

        t0 = time.perf_counter()
        # 直接调用而非 predict()：单样本推理快约 2 倍，且避免 TF data-pipeline 的批处理抖动
        try:
            p_lstm = float(np.asarray(self.lstm(seq, training=False)).ravel()[0])
        except Exception:
            p_lstm = float(self.lstm.predict(seq, verbose=0).ravel()[0])
        p_xgb = float(self.xgb.predict_proba(tab)[:, 1][0])
        risk = self.w_lstm * p_lstm + self.w_xgb * p_xgb
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        # 双保险：任何异常数值都退化为中性分，绝不让服务中断
        if not np.isfinite(risk):
            risk = 0.0
        p_lstm = p_lstm if np.isfinite(p_lstm) else 0.0
        p_xgb = p_xgb if np.isfinite(p_xgb) else 0.0

        if risk >= self.th_block:
            decision = "BLOCK"
        elif risk >= self.th_confirm:
            decision = "CONFIRM"
        else:
            decision = "APPROVE"

        codes = self._reason_codes(tab_raw, p_lstm, p_xgb)
        profile = profile_for(txn["user"], txn["card"])

        # 家属通知：只要交易被暂停（需确认或拦截）、且金额超过守护额度，就通知关联家属
        guardian_notified = (
            decision in ("CONFIRM", "BLOCK")
            and txn["amount"] >= profile["guardian_limit"]
            and profile["protected"]
        )

        is_fraud = txn.get("is_fraud")
        stopped = decision in ("CONFIRM", "BLOCK")

        with self._stats_lock:
            c = self.counters
            c["scored"] += 1
            c[decision] += 1
            c["amount_total"] += txn["amount"]
            if decision == "BLOCK":
                c["amount_blocked"] += txn["amount"]
            if guardian_notified:
                c["guardian_alerts"] += 1
            if is_fraud:
                c["fraud_seen"] += 1
                if stopped:
                    c["fraud_stopped"] += 1
                    c["amount_recovered"] += txn["amount"]
            self.latencies.append(elapsed_ms)

        return {
            "risk": round(risk, 4),
            "p_lstm": round(p_lstm, 4),
            "p_xgb": round(p_xgb, 4),
            "decision": decision,
            "latency_ms": round(elapsed_ms, 2),
            "reason_codes": [{"code": c_, "en": REASONS[c_][0], "zh": REASONS[c_][1]}
                             for c_ in codes],
            "guardian_notified": guardian_notified,
            "guardian_relation": profile["guardian_relation"],
            "guardian_mask": profile["guardian_mask"],
            "guardian_limit": profile["guardian_limit"],
            "age_band": profile["age_band"],
            "protected": profile["protected"],
            "is_fraud": is_fraud,
        }

    # ------------------------------------------------------------------ 统计
    def snapshot(self):
        with self._stats_lock:
            lat = list(self.latencies)
            c = dict(self.counters)

        if lat:
            a = np.asarray(lat)
            lat_stats = {"p50": round(float(np.percentile(a, 50)), 2),
                         "p95": round(float(np.percentile(a, 95)), 2),
                         "p99": round(float(np.percentile(a, 99)), 2),
                         "mean": round(float(a.mean()), 2)}
        else:
            lat_stats = {"p50": 0.0, "p95": 0.0, "p99": 0.0, "mean": 0.0}

        recall = (c["fraud_stopped"] / c["fraud_seen"]) if c["fraud_seen"] else None
        precision_like = (c["fraud_stopped"] / (c["CONFIRM"] + c["BLOCK"])) \
            if (c["CONFIRM"] + c["BLOCK"]) else None

        return {
            "counters": c,
            "latency_ms": lat_stats,
            "thresholds": {"block": self.th_block, "confirm": self.th_confirm},
            "fusion": {"w_lstm": self.w_lstm, "w_xgb": self.w_xgb},
            "fraud_recall_live": round(recall, 3) if recall is not None else None,
            "stop_precision_live": round(precision_like, 3) if precision_like is not None else None,
            "amount_recovered": round(c["amount_recovered"], 2),
        }
