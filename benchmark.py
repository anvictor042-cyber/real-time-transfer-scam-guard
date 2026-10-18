#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reproducible evaluation — produces the numbers quoted in the pitch deck.

Runs the full curated stream once (no looping) through the live engine and
prints recall, precision, latency and the amount recovered, plus the offline
model metrics recorded at training time.

    python3 benchmark.py [--json]
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("MODEL_DIR", os.path.join(HERE, "models"))

from app.engine import RiskEngine          # noqa: E402
from app.stream import StreamBuilder       # noqa: E402


def run():
    eng = RiskEngine(os.environ["MODEL_DIR"]).load()
    stream = StreamBuilder().prepare(profile="demo")

    lat = []
    for ev in stream.events:
        meta = {k: v for k, v in ev.items() if not k.startswith("_")}
        r = eng.score(meta, ev["_seq"], ev["_tab"])
        lat.append(r["latency_ms"])

    snap = eng.snapshot()
    c = snap["counters"]
    a = np.asarray(lat)

    out = {
        "transfers": c["scored"],
        "approve": c["APPROVE"],
        "confirm": c["CONFIRM"],
        "block": c["BLOCK"],
        "fraud_seen": c["fraud_seen"],
        "fraud_stopped": c["fraud_stopped"],
        "recall": snap["fraud_recall_live"],
        "precision_on_stops": snap["stop_precision_live"],
        "guardian_alerts": c["guardian_alerts"],
        "amount_attempted": round(c["amount_total"], 2),
        "amount_recovered": round(c["amount_recovered"], 2),
        "latency_ms": {
            "p50": round(float(np.percentile(a, 50)), 2),
            "p95": round(float(np.percentile(a, 95)), 2),
            "p99": round(float(np.percentile(a, 99)), 2),
        },
        "thresholds": snap["thresholds"],
        "fusion_weights": snap["fusion"],
    }

    with open(os.path.join(os.environ["MODEL_DIR"], "meta.json")) as f:
        meta = json.load(f)
    out["offline_model_quality"] = meta["metrics"]
    return out


if __name__ == "__main__":
    res = run()
    if "--json" in sys.argv:
        print(json.dumps(res, indent=2))
    else:
        print("=" * 62)
        print("  Real-Time Transfer Scam Guard — reproducible evaluation")
        print("=" * 62)
        print(f"  transfers scored      : {res['transfers']}")
        print(f"  approve / confirm / block : {res['approve']} / {res['confirm']} / {res['block']}")
        print(f"  labelled frauds seen  : {res['fraud_seen']}")
        print(f"  frauds stopped        : {res['fraud_stopped']}")
        print(f"  recall                : {res['recall']*100:.1f} %")
        print(f"  precision on stops    : {res['precision_on_stops']*100:.1f} %")
        print(f"  families alerted      : {res['guardian_alerts']}")
        print(f"  amount attempted      : ${res['amount_attempted']:,.2f}")
        print(f"  amount recovered      : ${res['amount_recovered']:,.2f}")
        print(f"  latency p50/p95/p99   : {res['latency_ms']['p50']} / "
              f"{res['latency_ms']['p95']} / {res['latency_ms']['p99']} ms")
        print("-" * 62)
        m = res["offline_model_quality"]
        for k in ("lstm", "xgb", "fusion"):
            if k in m:
                d = m[k]
                print(f"  {k:8s} PR-AUC {d['pr_auc']:.4f}   ROC-AUC {d['roc_auc']:.4f}   "
                      f"best F1 {d['best_f1']:.3f}")
        print("=" * 62)
