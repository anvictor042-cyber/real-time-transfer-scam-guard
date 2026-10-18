#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 A4 竖版 Pitch Deck PDF（4 页，无冗余）。

英文按 humanizer 规范写：不用「不是X而是Y」对比、不用单句升华收尾、
不用「nobody else」这类抬价说法、不用铺垫式开场、破折号尽量少。

    python3 make_a4_pdf.py   →  proposal.pdf  (A4, 4 页)
"""
import base64
import os
import pathlib
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
OUT_HTML = HERE / "_a4.html"
OUT_PDF = HERE / "proposal.pdf"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def b64(name):
    p = HERE / name
    return base64.b64encode(p.read_bytes()).decode() if p.exists() else ""


ARCH, SHOT, CASE = b64("architecture.png"), b64("dashboard.png"), b64("dashboard-case.png")

CSS = """
@page { size: A4; margin: 0; }
* { margin:0; padding:0; box-sizing:border-box; }
html, body { background:#fff; }
body { font-family:"Helvetica Neue",Helvetica,Arial,"PingFang SC",sans-serif;
       color:#14161a; -webkit-font-smoothing:antialiased; font-size:9.9pt; line-height:1.52; }
.page { position:relative; width:210mm; height:297mm; background:#fff;
        padding:20mm 19mm 17mm 19mm; page-break-after:always; overflow:hidden; }
.page:last-child { page-break-after:auto; }
.rh { position:absolute; top:10mm; left:19mm; right:19mm; display:flex;
      justify-content:space-between; font-size:7.3pt; letter-spacing:.09em;
      text-transform:uppercase; color:#9aa3af; border-bottom:.4pt solid #e6e9ee;
      padding-bottom:2mm; }
.pn { position:absolute; bottom:8mm; left:19mm; right:19mm; display:flex;
      justify-content:space-between; font-size:7.5pt; color:#9aa3af;
      border-top:.4pt solid #e6e9ee; padding-top:2.2mm; }
h1 { font-size:31pt; line-height:1.05; letter-spacing:-.022em; font-weight:700; }
h2 { font-size:16.5pt; line-height:1.15; letter-spacing:-.012em; font-weight:700;
     margin:0 0 2.6mm 0; }
h3 { font-size:10.6pt; font-weight:700; margin-bottom:1.3mm; }
.eyebrow { font-size:7.9pt; letter-spacing:.15em; text-transform:uppercase;
           font-weight:700; color:#16a34a; margin-bottom:3.6mm; }
.lede { font-size:10.8pt; color:#3d4653; line-height:1.55; }
p { margin-bottom:2.6mm; color:#3d4653; }
p:last-child { margin-bottom:0; }
strong { color:#14161a; font-weight:700; }
.sec-no { font-size:7.9pt; letter-spacing:.13em; text-transform:uppercase;
          color:#9aa3af; font-weight:700; margin-bottom:2mm; }
.sp { height:5.5mm; }
.sp2 { height:3.4mm; }

.card { border:.5pt solid #e2e6ec; border-radius:2.2mm; padding:4.2mm; background:#fff; }
.card .k { font-size:7.6pt; letter-spacing:.07em; text-transform:uppercase;
           color:#8b95a3; font-weight:700; margin-bottom:1.4mm; }
.card .v { font-size:20pt; font-weight:700; letter-spacing:-.02em; }
.card .d { font-size:8.4pt; color:#6b7583; margin-top:.6mm; }

.callout { border-left:2.4pt solid #dc2626; background:#fdf4f4; padding:3.8mm 4.6mm;
           border-radius:0 1.8mm 1.8mm 0; }
.callout .t { font-weight:700; color:#b91c1c; font-size:10pt; margin-bottom:1.1mm; }
.callout .s { font-size:8.6pt; color:#7f1d1d; line-height:1.45; }

.tl { display:flex; margin:3.6mm 0; }
.tl .step { flex:1; border:.5pt solid #e2e6ec; border-radius:1.8mm; padding:2.8mm; font-size:8.6pt; }
.tl .step .a { font-weight:700; font-size:9pt; margin-bottom:.5mm; }
.tl .step .b { color:#7b8492; font-size:8pt; }
.tl .step.hot { border-color:#f3b4b4; background:#fdf4f4; }
.tl .step.hot .a { color:#b91c1c; }
.tl .gap { width:3.4mm; display:flex; align-items:center; justify-content:center;
           color:#c3cad4; font-size:10pt; }

.three { display:flex; gap:4mm; }
.three .o { flex:1; border-radius:2mm; padding:4mm; border:.6pt solid; }
.three .o .n { font-size:12.5pt; font-weight:700; margin-bottom:1.5mm; }
.three .o .m { font-size:9.2pt; font-weight:700; margin-bottom:1.1mm; }
.three .o .b { font-size:8.3pt; color:#5b6472; line-height:1.45; }
.o.g { background:#f6fdf9; border-color:#c3ecd8; } .o.g .n { color:#15803d; }
.o.a { background:#fffbf2; border-color:#f5e0b4; } .o.a .n { color:#b45309; }
.o.r { background:#fdf5f5; border-color:#f5c9c9; } .o.r .n { color:#b91c1c; }

.num { display:flex; gap:3.4mm; margin-bottom:2.6mm; }
.num .i { width:6.4mm; height:6.4mm; border-radius:1.2mm; background:#16a34a; color:#fff;
          font-weight:700; font-size:9pt; display:flex; align-items:center;
          justify-content:center; flex:none; }
.num .c .h { font-weight:700; font-size:9.8pt; margin-bottom:.4mm; }
.num .c .t { font-size:8.8pt; color:#5b6472; line-height:1.45; }

figure { margin:0; }
figure img { width:100%; display:block; border-radius:1.8mm; }
figcaption { font-size:8pt; color:#8b95a3; margin-top:1.6mm; line-height:1.45; }

table { width:100%; border-collapse:collapse; font-size:8.8pt; }
th { text-align:left; font-weight:700; font-size:7.8pt; letter-spacing:.05em;
     text-transform:uppercase; color:#6b7583; border-bottom:.8pt solid #d7dce4;
     padding:1.6mm 2.2mm; }
td { padding:1.55mm 2.2mm; border-bottom:.4pt solid #eceff3; color:#3d4653; }
tr.hl td { background:#f2fbf6; font-weight:700; color:#14161a; }

.kv { display:flex; gap:5mm; }
.kv .k { flex:1; }
.kv .k .v { font-size:21pt; font-weight:700; letter-spacing:-.02em; color:#16a34a; }
.kv .k .l { font-size:7.6pt; letter-spacing:.06em; text-transform:uppercase;
            color:#8b95a3; font-weight:700; margin-top:.9mm; }
.two { display:flex; gap:6mm; }
.two > * { flex:1; }
.bullets { list-style:none; }
.bullets li { position:relative; padding-left:4.2mm; margin-bottom:1.6mm; font-size:8.9pt;
              color:#3d4653; line-height:1.45; }
.bullets li:before { content:""; position:absolute; left:0; top:1.9mm; width:1.4mm;
                     height:1.4mm; border-radius:50%; background:#c3cad4; }
.bullets.neg li:before { background:#f0b4b4; }
.bullets.pos li:before { background:#86d3a8; }
.hr { height:.4pt; background:#e6e9ee; margin:3.4mm 0; }
.note { font-size:8pt; color:#8b95a3; line-height:1.45; }
"""


def head(t):
    return f'<div class="rh"><span>Real-Time Transfer Scam Guard</span><span>{t}</span></div>'


def foot(n):
    return (f'<div class="pn"><span>Real-Time Transfer Scam Guard · Team Chinese Can Fly</span>'
            f'<span>{n} / 3</span></div>')


pages = []

# ───────────────────────────────────────────────── 1 · 封面
pages.append(f"""
<div class="page">
  <div class="eyebrow">IBM Z Datathon 2026 · Track: Real-Time AI for Critical Decisions</div>
  <h1>Real-Time<br>Transfer Scam Guard</h1>
  <p class="lede" style="margin-top:4.4mm; max-width:145mm;">Scores every transfer before the
    money leaves, and returns APPROVE, CONFIRM or BLOCK in about 22 ms.</p>

  <div class="kv" style="margin-top:7mm;">
    <div class="k"><div class="v">65.2%</div><div class="l">Fraud recall</div></div>
    <div class="k"><div class="v">96.7%</div><div class="l">Precision on stops</div></div>
    <div class="k"><div class="v">22 ms</div><div class="l">Median decision</div></div>
    <div class="k"><div class="v">$18,418</div><div class="l">Recovered</div></div>
  </div>

  <figure style="margin-top:8mm;">
    <img src="data:image/png;base64,{CASE}">
    <figcaption>The console, running on IBM LinuxONE (s390x). Each row is one decision.
      The open panel shows the six transfers behind a blocked one: same account, a few
      minutes apart, amounts climbing from $14.75 to $602.24.</figcaption>
  </figure>

  <div class="sp"></div>
  <div class="two">
    <div><h3>What it is</h3>
      <p>A decision engine that sits inside the bank's authorisation path. When the risk is
        elevated it pauses the transfer, explains it to the account holder in plain
        language, and alerts a linked family member.</p></div>
    <div><h3>Why it matters</h3>
      <p>Older people authorise scam transfers themselves, so nothing looks wrong until the
        money clears. The few seconds before authorisation are the only place to intervene.</p></div>
  </div>

  <div style="position:absolute; bottom:16mm; left:19mm; right:19mm; display:flex;
              justify-content:space-between; border-top:.6pt solid #e6e9ee;
              padding-top:2.6mm; font-size:8.6pt; color:#6b7583;">
    <span><strong>Team Chinese Can Fly</strong></span><span>October 2026</span>
  </div>
</div>""")

# ───────────────────────────────────────────────── 2 · 问题 + 方案
pages.append(f"""
<div class="page">{head("The problem and the solution")}
  <div class="sec-no">Section 1 · The problem</div>
  <h2>Older people send the money themselves</h2>
  <p>To the bank the payment looks normal: the customer authenticated properly, from a
     device they have used before. Nothing is wrong until the money clears, and by then it
     is gone. The intervention point is the few seconds before authorisation.</p>

  <div class="tl">
    <div class="step"><div class="a">Victim tricked</div><div class="b">Hours of phone pressure</div></div>
    <div class="gap">&#9656;</div>
    <div class="step hot"><div class="a">Transfer authorised</div><div class="b">Valid PIN, valid device</div></div>
    <div class="gap">&#9656;</div>
    <div class="step"><div class="a">Funds cleared</div><div class="b">Irreversible</div></div>
    <div class="gap">&#9656;</div>
    <div class="step"><div class="a">Bank / family notice</div><div class="b">Too late</div></div>
  </div>

  <div class="callout">
    <div class="t">$4.885 billion reported lost by older Americans in 2024, across 147,127
      complaints, 43% more than 2023.</div>
    <div class="s">The FBI notes reporting is incomplete, because victims are embarrassed or
      do not know they were scammed. Source: FBI IC3, 2025. Existing fraud systems detect
      misuse after the fact; they were not built for a customer being talked into paying
      right now, and they cannot involve the family.</div>
  </div>

  <div class="hr"></div>

  <div class="sec-no">Section 2 · The solution</div>
  <h2>Three outcomes, decided in the authorisation path</h2>

  <div class="three" style="margin:3.4mm 0 4.4mm 0;">
    <div class="o g"><div class="n">APPROVE</div><div class="m">Release immediately</div>
      <div class="b">Risk below 0.55. Normal payments are not slowed down.</div></div>
    <div class="o a"><div class="n">CONFIRM</div><div class="m">Pause, explain, alert the family</div>
      <div class="b">Risk 0.55 to 0.95. The holder gets plain language. Above their guardian
        limit, a linked relative is alerted too.</div></div>
    <div class="o r"><div class="n">BLOCK</div><div class="m">Hold and record</div>
      <div class="b">Risk above 0.95. The transfer is held and an auditable record is
        written with reason codes.</div></div>
  </div>

  <div class="two">
    <div>
      <h3>Bringing in the family</h3>
      <p>A blocked card can be retried at another branch or online. A relative who knows the
         customer can end the call. CONFIRM is the outcome that pauses the payment and
         brings that person in.</p>
    </div>
    <div>
      <h3>Auditable by default</h3>
      <p>Nine reason codes (R01 to R09) travel with every decision, so a case can be
         reviewed later and the model audited over time. Clicking any row in the console
         opens the transfers behind that decision.</p>
    </div>
  </div>
  <div class="hr"></div>

  <div class="sec-no">Section 3 · Results</div>
  <h2>Measured on the LinuxONE instance</h2>

  <div class="kv" style="margin:1.4mm 0 2.4mm 0;">
    <div class="k"><div class="v">65.2%</div><div class="l">Fraud recall</div></div>
    <div class="k"><div class="v">96.7%</div><div class="l">Precision on stops</div></div>
    <div class="k"><div class="v">22 ms</div><div class="l">Median decision</div></div>
    <div class="k"><div class="v">$18,418</div><div class="l">Recovered</div></div>
  </div>

  <table>
    <tr><th>Offline quality, held-out test split (0.11% positives)</th><th>PR-AUC</th><th>ROC-AUC</th><th>Best F1</th></tr>
    <tr><td>LSTM only</td><td>0.3829</td><td>0.9293</td><td>0.478</td></tr>
    <tr><td>XGBoost only</td><td>0.0765</td><td>0.9411</td><td>0.161</td></tr>
    <tr class="hl"><td>Fusion (0.85 / 0.15)</td><td>0.4277</td><td>0.9654</td><td>0.506</td></tr>
  </table>
  {foot(2)}
</div>""")

# ───────────────────────────────────────────────── 3 · 怎么工作 + 证据（合并页）
pages.append(f"""
<div class="page">{head("How it works, results, scope")}
  <div class="sec-no">Section 4 · Architecture</div>
  <h2>Two models, one decision, about 22 ms</h2>

  <figure style="margin-top:1.2mm; width:144mm; margin-left:auto; margin-right:auto;">
    <img src="data:image/png;base64,{ARCH}">
    <figcaption>Only the decision sits in front of the customer. IBM Granite writes the
      explanation afterwards and never delays authorisation.</figcaption>
  </figure>

  <div class="two" style="margin-top:3.4mm;">
    <div><h3>Why two models</h3>
      <p>A 7-step LSTM reads the sequence of recent transfers; an XGBoost GBDT reads the
         structured risk. The scores are fused 0.85 / 0.15. XGBoost alone catches few
         frauds at usable precision, and the LSTM alone misses structured signals such as
         amount against the account's own history.</p></div>
    <div><h3>Why it stays fast</h3>
      <p>Feature construction and scoring are numeric work on the CPU. The language model
         runs on two threads in a separate pool, so writing an explanation cannot delay a
         decision.</p></div>
  </div>

  <div class="hr"></div>

  <div class="sec-no">Section 5 · Platform</div>
  <h2>Running on IBM Z / LinuxONE</h2>
  <div class="two">
    <div><ul class="bullets">
      <li><strong>Telum on-chip AI.</strong> Both models and Granite run on the same
        processor; the accelerator shares the die with the CPU.</li>
      <li><strong>Pervasive encryption.</strong> Data is encrypted at rest and in transit by
        the platform, quantum-safe.</li>
    </ul></div>
    <div><ul class="bullets">
      <li><strong>Data stays on platform.</strong> Granite is served locally by llama.cpp
        with the zDNN / NNPA backend. No external API calls.</li>
      <li><strong>Container native.</strong> One Docker image on IBM's s390x AI/ML base,
        health-checked. <code>uname -m</code> returns <code>s390x</code>.</li>
    </ul></div>
  </div>

  <div class="hr"></div>

  <div class="sec-no">Section 6 · Scope</div>
  <h2>What it does and does not do</h2>
  <div class="two">
    <div><ul class="bullets pos">
      <li>Scores each transfer in about 22 ms and returns one of three decisions</li>
      <li>Writes a plain-language message for the holder, with reason codes</li>
      <li>Alerts a linked relative above the guardian limit</li>
      <li>Runs containerised on LinuxONE, with no API calls</li>
    </ul></div>
    <div><ul class="bullets neg">
      <li>No live bank core integration; the stream is a replay</li>
      <li>The guardian notification is simulated, not a real SMS gateway</li>
      <li>No production load testing; age fields are a synthetic overlay</li>
      <li>onnxruntime has no s390x wheel, so ONNX is export-only</li>
    </ul></div>
  </div>

  <p class="note" style="margin-top:2mm;">Next 30 days: swap the replay for the bank's
    authorisation feed, connect a real notification provider, and run IEEE-CIS and PaySim as
    the production corpus. Code, benchmark and tests:
    github.com/anvictor042-cyber/real-time-transfer-scam-guard (MIT).</p>
  {foot(3)}
</div>""")

html = (f'<!DOCTYPE html><html><head><meta charset="utf-8">'
        f'<title>Real-Time Transfer Scam Guard — Pitch Deck</title>'
        f'<style>{CSS}</style></head><body>{"".join(pages)}</body></html>')

OUT_HTML.write_text(html, encoding="utf-8")
print(f"HTML {len(html)//1024} KB, {len(pages)} 页")

if os.path.exists(CHROME):
    if OUT_PDF.exists():
        OUT_PDF.unlink()
    subprocess.run([CHROME, "--headless=new", "--disable-gpu",
                    "--no-pdf-header-footer", f"--print-to-pdf={OUT_PDF}", OUT_HTML.as_uri()],
                   check=False, capture_output=True, timeout=180)
    if OUT_PDF.exists():
        print(f"✅ {OUT_PDF.name}  {OUT_PDF.stat().st_size/1024:.0f} KB")
    else:
        print("❌ 打印失败")
