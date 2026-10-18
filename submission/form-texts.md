# IBM Z Datathon 2026 — Submission form text

Team: **Chinese Can Fly** · Track: **Real-Time AI for Critical Decisions**

## 1. What is the Problem you are trying to solve?

<!-- 626/1024 characters -->

Older people are the main target of phone scams, and they authorise the transfer themselves. To the bank the payment looks normal: the customer authenticated properly, from a device they have used before. Nothing is wrong until the money clears, and by then it is gone.

Banks and families react afterwards, when recovery is unlikely. The intervention point is the few seconds between the victim being persuaded and the transfer being authorised.

Existing fraud systems detect misuse after the fact. They were not built for a customer who is being talked into paying now, and they cannot involve the people who could stop it.

## 2. How are you planning to solve the problem? (Brief Overview)

<!-- 993/1024 characters -->

Every transfer is scored inside the authorisation path and returns APPROVE, CONFIRM or BLOCK.

The transfer becomes real-time features: how the amount compares with the account's own history, how fast transfers follow each other, the hour, the channel, and whether the recipient is new. Two open-source models score in parallel. A 7-step LSTM sequence model (TensorFlow/Keras) reads behavioural sequences; an XGBoost GBDT reads structured risk. Their scores are fused into one risk value at 0.85 and 0.15, and nine reason codes are derived so a decision can be audited.

CONFIRM pauses the transfer, shows the holder a plain-language message, and alerts a linked relative when the amount exceeds their guardian limit. BLOCK holds the transfer and writes an audit record.

The decision returns in about 22 ms. IBM Granite runs on the same machine through llama.cpp and writes the explanation afterwards, so the model never sits in the authorisation path. The service runs as a Docker container.

## 3. How does your solution leverage IBM Z / LinuxONE technologies?

<!-- 791/1024 characters -->

The solution runs on IBM LinuxONE (s390x).

The Telum processor carries an on-chip AI accelerator, and inference for both models and the Granite LLM executes on that processor. Because the accelerator shares the die with the CPU, the decision path stays near 22 ms while the LLM generates explanations at the same time.

The platform encrypts data at rest and in transit, and the protection is quantum-safe. Scam detection has to read transfer and identity context, so this covers the data the system touches.

Granite is served locally by llama.cpp compiled with the zDNN/NNPA backend. The system makes no external API calls, so customer data stays inside the enterprise perimeter.

The service ships as a Docker image built on IBM's s390x AI/ML base image, and it runs with a health check.

## 4. What value does your solution deliver, and who will benefit from it?

<!-- 881/1024 characters -->

1. Older adults targeted by phone scams act alone and often cannot stop in time. The system pauses the transfer and gives them a plain way to say they are unsure, before the money leaves.

2. Adult children living away from their parents cannot watch every transfer. They set a guardian limit and get an alert when a transfer needs confirmation, so they can act from their phone.

3. Banks and payment providers see fewer scam losses and complaints, and keep an audit record for regulators. The engine sits in the authorisation path, so it cuts loss without slowing genuine payments.

4. Anti-fraud teams and regulators get reason codes with every decision, so a case can be reviewed later and the model audited over time.

On a single reproducible pass of 587 transfers: 65.2% fraud recall at 96.7% precision on stopped transfers, recovering $18,418, with a 22 ms median decision.

---

Challenges dropdown: select **Real-Time AI for Critical Decisions**.
