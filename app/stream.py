#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real-Time Transfer Scam Guard — 交易流模拟器

从历史数据里抽取「欺诈 + 前文上下文」的连续片段，按时间顺序回放，
模拟真实转账流的到达过程。
"""
import numpy as np
import pandas as pd

from . import features as F



class StreamBuilder:
    def __init__(self, csv_path=None):
        self.csv_path = csv_path or F.resolve_csv()
        self.events = []

    def prepare(self, profile="demo"):
        df = F.load_and_engineer(self.csv_path)

        # 每张卡内的有序行号：既用于取窗口前文，也用于反查
        cards = {}
        for key, idx in df.groupby(["User", "Card"]).indices.items():
            cards[key] = np.sort(np.asarray(idx))
        row2card = {int(r): (k, pos)
                    for k, arr in cards.items()
                    for pos, r in enumerate(arr)}

        fraud = np.where(df["is_fraud"].to_numpy() == 1)[0]
        context = 12
        if profile == "demo":
            fraud = fraud[::5]          # 抽样约 1/5，让流更短更密
            context = 12
        else:
            context = 20

        keep = set()
        for fi in fraud:
            key, pos = row2card[int(fi)]
            arr = cards[key]
            keep.update(int(x) for x in arr[max(0, pos - context):pos + 1])

        sel = np.array(sorted(keep))
        sel = sel[np.argsort(df.iloc[sel]["ts"].to_numpy())]     # 严格按时间回放
        self.events = [self._event(df, int(r), row2card, cards) for r in sel]
        return self

    @staticmethod
    def _event(df, row_idx, row2card, cards):
        row = df.iloc[row_idx]
        key, pos = row2card[row_idx]
        arr = cards[key]
        win_idx = arr[max(0, pos - F.TIMESTEPS + 1):pos + 1]

        seq = df.iloc[win_idx][F.SEQ_FEATS].to_numpy(dtype=np.float32)
        if len(seq) < F.TIMESTEPS:                      # 冷启动用首笔填充
            seq = np.vstack([np.repeat(seq[:1], F.TIMESTEPS - len(seq), axis=0), seq])

        w_amt = df.iloc[win_idx]["log_amount"].to_numpy(dtype=np.float32)
        merchants = df.iloc[win_idx]["Merchant Name"].astype(str).to_numpy()

        tab = np.asarray([
            row["log_amount"], row["hour"], row["dow"], row["is_chip"],
            row["is_online"], row["is_swipe"], row["has_error"], row["amount_z"],
            float(w_amt.mean()), float(w_amt.std()), float(len(w_amt)),
            float(np.expm1(row["log_amount"]) / max(np.expm1(w_amt.mean()), 1e-6)),
            float(row["gap_prev_seconds"]), float(row["mcc_freq"]),
            float(len(np.unique(merchants))),
        ], dtype=np.float32)

        channel = ("Chip Transaction" if row["is_chip"]
                   else "Online Transaction" if row["is_online"]
                   else "Swipe Transaction")

        return {
            "user": int(row["User"]),
            "card": int(row["Card"]),
            "ts": int(row["ts"]),
            "date": f"{int(row['Year'])}-{int(row['Month']):02d}-{int(row['Day']):02d}",
            "hour": int(row["hour"]),
            "minute": int(row["minute"]),
            "amount": round(float(row["Amount"]), 2),
            "channel": channel,
            "merchant": str(row["Merchant Name"]),
            "state": str(row["Merchant State"]) if pd.notna(row["Merchant State"]) else "",
            "error": str(row["Errors?"]) if pd.notna(row["Errors?"]) else "",
            "amount_z": round(float(row["amount_z"]), 2),
            "win_txn": int(len(w_amt)),
            "gap_min": round(float(np.expm1(row["gap_prev_seconds"])), 1),
            "is_fraud": bool(row["is_fraud"]),
            "_seq": seq.tolist(),
            "_tab": tab.tolist(),
        }

    def __len__(self):
        return len(self.events)
