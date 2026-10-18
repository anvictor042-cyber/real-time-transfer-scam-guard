# 3-Minute Demo Video Script

**Hard limit: 3:00.** This narration is 390 words ≈ **2:41** at a calm 145 wpm, leaving ~19 s of headroom.

---

## Before you record (5 minutes)

```bash
# 1. Reset counters so the demo starts from zero
ssh datathon 'sudo docker restart scam-guard && sleep 35'

# 2. Confirm it is healthy
curl -s http://148.100.76.225:8000/api/health
```

**Open two windows**
- A: `http://148.100.76.225:8000` — the dashboard
- B: a terminal with `ssh datathon` — for the s390x proof shot

**Recording setup**
- `⌘ + Shift + 5` → Record Selected Portion → pick the dashboard window
- Microphone: built-in is fine; quiet room, no fan
- Resolution: 1080p
- **Do 2–3 takes.** Do not edit — one clean take beats a rushed edit.

---

## Shot list

### 0:00 – 0:12 · Title card
**On screen:** pitch deck slide 1
**Say:**
> Every year, older people are talked into sending their own money to scammers. And the bank sees nothing wrong.

### 0:12 – 0:35 · The problem
**On screen:** pitch deck slide 2 (scam timeline)
**Say:**
> The transfer looks completely normal. Valid card, valid PIN, valid device. Nothing is anomalous, because the customer is doing it themselves.
>
> By the time anyone notices, the money has cleared. There is exactly one moment where a scam can still be stopped: the few seconds before authorisation.

### 0:35 – 0:58 · The solution
**On screen:** pitch deck slide 3 (three outcome cards)
**Say:**
> This is Real-Time Transfer Scam Guard. Every transfer is scored inside the authorisation path and gets one of three outcomes.
>
> Approve, release it. Confirm, pause it, tell the customer in plain language, and alert a linked family member. Block, hold it, and write an audit record.
>
> That middle case is what nobody else does. It does not just stop the payment, it brings in the person who can actually stop the scam.

### 0:58 – 1:50 · Live demo
**On screen:** the live dashboard, streaming
**Action:** let it run. A CONFIRM should appear on the right within the first ~20 seconds.
**Say:**
> This is running live on IBM LinuxONE.
>
> Transfers stream in. Each one is scored by two models: an LSTM reading the last seven transfers, and an XGBoost reading the structured risk. Their scores are fused, and the decision comes back in about twenty milliseconds.
>
> Look at this one. High risk. Watch the right panel. *(point)*
>
> IBM Granite writes two things: a sentence the customer can understand, and an alert for the family. Generated locally on this machine, so the data never leaves the platform.
>
> And every decision carries reason codes, so an analyst can review the case later.

### 1:50 – 2:15 · Why IBM Z
**On screen:** cut to terminal
**Action:** run
```bash
ssh datathon 'uname -m; nproc; sudo docker ps --format "{{.Names}} {{.Status}}"'
```
**Say:**
> This is not an x86 app ported over. We are on s390x: three cores and one on-chip AI accelerator.
>
> Because the accelerator sits on the same die as the CPU, the decision stays fast even while the language model is generating. And pervasive encryption means the data is protected by the platform, not by our code.

### 2:15 – 2:42 · Results
**On screen:** pitch deck slide 7 (metrics)
**Say:**
> On the full stream: sixty-five percent fraud recall at ninety-six percent precision on the transfers we stop, recovering over eighteen thousand dollars.
>
> The fusion matters. Alone, each model is weaker. Combined, ROC-AUC is zero point nine six.

### 2:42 – 3:00 · Close
**On screen:** pitch deck slide 8 (beneficiaries), then back to the dashboard
**Say:**
> For the older customer, it buys back the seconds where they can still change their mind. For their children, an alert they can act on. For the bank, loss avoided with a record they can show a regulator.
>
> Real-time AI, deciding while it still matters. Thank you.

---

## Stills you can use (no recording needed)

The dashboard has a seed mode that renders a populated view instantly:

```
http://148.100.76.225:8000/?seed=30
```

About 30 rows with APPROVE / CONFIRM / BLOCK already present, plus two explanation cards.
Add `&explain=0` to hide the cards. Add `&nosse=1` to stop the live feed and keep the frame still.

## Checklist before upload

- [ ] Duration **strictly under 3:00** (QuickTime `⌘I`)
- [ ] 1080p
- [ ] Audio audible throughout, no clipping
- [ ] The terminal shot really shows `s390x`
- [ ] The dashboard shot really shows APPROVE, CONFIRM and BLOCK
- [ ] Upload to YouTube as **Unlisted** (not Private)
- [ ] Open the link in an incognito window to confirm it plays

## If a take goes wrong

| Problem | Fix |
|---|---|
| No CONFIRM appeared | Set speed to 3 tx/s and wait; CONFIRM appears within the first ~25 transfers |
| The Granite panel looks empty | It takes ~5 s; hold the shot, or say "the explanation lands a few seconds later" |
| You stumble on a word | Keep going, finish the take, re-record only if it is bad |
| Terminal shows the wrong thing | That is a cut-in, not live — re-record just that 25-second segment |

## Honest wording to keep

Say **"simulated"** if you mention the family alert reaching a phone. It is generated and displayed, not sent by SMS. Do not imply a real message was delivered.
