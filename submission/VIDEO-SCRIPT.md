# 视频脚本 · 单窗口版（不切终端，不用 PPT）

**全程只录浏览器一个窗口。不切应用，不切窗口。**

s390x 的证据在浏览器顶部 —— 写着 `IBM LinuxONE · s390x · Telum`，一直可见。

约 237 词 ≈ **1 分 38 秒**，排程 2:07，留 29 秒余量。

---

## 录之前（5 分钟）

页面打开时是**暂停**的（顶部 `paused`，表格空的）。这是故意的 —— 由你决定什么时候开始。

**`▶ Start` 由你自己在开录后点**，这是演示的一部分 —— 评委能看到数据开始流进来。

| 步 | 操作 |
|---|---|
| 1 | 打开 `http://148.100.76.225:8000`（显示 `paused`，表格空的，**这是对的**）|
| 2 | 关微信 / 打开专注模式 |
| 3 | `⌘ + Shift + 5` → **录制所选部分** |
| 4 | 点 **「选项」** → **麦克风选「iMac麦克风」** ← 不选就是哑的 |
| 5 | 框住浏览器窗口 → 点「录制」 |
| 6 | 3 秒倒计时结束，**点一下绿色的 `▶ Start`**，然后开始念 |

> 点完 Start 后别停，让它一直跑。第 24 秒时已经有 100 多笔，表格是满的。

---

## 逐字稿

### 0:00 – 0:24 · 问题

**画面：** 仪表盘（此时表格是空的）

**动作：** 倒计时一结束，**点一下绿色 `▶ Start`**，然后立刻开始念

> 前 5 秒表格只有几行，这是正常的 —— 正好说明它是实时的。
> 念到"By the time anyone notices"时表格已经满了。

> In 2024, older Americans reported losing almost five billion dollars. The FBI says the real figure is higher, because many victims never report it.
>
> The bank sees nothing wrong, because the customer is doing it themselves. By the time anyone notices, the money is gone.

---

### 0:24 – 0:45 · 方案

**动作：** 鼠标依次指三行，每行停 1 秒。**只移动，不点击。**

| 指哪行 | 说 |
|---|---|
| 🟢 绿色 | **Approve** — let it go. |
| 🟠 橙色 | **Confirm** — pause it, tell the customer in simple words, and alert their family. |
| 🔴 红色 | **Block** — stop it, and save a record. |

---

### 0:45 – 1:11 · 点开案例（**最重要**）

**动作：用鼠标点一下那行红色的 BLOCK**

点对了会在那一行下面展开一张卡，显示同账户之前几笔交易，金额一笔比一笔大。

> Let me show you one. *(点击)*
>
> These are the transfers behind that decision. Same account, a few minutes apart, and the amount keeps climbing.
>
> That is what a scam looks like in the data, and it is what the sequence model reads.

> ⚠️ **不要念死数字。** 每次点开的笔数和金额都不同，念错就露馅。
>
> 想加数字就念屏幕上真实看到的那个。最稳就是上面那句，永远正确。

**出错了：**

| 情况 | 处理 |
|---|---|
| 只展开 1–2 笔 | 再点一次收起，换一行红的 |
| 点错行 | 再点一次收起，重新点 |

---

### 1:11 – 1:40 · 解释 + 一句话证明是 IBM Z

**动作：**
1. 鼠标移到右上角 **「IBM LinuxONE · s390x · Telum」** 那行字上，停 1 秒
2. 再移到右侧解释卡上，停 2 秒

> At the same time, IBM Granite writes a message the customer can understand, and a simulated alert for the family. It all runs on this machine, so no data leaves the bank.
>
> This is s390x, a real IBM Z machine, with an AI accelerator built into the processor. That is why the answer comes back in about 22 milliseconds.

> 💡 说 "This is s390x" 的时候，鼠标就停在顶部那行字上。评委看得到。

---

### 1:40 – 1:55 · 结果

**动作：** 无

> On a full replay of 587 transfers, we catch about two thirds of the fraud, and almost every transfer we stop is a real one. That is money that stays in the account.

> 💡 **只说约数，不报精确值。** 顶部计数器是这一次录制的实时累计，和完整一轮对不上，报精确值容易被追问。
> "two thirds" 和 "almost every" 都是保守说法，经得起核对。


---

### 1:55 – 2:07 · 收尾

> For the customer, a few more seconds to change their mind. For the family, an alert they can act on.
>
> Thank you.

**说完停 2 秒再停录**，方便后期裁。

---

## 全程只有三个动作

```
0:00 ─ 点 ▶ Start，开始念
0:24 ─ 鼠标指 绿 → 橙 → 红（各停 1 秒）
0:45 ─ 点一下红色 BLOCK 行
1:11 ─ 鼠标指顶部 "s390x" → 再指右侧卡片
1:40 ─ 念完收尾
```

**没有一次窗口切换，没有一次应用切换。**

---

## 停止与上传

| 步骤 | 操作 |
|---|---|
| 停止 | 点屏幕右上角菜单栏的 **⏹** 图标 |
| 查时长 | 播放器里按 **`⌘ + I`**，必须 **< 3:00** |
| 查声音 | 播放一遍，确认有声 |
| 上传 | YouTube → 可见性 **Unlisted（不公开列出）** |
| 验证 | **`⌘ + Shift + N`** 无痕窗口打开链接，确认能播 |

> 🔴 绝不能选 **Private** —— 评委打不开 = 直接不合格。

---

## 最后检查

```
☐ 时长 < 3:00（2:07 左右最舒服）
☐ 有声音（播放确认过）
☐ 开头能看到你自己点了 Start
☐ 地址栏能看到 148.100.76.225:8000
☐ 顶部能看到 "IBM LinuxONE · s390x"
☐ APPROVE / CONFIRM / BLOCK 都出现过
☐ 点开过案例，能看到金额递增的链
☐ 右侧出现过带家属信息的卡片
☐ YouTube 是 Unlisted，无痕能播
```

---

## 为什么去掉终端

- 少一次 `⌘ + Tab` = 少一个出错点
- 不用担心录制区域和窗口尺寸对不上
- **s390x 的证据本来就在浏览器顶部**，不用切窗口

如果你想要更硬的证据，可以单独录一段终端给评委看（不进视频），或者直接看仓库里的 `proof.sh`。
