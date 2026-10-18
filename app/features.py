#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real-Time Fraud Shield — 统一特征管线
训练与推理共用同一套逻辑，保证 train/serve 一致性。
"""
import os

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def resolve_csv():
    """找到交易语料。依次尝试：环境变量 → IBM 实验镜像内置 → 仓库 data/ 目录。

    换机器时只需设 TRANSACTIONS_CSV，不用改代码。
    """
    candidates = [
        os.environ.get("TRANSACTIONS_CSV"),
        "/home/ibm-user/transactions_history.csv",          # IBM LinuxONE AI/ML 镜像
        os.path.join(ROOT, "data", "transactions_history.csv"),
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    raise FileNotFoundError(
        "transactions_history.csv not found. Set TRANSACTIONS_CSV=/path/to/transactions_history.csv")


def resolve_models():
    """模型目录：环境变量 → 容器内 /app/models → 仓库 models/。"""
    for c in (os.environ.get("MODEL_DIR"),
              "/app/models" if os.path.isdir("/app/models") else None,
              os.path.join(ROOT, "models")):
        if c and os.path.isdir(c):
            return c
    return os.path.join(ROOT, "models")

TIMESTEPS = 7
SEQ_FEATS = ["log_amount", "hour_sin", "hour_cos", "dow",
             "is_chip", "is_online", "has_error", "amount_z"]
TAB_FEATS = ["log_amount", "hour", "dow", "is_chip", "is_online", "is_swipe", "has_error",
             "amount_z", "win_mean_log_amount", "win_std_log_amount", "win_n_txn",
             "win_amt_ratio", "gap_prev_seconds", "mcc_freq", "win_unique_merchants"]


def load_and_engineer(csv_path):
    """读原始 CSV 并完成全部特征工程（与训练脚本一致）"""
    df = pd.read_csv(csv_path)

    df["Amount"] = df["Amount"].astype(str).str.replace(r"[\$,]", "", regex=True).astype(float)
    df["is_fraud"] = (df["Is Fraud?"] == "Yes").astype(int)
    df["is_chip"] = (df["Use Chip"] == "Chip Transaction").astype(int)
    df["is_online"] = (df["Use Chip"] == "Online Transaction").astype(int)
    df["is_swipe"] = (df["Use Chip"] == "Swipe Transaction").astype(int)
    df["has_error"] = df["Errors?"].notna().astype(int)

    tm = df["Time"].astype(str).str.split(":", expand=True)
    df["hour"] = tm[0].astype(int)
    df["minute"] = tm[1].astype(int)
    df["dow"] = pd.to_datetime(
        dict(year=df["Year"], month=df["Month"], day=df["Day"]), errors="coerce"
    ).dt.dayofweek.fillna(0).astype(int)

    df["ts"] = (pd.to_datetime(
        dict(year=df["Year"], month=df["Month"], day=df["Day"],
             hour=df["hour"], minute=df["minute"]), errors="coerce"
    ).astype("int64") // 10**9).fillna(0).astype("int64")

    # 金额可能为负（退款/冲正），log1p 会产生 NaN 并导致 NNPA 越界，先下限截断
    df["log_amount"] = np.log1p(df["Amount"].clip(lower=0))
    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)

    df = df.sort_values(["User", "Card", "ts"]).reset_index(drop=True)
    g = df.groupby(["User", "Card"])["log_amount"]
    df["card_mean"] = g.transform(lambda s: s.expanding().mean())
    df["card_std"] = g.transform(lambda s: s.expanding().std()).fillna(0)
    safe_std = df["card_std"].replace(0, np.nan).clip(lower=0.05)
    df["amount_z"] = ((df["log_amount"] - df["card_mean"]) / safe_std).fillna(0).clip(-8, 8)

    raw_gap = df.groupby(["User", "Card"])["ts"].diff().fillna(0).clip(0, 86400 * 7)
    df["gap_prev_seconds"] = np.log1p(raw_gap / 60.0)

    mcc_counts = df["MCC"].value_counts()
    df["mcc_freq"] = df["MCC"].map(mcc_counts).fillna(0) / len(df)

    return df


def build_windows(df):
    """为每笔交易构造 (seq[TIMESTEPS, F], tab[F2]) 原始特征"""
    seqs = np.zeros((len(df), TIMESTEPS, len(SEQ_FEATS)), dtype=np.float32)
    tabs = np.zeros((len(df), len(TAB_FEATS)), dtype=np.float32)

    for (user, card), idx in df.groupby(["User", "Card"]).indices.items():
        idx = np.sort(np.asarray(idx))
        sub = df.iloc[idx]
        seq_arr = sub[SEQ_FEATS].to_numpy(dtype=np.float32)
        amt = sub["log_amount"].to_numpy(dtype=np.float32)
        merchants = sub["Merchant Name"].astype(str).to_numpy()
        n = len(idx)

        for i in range(n):
            lo = max(0, i - TIMESTEPS + 1)
            win = seq_arr[lo:i + 1]
            if len(win) < TIMESTEPS:                     # 冷启动：用首笔填充
                pad = np.repeat(win[:1], TIMESTEPS - len(win), axis=0)
                win = np.vstack([pad, win])
            seqs[idx[i]] = win

            w_amt = amt[lo:i + 1]
            row = sub.iloc[i]
            tabs[idx[i]] = [
                row["log_amount"], row["hour"], row["dow"], row["is_chip"],
                row["is_online"], row["is_swipe"], row["has_error"], row["amount_z"],
                float(w_amt.mean()), float(w_amt.std()), float(len(w_amt)),
                float(np.expm1(row["log_amount"]) / max(np.expm1(w_amt.mean()), 1e-6)),
                float(row["gap_prev_seconds"]), float(row["mcc_freq"]),
                float(len(np.unique(merchants[lo:i + 1]))),
            ]
    return seqs, tabs
