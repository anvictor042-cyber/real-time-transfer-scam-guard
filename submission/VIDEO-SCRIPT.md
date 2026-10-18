# 视频脚本 · 纯屏录版（不用 PPT）

**只开两个窗口：仪表盘 + 终端。全程不切到 PDF。**

官方对视频的要求只有三件事：讲清问题、演示方案、讲亮点和影响 —— **不需要幻灯片**。

约 275 词 ≈ **1 分 55 秒**。

---

## 录之前（3 分钟）

页面打开后是**暂停状态**（顶部显示 `paused`，表格空的）。这是故意的 —— 由你决定什么时候开始。

1. 浏览器打开 `http://148.100.76.225:8000`
2. **点绿色的 `▶ Start`** → 交易开始流入
3. **等 30–40 秒**，让表格填满、顶部计数器有数字、右侧出现解释卡
4. **找一行红色的 BLOCK**，等一下要点击它
5. 终端里**先跑一次** `ssh datathon 'uname -m; nproc'`，确认输出 `s390x`
6. 关微信 / 开专注模式
7. `⌘ + Shift + 5` → **截取所选部分** → 框住浏览器 → 麦克风**别选「无」**

> 录的时候**让它继续跑**，不要按暂停。
> 想从零重来：点 `reset` → 再点 `▶ Start`。

---

## 逐字稿

### 0:00 – 0:24 · 问题（停在仪表盘）

> Every year, older people are tricked into sending money away.
>
> In 2024, older Americans reported losing almost five billion dollars. The FBI says the real figure is higher, because many victims never report it.
>
> The bank sees nothing wrong, because the customer is doing it themselves. By the time anyone notices, the money is gone.

### 0:24 – 0:45 · 方案（仍在仪表盘，指着表格）

> Our system scores every transfer before it goes through. It gives one of three answers.
>
> **Approve** — let it go. *(指一行绿色的)*
>
> **Confirm** — pause it, tell the customer in simple words, and alert their family. *(指一行橙色的)*
>
> **Block** — stop it, and save a record. *(指一行红色的)*

### 0:45 – 1:11 · 点开一个案例（**这一段最关键**）

**动作：用鼠标点那一行红色的 BLOCK**

> Let me show you one. *(点击)*
>
> These are the transfers behind that decision. Same account, a few minutes apart, and the amount keeps climbing.
>
> That is what a scam looks like in the data, and it is what the sequence model reads.

> 💡 **不要念死数字。** 卡片上的笔数和金额每次都不同，念错反而暴露是背稿。
>
> 想加一个数字就说你**屏幕上真实看到的那个**，比如：
> "Six transfers in nine minutes. The amount grew forty times." —— 但**先看清屏幕**再念。
>
> 最稳的说法：**"Same account, a few minutes apart, the amount keeps climbing."** 这句永远正确。

### 1:11 – 1:30 · 解释

**动作：鼠标移到右侧解释卡**

> At the same time, IBM Granite writes a message the customer can understand, and a simulated alert for the family. It all runs on this machine, so no data leaves the bank.
>
> The answer comes back in about 22 milliseconds.

### 1:30 – 1:47 · 证明是 IBM Z（切到终端）

**动作：`⌘ + Tab` 切到终端**

> This is s390x, a real IBM Z machine. Three cores, and an AI accelerator built into the processor. That is why the decision stays fast.

*(终端里已经显示 `s390x` 和 `3`)*

### 1:47 – 2:00 · 结果（`⌘ + Tab` 切回仪表盘）

> Across the 587 transfers we replay, we catch 65 percent of fraud. And 96 out of 100 transfers we stop are real fraud. That is about 18 thousand dollars recovered.

*(顶部计数器就显示这些数字)*

### 2:00 – 2:12 · 收尾

> For the customer, a few more seconds to change their mind. For the family, an alert they can act on.
>
> Thank you.

---

## 只有一次窗口切换

```
0:00 ─────────────── 1:30  仪表盘
                       ↓  ⌘ + Tab
1:30 ─────────────── 1:47  终端
                       ↓  ⌘ + Tab
1:47 ─────────────── 2:12  仪表盘
```

---

## 三个关键动作

| 时间 | 动作 | 说明 |
|---|---|---|
| 0:24–0:45 | 鼠标指绿/橙/红三行各停 1 秒 | 不用点 |
| **0:45** | **点红色 BLOCK 那一行** | 展开该账户的交易链 |
| 1:11 | 鼠标移到右侧解释卡 | 停 2 秒 |

> 点开案例后**再点一次同一行可以收起**。如果点错了，再点一下关掉就行。
>
> 如果某一行展开后只显示 1–2 笔：说明那笔是该账户的第一笔。**换一行红的再点**，找个链长的。

---

## 上传

YouTube → 可见性 **Unlisted（不公开列出）** → 传完开无痕窗口确认能播。

---

## 最后检查

```
☐ 时长 < 3:00（2:12 左右最舒服）
☐ 地址栏能看到 148.100.76.225:8000
☐ APPROVE / CONFIRM / BLOCK 都出现过
☐ 点开过案例，能看到 6 笔金额递增的链
☐ 右侧出现过带家属信息的卡片
☐ 终端显示 s390x
☐ 有声音，无杂音
☐ YouTube 是 Unlisted，无痕能播
```

---

## 现在就去录

**别忘了：Pitch Deck 的 PDF 还是要单独上传到表单第 6 项。**
只是视频里不用出现它。
