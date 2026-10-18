#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""提交表单 4 段文案 —— 自动校验 ≤1024 字符"""
import json
import os

Q1 = """Older people are the main target of phone scams, and they authorise the transfer themselves. In 2024 the FBI's IC3 logged 147,127 elder-fraud complaints reporting $4.885 billion in losses, 43% more than 2023, and the FBI notes that reporting is incomplete because victims are embarrassed or do not know they were scammed. To the bank the payment looks normal: the customer authenticated properly, from a device they have used before. Nothing is wrong until the money clears, and by then it is gone. Banks and families react afterwards, when recovery is unlikely. The intervention point is the few seconds between the victim being persuaded and the transfer being authorised. Existing fraud systems detect misuse after the fact. They were not built for a customer who is being talked into paying now, and they cannot involve the people who could stop it."""

Q2 = """Every transfer is scored inside the authorisation path and returns APPROVE, CONFIRM or BLOCK. The transfer becomes real-time features: how the amount compares with the account's own history, how fast transfers follow each other, the hour, the channel, and whether the recipient is new. Two open-source models score in parallel. A 7-step LSTM sequence model (TensorFlow/Keras) reads behavioural sequences; an XGBoost GBDT reads structured risk. Their scores are fused into one risk value at 0.85 and 0.15, and nine reason codes are derived so a decision can be audited. CONFIRM pauses the transfer, shows the holder a plain-language message, and alerts a linked relative when the amount exceeds their guardian limit. BLOCK holds the transfer and writes an audit record. The decision returns in about 22 ms. IBM Granite runs on the same machine through llama.cpp and writes the explanation afterwards, so the model never sits in the authorisation path. The service runs as a Docker container."""

Q3 = """The solution runs on IBM LinuxONE (s390x). The Telum processor carries an on-chip AI accelerator, and inference for both models and the Granite LLM executes on that processor. Because the accelerator shares the die with the CPU, the decision path stays near 22 ms while the LLM generates explanations at the same time. The platform encrypts data at rest and in transit, and the protection is quantum-safe. Scam detection has to read transfer and identity context, so this covers the data the system touches. Granite is served locally by llama.cpp compiled with the zDNN/NNPA backend. The system makes no external API calls, so customer data stays inside the enterprise perimeter. The service ships as a Docker image built on IBM's s390x AI/ML base image, and it runs with a health check."""

Q4 = """1. Older adults targeted by phone scams act alone and often cannot stop in time. The system pauses the transfer and gives them a plain way to say they are unsure, before the money leaves. 2. Adult children living away from their parents cannot watch every transfer. They set a guardian limit and get an alert when a transfer needs confirmation, so they can act from their phone. 3. Banks and payment providers see fewer scam losses and complaints, and keep an audit record for regulators. The engine sits in the authorisation path, so it cuts loss without slowing genuine payments. 4. Anti-fraud teams and regulators get reason codes with every decision, so a case can be reviewed later and the model audited over time. On a single reproducible pass of 587 transfers: 65.2% fraud recall at 96.7% precision on stopped transfers, recovering $18,418, with a 22 ms median decision."""

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
