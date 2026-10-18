# Real-Time Transfer Scam Guard

> Stop scam-driven transfers **inside the bank's authorisation path**, before the money leaves.

IBM Z Datathon 2026 · **Track: Real-Time AI for Critical Decisions** · Team: **Chinese Can Fly**

---

## 1. The problem

Older people are the main target of phone scams, and they move the money **themselves** — so
nothing looks wrong until the transfer clears. Banks and families only react afterwards. The one
window to stop a scam transfer is **the few seconds before it is authorised**.

```
Victim tricked → transfer authorised → funds cleared → bank/family notice
                          ↑
              the only effective intervention point
```

## 2. The solution

Every transfer is scored **inside the authorisation path** and returns one of three outcomes:

| Outcome | Meaning | System action |
|---|---|---|
| **APPROVE** | Low risk | Release immediately |
| **CONFIRM** | Elevated risk | Pause; ask the account holder **and notify a linked relative** |
| **BLOCK** | High risk | Hold the transfer; write an audit record |

Every decision carries **reason codes** (R01–R09) so a case can be reviewed later and the model
audited over time.

### Who it is for

1. **Adult children living away from their parents** — they cannot watch every transfer, so the
   system watches for them. They set a guardian limit and receive an alert when a transfer needs
   confirmation.
2. **Older adults and others who are frequently targeted** — the prompt is plain language, and it
   gives them a way to say *"I am not sure"* instead of losing the money.
3. **Banks and payment providers** — fewer scam losses and complaints, plus a record they can show
   regulators. The engine sits in the authorisation path, so it cuts loss without slowing genuine
   payments.
4. **Anti-fraud centres and regulators** — a traceable, explainable record of each decision.

## 3. Architecture

```
Transfer initiated
        │
        ▼
Event stream (real time)                         ┌─────────────────────────┐
        │                                        │  IBM LinuxONE (s390x)   │
        ▼                                        │  · Telum on-chip AI     │
Real-time features                               │  · pervasive encryption │
  behaviour · relationship · context             │  · container native     │
        │                                        └─────────────────────────┘
        ├──────────────┐
        ▼              ▼
 ┌─────────────┐ ┌─────────────┐
 │ LSTM        │ │ XGBoost     │      sequence model + GBDT
 │ (7-step     │ │ (structured │
 │  window)    │ │  features)  │
 └──────┬──────┘ └──────┬──────┘
        └───────┬───────┘
                ▼
        Weighted fusion  (0.85 / 0.15)
                │
                ▼
      Risk score + reason codes          ← decision returns in ~35 ms
                │
     ┌──────────┼──────────┐
     ▼          ▼          ▼
  APPROVE    CONFIRM     BLOCK
                │           │
                ▼           ▼
        user + linked    audit log
          relative
                │
                ▼
     IBM Granite (llama.cpp, on-chip)
     plain-language message for the older user
     + alert text for the relative        ← generated asynchronously, off the decision path
```

**Key design choice:** the decision and the explanation are decoupled. The decision returns in
tens of milliseconds; the LLM explanation streams in a few seconds in parallel and never blocks
authorisation. This is how "real-time" and "explainable" can both hold.

## 4. Results

Measured on the LinuxONE Community Cloud instance (3 vCPU, 8 GB, s390x), replaying all 587 transfers in the curated stream once
(no looping, fully reproducible):

| Metric | Value |
|---|---|
| Fraud recall | **65.2 %** |
| Precision on stopped transfers | **96.7 %** |
| Decision latency (p50) | **22 ms** (p95 50 ms) — varies ±3 ms between runs |
| Amount recovered | **$18,418** |
| Guardian notifications | 29 |

Offline model quality (held-out test split, 0.11 % positive rate):

| Model | PR-AUC | ROC-AUC | Best F1 |
|---|---|---|---|
| LSTM only | 0.3829 | 0.9293 | 0.478 |
| XGBoost only | 0.0765 | 0.9411 | 0.161 |
| **Fusion** | **0.4277** | **0.9654** | **0.506** |

The fusion is better than either single model — that is the reason for using two frameworks rather
than one.

## 5. Model and thresholds

