#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the decision engine.

Run either way:
    python3 tests/test_engine.py
    pytest tests/test_engine.py
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
os.environ.setdefault("MODEL_DIR", os.path.join(HERE, "models"))

from app.engine import REASONS, TH_BLOCK, TH_CONFIRM, RiskEngine  # noqa: E402
from app.profiles import profile_for                              # noqa: E402

_ENGINE = None


def engine():
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = RiskEngine(os.environ["MODEL_DIR"]).load()
    return _ENGINE


def make_txn(user=1, card=0, amount=100.0, hour=12, fraud=None):
    return {"user": user, "card": card, "amount": amount, "hour": hour,
            "channel": "Online Transaction", "is_fraud": fraud}


def test_engine_loads():
    e = engine()
    assert e.lstm is not None
    assert e.xgb is not None
    assert 0 < e.w_lstm < 1


def test_decision_is_one_of_three():
    e = engine()
    seq = np.zeros((7, 8), dtype=np.float32)
    tab = np.zeros(15, dtype=np.float32)
    r = e.score(make_txn(), seq, tab)
    assert r["decision"] in ("APPROVE", "CONFIRM", "BLOCK")


def test_thresholds_are_ordered():
    assert 0 < TH_CONFIRM < TH_BLOCK < 1


def test_reason_codes_documented_and_emitted():
    e = engine()
    seq = np.zeros((7, 8), dtype=np.float32)
    # night-time, online, high z-score, rapid window -> should fire several codes
    tab = np.zeros(15, dtype=np.float32)
    tab[1] = 2.0     # hour
    tab[4] = 1.0     # online
    tab[7] = 3.5     # amount_z
    tab[10] = 7.0    # window size
    tab[11] = 4.0    # amount ratio
    r = e.score(make_txn(hour=2), seq, tab)
    codes = [c["code"] for c in r["reason_codes"]]
    assert codes, "expected at least one reason code"
    for c in codes:
        assert c in REASONS
    assert "R01" in codes          # amount far above history
    assert "R03" in codes          # unusual hour


def test_guardian_limit_is_respected():
    e = engine()
    seq = np.zeros((7, 8), dtype=np.float32)
    tab = np.zeros(15, dtype=np.float32)
    tab[7] = 4.0
    tab[10] = 7.0
    tab[11] = 5.0

    prof = profile_for(3, 1)
    # a very small amount must not page the family, a large one may
    small = e.score(make_txn(user=3, card=1, amount=max(1.0, prof["guardian_limit"] * 0.1)), seq, tab)
    if small["decision"] == "APPROVE":
        assert small["guardian_notified"] is False

    big = e.score(make_txn(user=3, card=1, amount=prof["guardian_limit"] * 20), seq, tab)
    if big["decision"] in ("CONFIRM", "BLOCK") and prof["protected"]:
        assert big["guardian_notified"] is True


def test_recovered_amount_only_counts_real_fraud():
    e = engine()
    seq = np.zeros((7, 8), dtype=np.float32)
    tab = np.zeros(15, dtype=np.float32)
    tab[7] = 4.0
    e.score(make_txn(amount=500.0, fraud=False), seq, tab)
    before = e.snapshot()["counters"]["amount_recovered"]
    e.score(make_txn(amount=500.0, fraud=False), seq, tab)
    after = e.snapshot()["counters"]["amount_recovered"]
    assert after == before, "non-fraud must never add to the recovered amount"


def _run_standalone():
    names = [n for n in sorted(globals()) if n.startswith("test_")]
    failed = 0
    for n in names:
        try:
            globals()[n]()
            print(f"  PASS  {n}")
        except AssertionError as ex:
            failed += 1
            print(f"  FAIL  {n}  {ex}")
        except Exception as ex:                    # noqa: BLE001
            failed += 1
            print(f"  ERROR {n}  {type(ex).__name__}: {ex}")
    print(f"\n  {len(names) - failed}/{len(names)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(_run_standalone())
