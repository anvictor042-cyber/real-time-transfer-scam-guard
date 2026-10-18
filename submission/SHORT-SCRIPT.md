# 视频脚本 · 精简版（约 2 分钟）

**目标：2:00 以内。词数少、句子短、都是常用词。念慢也没关系。**

---

## 录之前

1. 打开仪表盘，**等 60 秒**让它填满
2. 关掉微信 / 开专注模式
3. `⌘ + Shift + 5` → 截取所选部分 → 麦克风别选「无」→ 录制

---

## 逐字稿

### 0:00 – 0:15 · 问题
**画面：** 仪表盘（或 Deck 第 1 页）

> Every year, older people are tricked into sending money away.
>
> The bank sees nothing wrong, because the customer is doing it themselves. By the time anyone notices, the money is gone.

### 0:15 – 0:40 · 方案
**画面：** Deck 第 3 页（三档决策）

> Our system scores every transfer before it goes through. It gives one of three answers.
>
> **Approve** — let it go.
> **Confirm** — pause it, tell the customer in simple words, and alert their family.
> **Block** — stop it, and save a record.

### 0:40 – 1:20 · 演示
**画面：** 切回仪表盘（已在跑）

> This is running live on IBM LinuxONE.
>
> Two models score each transfer. An LSTM reads the last seven transfers. An XGBoost reads the numbers. We combine the scores, and the answer comes back in about 22 milliseconds.
>
> Here is a high-risk one. *(鼠标指向右侧)* Watch the right side.
>
> IBM Granite writes a message the customer can understand, and an alert for the family. It all runs on this machine, so no data leaves the bank.

### 1:20 – 1:35 · 证明是 IBM Z
**画面：** 切到终端，跑 `ssh datathon 'uname -m; nproc'`

> This is s390x — a real IBM Z machine. Three cores, and one AI chip on the processor.

### 1:35 – 1:50 · 结果
**画面：** Deck 第 7 页（指标）

> On the full test set, we catch 65 percent of fraud. And 96 out of 100 transfers we stop are real fraud. That is about 18 thousand dollars recovered.

### 1:50 – 2:00 · 收尾
**画面：** 回仪表盘

> For the customer, a few more seconds to change their mind. For the family, an alert they can act on.
>
> Thank you.

---

## 拍摄提示

| 事项 | 说明 |
|---|---|
| **语速** | 慢一点没关系，宁可 2:00 也别赶 |
| **卡词** | 直接重录，别剪 |
| **鼠标** | 讲 "Watch the right side" 时指一下右侧卡片 |
| **终端** | 提前开好窗口，只跑那一条命令 |
| **数字** | 22 毫秒 / 65% / 96% / 1.8 万美元 |

## 上传

YouTube → 可见性选 **Unlisted（不公开列出）** → 上传完用无痕窗口打开确认能播。

---

## 如果还是超时

删掉这几句，不影响完整性：

- "and save a record"
- "It all runs on this machine, so no data leaves the bank."
- 收尾第一句

---

## 最后检查

```
☐ 时长 < 3:00
☐ 地址栏能看到 148.100.76.225:8000
☐ APPROVE / CONFIRM / BLOCK 都出现过
☐ 终端显示 s390x
☐ 有声音
☐ YouTube 是 Unlisted，无痕能播
```