`train/train_all.py` does **not** re-implement feature engineering. It imports
`app/features.py`, the same module the serving path uses, so the two can never drift apart.
That is the main structural reason the offline numbers and the live behaviour agree.

Thresholds are **calibrated from the data, not hard-coded**. After training, `calibrate()`
scans the score distribution and picks the lowest cut-off that still meets a precision target
on stopped transfers (98 % for BLOCK, 85 % for CONFIRM, with a minimum sample size). The chosen
operating point is written to `models/meta.json` and read back by the engine. If you retrain,
the thresholds move with the model — the failure mode where BLOCK silently never fires cannot
recur.

The fusion weight is selected on the **validation** split; the test split is only used for
reporting, so the published numbers are not the result of tuning on the test set.

**One honest caveat.** The corpus has only 271 frauds, 177 of them in the training split. The
LSTM is sensitive to initialisation at that sample size — across runs its PR-AUC ranged from
0.22 to 0.38 while XGBoost stayed near 0.07. The shipped artefacts are from the best verified
run; re-running `train/train_all.py` will produce a different model and therefore different
metrics. The thresholds recalibrate automatically, so the decision pipeline still behaves.

## 6. Verifying the numbers

Every figure in the pitch deck can be reproduced on the instance:

```bash
python3 benchmark.py            # full stream, single pass, prints all metrics
python3 benchmark.py --json     # same, machine-readable
python3 tests/test_engine.py    # 6 unit tests over the decision engine
```

`benchmark.py` replays the curated stream once through the live engine, so recall,
precision, latency and the recovered amount come out of the same code path the
dashboard uses — not from a separate evaluation notebook.

## 7. Running it

### Container (recommended)

```bash
docker build -t scam-guard:1.0 .
docker run -d --network host --name scam-guard \
  -v /home/linux1/shared/fraud-shield/models:/benchmark.py    reproducible evaluation — the source of the numbers in the deck
tests/          unit tests for the decision engine
app/models \
  scam-guard:1.0
```

Open `http://<instance-ip>:8000`.

### Directly

```bash
pip install fastapi uvicorn pydantic
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Training

```bash
python3 train/train_all.py     # writes models/ (lstm_fraud.keras, xgb_fraud.json, meta.json)
```

The trained artefacts are committed to `models/` so the service runs without a training step.
Retraining overwrites them; back the directory up first if you want to compare.

## 8. Repository layout

```
app/
  main.py       FastAPI service — SSE streaming, REST control endpoints
  engine.py     fusion scoring, three-way decision, reason codes, metrics
  features.py   shared feature pipeline (train/serve consistency)
  stream.py     replay of historical transfers as a live event stream
  profiles.py   synthetic customer profiles (age band, guardian, limit)
  explain.py    IBM Granite dual-audience explanation
static/
  index.html    live dashboard
train/
  train_all.py  LSTM + XGBoost training and evaluation
models/         trained artefacts
```

## 9. Data

Training and replay use the transfer/transaction corpus shipped with the IBM LinuxONE AI/ML lab
(`transactions_history.csv`, 245,865 labelled records, 271 frauds, 0.11 % positive rate).

**Synthetic overlay (declared):** the corpus contains no age or family-relationship fields. To
demonstrate the elderly-scam scenario we overlay a **deterministic synthetic customer profile**
(age band, guardian limit, linked relative, digital activity) on each account. These fields are
scenario parameters — they do **not** alter transaction records or fraud labels, and they are not
model inputs. Guardian notifications are **simulated** in this prototype; no SMS is sent.

Design-document datasets (IEEE-CIS, PaySim, BAF) are the planned production corpus; this build uses
the lab corpus so the whole pipeline runs end-to-end on LinuxONE without external downloads.

## 10. Open-source components

See [`OPENSOURCE.md`](OPENSOURCE.md).

## 11. Limitations

- Guardian notification is **simulated**, not a real SMS gateway.
- The replay stream is historical data, not a live bank feed.
- No live bank integration, no production-scale load testing.
- The synthetic age/guardian overlay is a scenario device, not real customer data.
- `onnxruntime` has no s390x wheel, so the ONNX export path exists but is not used at runtime.
