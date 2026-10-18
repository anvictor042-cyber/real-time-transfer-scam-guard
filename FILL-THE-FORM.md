# 提交表填写指南 — IBM Z Datathon 2026

**队名**：Chinese Can Fly　**赛道**：Real-Time AI for Critical Decisions
**仓库**：https://github.com/anvictor042-cyber/real-time-transfer-scam-guard

> 每一格都写了填什么。4 段文案直接整段复制，**不要改动、不要加空行**（都已卡在 1024 字符内）。

---

## 第 1 格 · Challenges（下拉框）

```
Real-Time AI for Critical Decisions
```

---

## 第 2 格 · What is the Problem you are trying to solve?

复制下面**整段**（626 字符）：

```
Older people are the main target of phone scams, and they authorise the transfer themselves. To the bank the payment looks normal: the customer authenticated properly, from a device they have used before. Nothing is wrong until the money clears, and by then it is gone.

Banks and families react afterwards, when recovery is unlikely. The intervention point is the few seconds between the victim being persuaded and the transfer being authorised.

Existing fraud systems detect misuse after the fact. They were not built for a customer who is being talked into paying now, and they cannot involve the people who could stop it.
```

---

## 第 3 格 · How are you planning to solve the problem? (Brief Overview)

复制下面**整段**（993 字符）：

```
Every transfer is scored inside the authorisation path and returns APPROVE, CONFIRM or BLOCK.

The transfer becomes real-time features: how the amount compares with the account's own history, how fast transfers follow each other, the hour, the channel, and whether the recipient is new. Two open-source models score in parallel. A 7-step LSTM sequence model (TensorFlow/Keras) reads behavioural sequences; an XGBoost GBDT reads structured risk. Their scores are fused into one risk value at 0.85 and 0.15, and nine reason codes are derived so a decision can be audited.

CONFIRM pauses the transfer, shows the holder a plain-language message, and alerts a linked relative when the amount exceeds their guardian limit. BLOCK holds the transfer and writes an audit record.

The decision returns in about 22 ms. IBM Granite runs on the same machine through llama.cpp and writes the explanation afterwards, so the model never sits in the authorisation path. The service runs as a Docker container.
```

---

## 第 4 格 · How does your solution leverage IBM Z / LinuxONE technologies?

复制下面**整段**（791 字符）：

```
The solution runs on IBM LinuxONE (s390x).

The Telum processor carries an on-chip AI accelerator, and inference for both models and the Granite LLM executes on that processor. Because the accelerator shares the die with the CPU, the decision path stays near 22 ms while the LLM generates explanations at the same time.

The platform encrypts data at rest and in transit, and the protection is quantum-safe. Scam detection has to read transfer and identity context, so this covers the data the system touches.

Granite is served locally by llama.cpp compiled with the zDNN/NNPA backend. The system makes no external API calls, so customer data stays inside the enterprise perimeter.

The service ships as a Docker image built on IBM's s390x AI/ML base image, and it runs with a health check.
```

---

## 第 5 格 · What value does your solution deliver, and who will benefit from it?

复制下面**整段**（881 字符）：

```
1. Older adults targeted by phone scams act alone and often cannot stop in time. The system pauses the transfer and gives them a plain way to say they are unsure, before the money leaves.

2. Adult children living away from their parents cannot watch every transfer. They set a guardian limit and get an alert when a transfer needs confirmation, so they can act from their phone.

3. Banks and payment providers see fewer scam losses and complaints, and keep an audit record for regulators. The engine sits in the authorisation path, so it cuts loss without slowing genuine payments.

4. Anti-fraud teams and regulators get reason codes with every decision, so a case can be reviewed later and the model audited over time.

On a single reproducible pass of 587 transfers: 65.2% fraud recall at 96.7% precision on stopped transfers, recovering $18,418, with a 22 ms median decision.
```

---

## 第 6 格 · Upload your pitch deck in PDF Format

上传 `submission/pitch-deck.pdf`（9 页，720 KB，上限 5 MB）。

---

## 第 7 格 · Github Link of your Project *

```
https://github.com/anvictor042-cyber/real-time-transfer-scam-guard
```

> 必须以 `https://` 开头。仓库已是 **Public**。

---

## 第 8 格 · Video Submission Link *

```
https://www.youtube.com/watch?v=XXXXXXXXXXX
```

旁白 370 词 ≈ **2 分 33 秒**（上限 3 分钟）。可见性选 **Unlisted**。

---

## 第 9 格 · Share the link to your pitch deck（可选）

**留空** —— 第 6 格已上传文件。

---

## 第 10 格 · Link to all open-source resources used *

```
https://github.com/anvictor042-cyber/real-time-transfer-scam-guard/blob/main/OPENSOURCE.md
```

---

## 第 11 格 · Any other document（可选，建议填）

```
https://github.com/anvictor042-cyber/real-time-transfer-scam-guard/blob/main/submission/architecture.png
```

---

## 点 Submit 之后

1. 页面提示成功
2. **查邮箱**，应收到 `submission ... received` 邮件
3. **截图存档**
4. 回 Submission 页面确认状态

---

## 提交前最后检查

```
☐ Challenges 已选 Real-Time AI for Critical Decisions
☐ 4 段文案都粘进去，页面没报超字数
☐ PDF 上传成功，能看到文件名
☐ GitHub 链接无痕窗口能打开，能看到 README 与截图
☐ 视频链接无痕窗口能播放，时长 < 3:00
☐ 开源资源链接能打开
☐ 架构图链接能打开
☐ 点了 Submit
☐ 收到确认邮件（截图）
```
