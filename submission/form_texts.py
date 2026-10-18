#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""提交表单 4 段文案 —— 自动校验 ≤1024 字符"""
import json
import os

Q1 = """Older people are the primary target of phone scams, and they authorise the transfer themselves. To the bank the payment looks completely normal: valid credentials, valid device, correct PIN. Nothing looks wrong until the money clears, and by then it is gone.

Banks and families only react afterwards, when recovery rates are very low. The only effective intervention point is the few seconds between the moment the victim is persuaded and the moment the transfer is authorised.

Existing fraud systems are built to detect card fraud after the fact. They are not built for a customer who is being talked into sending money right now, and they have no way to involve the people who could actually stop it: the family.

Real-Time Transfer Scam Guard closes exactly that gap."""

Q2 = """Every transfer is scored inside the authorisation path and returns one of three outcomes: APPROVE, CONFIRM or BLOCK.

The transfer becomes real-time features across three groups: behaviour (amount versus the account's own history, velocity, time of day, channel), relationship (recipient novelty) and context. Two open-source models score it in parallel. A 7-step LSTM sequence model (TensorFlow/Keras) captures behavioural sequences; an XGBoost GBDT captures structured risk. Scores are fused (0.85/0.15) into one risk value, and nine reason codes are derived for auditability.

CONFIRM pauses the transfer, shows the holder a plain-language message, and notifies a linked relative when the amount exceeds their guardian limit. BLOCK holds the transfer and writes an audit record.

Decision and explanation are decoupled: the decision returns in about 22 ms, while IBM Granite (local llama.cpp) generates the explanation asynchronously, so it never blocks authorisation. The service is containerised with Docker."""

Q3 = """The entire solution runs on IBM LinuxONE (s390x), not an x86 port.

Telum on-chip AI: inference for both models and the Granite LLM executes on the same processor, with the on-chip AI accelerator handling matrix operations. The decision path stays near 22 ms even while the LLM generates explanations concurrently, because the accelerator sits on-die rather than behind a GPU bus. That is what makes real-time scoring practical inside an authorisation path.

Pervasive encryption: the platform encrypts data at rest and in transit, with quantum-safe protection. Scam detection must read highly sensitive transfer and identity context, so this is a prerequisite.

Data stays on platform: Granite is served locally by llama.cpp compiled with the zDNN/NNPA backend. No external API calls are made, so no customer data leaves the enterprise perimeter - the condition a bank requires before permitting real-time AI.

Container native: shipped as a Docker image built on IBM's s390x AI/ML base image."""

Q4 = """1. Older adults targeted by phone scams. They act alone during a scam and often cannot stop themselves in time. The system pauses the transfer and offers a plain way to say "I am not sure" instead of losing their savings.

2. Adult children living away from their parents. They cannot watch every transfer. They set a guardian limit and receive an actionable alert when something needs confirmation, turning distant worry into a decision they can make from their phone.

3. Banks and payment providers. Fewer scam losses and complaints, plus a defensible audit record for regulators. Because the engine sits in the authorisation path it cuts loss without slowing genuine payments.

4. Anti-fraud teams and regulators. Every decision carries reason codes, so cases can be reviewed later and the model audited over time.

Measured on a single reproducible pass of 587 transfers: 65.2% fraud recall at 96.7% precision on stopped transfers, recovering $18,418, with a 22 ms median decision."""

FIELDS = [
    ("What is the Problem you are trying to solve?", Q1),
    ("How are you planning to solve the problem? (Brief Overview)", Q2),
    ("How does your solution leverage IBM Z / LinuxONE technologies?", Q3),
    ("What value does your solution deliver, and who will benefit from it?", Q4),
]

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "form-texts.md")
    ok = True
    lines = ["# IBM Z Datathon 2026 — Submission form text", "",
             "Team: **Chinese Can Fly** · Track: **Real-Time AI for Critical Decisions**", ""]
    for i, (label, text) in enumerate(FIELDS, 1):
        n = len(text)
        flag = "OK" if n <= 1024 else "TOO LONG"
        if n > 1024:
            ok = False
        print(f"[{i}] {n:4d}/1024  {flag}   {label}")
        lines += [f"## {i}. {label}", "", f"<!-- {n}/1024 characters -->", "",
                  text, ""]
    what = "Challenges dropdown: select **Real-Time AI for Critical Decisions**."
    lines += ["---", "", what, ""]
    with open(out, "w") as f:
        f.write("\n".join(lines))
    print()
    print(f"{'全部合规' if ok else '有超长字段，需精简'} → 已写入 {out}")
