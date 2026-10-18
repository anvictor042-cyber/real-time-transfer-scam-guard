# 提交操作手册 — 照着做即可

> 目标：在截止前把 11 项全部填好并在 Hack2skill 提交。
> 预计耗时：**约 1.5 小时**（不含录视频重录）。

---

## 一、现在已就绪的东西

| 文件 | 用途 | 状态 |
|---|---|---|
| `README.md` | GitHub 仓库首页 | 就绪 |
| `OPENSOURCE.md` | 开源资源清单（表单第 10 项） | 就绪 |
| `Dockerfile` / `docker-compose.yml` | 容器化（评分硬性项，已实测构建+运行） | 就绪 |
| `submission/pitch-deck.pdf` | **上传用 PDF**（8 页，640 KB < 5 MB） | 就绪 |
| `submission/pitch-deck.pptx` | 可编辑源文件（如需改） | 就绪 |
| `submission/architecture.png` | 架构图（表单第 11 项） | 就绪 |
| `submission/dashboard.png` | 实时控制台 1080p 截图（Deck 第 5 页 / 备用素材） | 就绪 |
| `submission/form-texts.md` | **4 段文案，直接复制粘贴** | 就绪 |
| `submission/video-script.md` | 3 分钟录制脚本 | 就绪 |

**服务地址**：http://148.100.76.225:8000
**稳定截图地址**：http://148.100.76.225:8000/?seed=30 （秒出满屏数据，适合做封面/静帧）

---

## 二、按顺序执行

### 步骤 1 · 重置服务（录屏前必做，让计数从 0 开始）

```bash
ssh datathon 'sudo docker restart scam-guard'
sleep 35
curl -s http://148.100.76.225:8000/api/health
```

看到 `"engine_ready":true,"explainer_ready":true` 就可以开录。

---

### 步骤 2 · 录视频（45 分钟）

打开 `submission/video-script.md`，照时间码念。

录制：`⌘ + Shift + 5` → 录制所选部分 → 选浏览器窗口 → 麦克风选内置

**关键要求**
- 时长 **必须 < 3:00**（录完用 QuickTime `⌘I` 确认）
- 必须出现 `s390x` 的终端画面
- 必须出现 APPROVE / CONFIRM / BLOCK 三种决策
- 提到家属通知时说 **"simulated"**

上传 YouTube → 可见性选 **Unlisted（不公开列出）** → 复制链接 → **用无痕窗口打开确认能播**。

---

### 步骤 3 · 推 GitHub

```bash
cd /Users/anvincent/Documents/deepseek-harness/default-workspace/datathon/fraud-shield
git init
git add .
git commit -m "Real-Time Transfer Scam Guard — IBM Z Datathon 2026"
git branch -M main
git remote add origin https://github.com/<你的账号>/<仓库名>.git
git push -u origin main
```

**注意**
- `models/` 里有训练产物（`lstm_fraud.keras` 约 1 MB、`xgb_fraud.json`），本地目录是空的 —— 需要从服务器取回：

```bash
scp -r datathon:/home/linux1/shared/fraud-shield/models/* ./models/
```

- 仓库必须 **Public**
- 推完后用**无痕窗口**打开仓库地址，确认未登录也能看到代码

---

### 步骤 4 · 填表（20 分钟）

打开 Hack2skill → Submissions → `IBM Z Datathon - Project Submissions`

| # | 字段 | 怎么填 |
|---|---|---|
| 1 | **Challenges** | 下拉选 **Real-Time AI for Critical Decisions** |
| 2 | What is the Problem… | 复制 `submission/form-texts.md` **第 1 段**（772/1024） |
| 3 | How are you planning to solve… | 复制 **第 2 段**（1013/1024） |
| 4 | How does your solution leverage IBM Z… | 复制 **第 3 段**（994/1024） |
| 5 | What value does your solution deliver… | 复制 **第 4 段**（986/1024） |
| 6 | Upload pitch deck PDF | 上传 `submission/pitch-deck.pdf` |
| 7 | Github Link | 你的仓库链接（`https://` 开头） |
| 8 | Video Submission Link | YouTube Unlisted 链接 |
| 9 | Pitch deck link | **留空**（第 6 项已上传文件） |
| 10 | Link to all open-source resources | 填你仓库里 OPENSOURCE.md 的链接，如 `https://github.com/<账号>/<仓库>/blob/main/OPENSOURCE.md` |
| 11 | Any other document | 架构图链接：`https://github.com/<账号>/<仓库>/blob/main/submission/architecture.png` |

→ 点 **Submit**

---

### 步骤 5 · 确认提交成功

- 查邮箱，应收到 **"submission has been successfully received"** 邮件（就像 10/5 那封）
- **截图存档**这封邮件
- 回到 Submission 页面确认状态变为已提交

---

## 三、提交前最终检查清单

```
☐ Challenges 已选 Real-Time AI for Critical Decisions
☐ 4 段文案都填了，页面没提示超字数
☐ Pitch Deck PDF 上传成功（页面上能看到文件名）
☐ GitHub 链接无痕窗口可访问，且是 Public
☐ 视频链接无痕窗口可播放，时长 < 3:00
☐ 开源资源链接可访问
☐ 架构图链接可访问（选填但建议填）
☐ 点了 Submit
☐ 收到确认邮件（截图）
```

---

## 四、如果出问题

| 问题 | 处理 |
|---|---|
| 服务起不来 | `ssh datathon 'sudo docker restart scam-guard'`，等 40 秒再访问 |
| 视频超过 3 分钟 | 砍掉 1:50–2:15 的终端段，改在片尾口播 "running on s390x" |
| GitHub 推不上去 | 改用 zip 上传网盘（Google Drive / 阿里云盘），链接填第 7 项 |
| PDF 超过 5MB | 当前 640 KB，不会超；若改图后变大，用 `压缩` 或减少图片 |
| 平台不支持修改提交 | 先确认再提交；若只能交一次，务必在全部就绪后再点 Submit |
| 忘记填某项 | 提交后若可编辑，补填再保存；否则立刻在 Discord `#helpdesk` 说明 |

---

## 五、口径统一（视频与文字必须一致）

所有材料已统一为以下数字，**口播和幻灯片不要说出别的数字**：

| 指标 | 数值 |
|---|---|
| 回放笔数 | 587 |
| 放行 / 需确认 / 拦截 | 467 / 70 / 50 |
| 欺诈召回 | **65.2 %** |
| 停损精确率 | **96.7 %** |
| 决策延迟 p50 | **22 ms**（p95 50 ms） |
| 挽回金额 | **$18,418** |
| 家属通知 | 29 次 |

离线模型质量：LSTM 单独 PR-AUC 0.3829 / ROC-AUC 0.9293；XGBoost 单独 0.0765 / 0.9411；
**融合 0.4277 / 0.9654**。
