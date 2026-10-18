# 视频脚本 · 纯屏录版（不用 PPT）

**只开两个窗口：仪表盘 + 终端。全程不切到 PDF。**

官方对视频的要求只有三件事：讲清问题、演示方案、讲亮点和影响 —— **不需要幻灯片**。

约 200 词 ≈ **1 分 25 秒**。

---

## 录之前（3 分钟）

页面打开后是**暂停状态**（顶部显示 `paused`，表格空的）。这是故意的 —— 由你决定什么时候开始。

1. 浏览器打开 `http://148.100.76.225:8000`
2. **点绿色的 `▶ Start` 按钮** → 交易开始流入
3. **等 30–40 秒**，让表格填满、顶部计数器有数字、右侧出现解释卡
4. 终端里**先跑一次** `ssh datathon 'uname -m; nproc'`，确认输出 `s390x`
5. 关微信 / 开专注模式
6. `⌘ + Shift + 5` → **截取所选部分** → 框住浏览器 → 麦克风**别选「无」**

> 录的时候**让它继续跑**，不要按暂停。表格一直是满的，画面好看。
>
> 想从零开始重来：点 `reset`（清零并暂停），再点 `▶ Start`。

---

## 逐字稿

### 0:00 – 0:15 · 问题（停在仪表盘）

> Every year, older people are tricked into sending money away.
>
> The bank sees nothing wrong, because the customer is doing it themselves. By the time anyone notices, the money is gone.

### 0:15 – 0:40 · 方案（仍在仪表盘，指着表格）

> Our system scores every transfer before it goes through. It gives one of three answers.
>
> **Approve** — let it go. *(指一行绿色的)*
>
> **Confirm** — pause it, tell the customer in simple words, and alert their family. *(指一行橙色的)*
>
> **Block** — stop it, and save a record. *(指一行红色的)*

### 0:40 – 1:15 · 演示（还是仪表盘）

> This is running live on IBM LinuxONE.
>
> Two models score each transfer. An LSTM reads the last seven transfers. An XGBoost reads the numbers. We combine the scores, and the answer comes back in about 22 milliseconds.
>
> Here is a high-risk one. *(鼠标指右侧新出现的卡片)* Watch the right side.
>
> IBM Granite writes a message the customer can understand, and an alert for the family. It all runs on this machine, so no data leaves the bank.

### 1:15 – 1:35 · 证明是 IBM Z（切到终端）

> This is s390x — a real IBM Z machine. Three cores, and one AI chip on the processor. That is why the decision stays fast.

*(终端里已经显示 `s390x` 和 `3`)*

### 1:35 – 1:50 · 结果（切回仪表盘）

> On the full test set, we catch 65 percent of fraud. And 96 out of 100 transfers we stop are real fraud. That is about 18 thousand dollars recovered.

*(顶部计数器就显示这些数字)*

### 1:50 – 2:00 · 收尾

> For the customer, a few more seconds to change their mind. For the family, an alert they can act on.
>
> Thank you.

---

## 只有一次窗口切换

```
0:00 ─────────────── 1:15  仪表盘
                       ↓  ⌘ + Tab
1:15 ─────────────── 1:35  终端
                       ↓  ⌘ + Tab
1:35 ─────────────── 2:00  仪表盘
```

**全程只切两次。** 比带 PPT 的版本少切四次，出错概率低很多。

---

## 怎么「指」那一行

说到 Approve / Confirm / Block 时，鼠标移到对应颜色的那一行上停 1 秒即可。

**不用点，不用滚** —— 减少动作就减少出错。

如果当时屏幕上没有某一种颜色，就跳过去，别等。脚本里那句照样念。

---

## 上传

YouTube → 可见性 **Unlisted（不公开列出）** → 传完开无痕窗口确认能播。

---

## 最后检查

```
☐ 时长 < 3:00（1:30 左右最舒服）
☐ 地址栏能看到 148.100.76.225:8000
☐ APPROVE / CONFIRM / BLOCK 都出现过
☐ 右侧出现过带家属信息的卡片
☐ 终端显示 s390x
☐ 有声音，无杂音
☐ YouTube 是 Unlisted，无痕能播
```

---

## 现在就去录

**别忘了：Pitch Deck 的 PDF 还是要单独上传到表单第 6 项。**
只是视频里不用出现它。
