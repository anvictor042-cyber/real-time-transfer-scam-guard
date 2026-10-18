#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 Pitch Deck（PPTX）—— Real-Time Transfer Scam Guard"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

HERE = os.path.dirname(os.path.abspath(__file__))
ARCH = os.path.join(HERE, "architecture.png")
OUT = os.path.join(HERE, "pitch-deck.pptx")

INK = RGBColor(0x1A, 0x24, 0x33)
DIM = RGBColor(0x5C, 0x6B, 0x80)
BLUE = RGBColor(0x25, 0x63, 0xEB)
PURPLE = RGBColor(0x7C, 0x3A, 0xED)
AMBER = RGBColor(0xD9, 0x77, 0x06)
GREEN = RGBColor(0x16, 0xA3, 0x4A)
RED = RGBColor(0xDC, 0x26, 0x26)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BG = RGBColor(0xF7, 0xF9, 0xFC)
CARD = RGBColor(0xFF, 0xFF, 0xFF)
LINE = RGBColor(0xE2, 0xE8, 0xF0)

FONT = "Arial"
W, H = 13.333, 7.5


def new_deck():
    prs = Presentation()
    prs.slide_width = Inches(W)
    prs.slide_height = Inches(H)
    return prs


def blank(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bg = s.shapes.add_shape(1, 0, 0, Inches(W), Inches(H))
    bg.fill.solid(); bg.fill.fore_color.rgb = BG
    bg.line.fill.background()
    bg.shadow.inherit = False
    return s


def text(slide, x, y, w, h, s, size=16, color=INK, bold=False, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, spacing=1.0, italic=False):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    lines = s.split("\n")
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        r = p.add_run(); r.text = ln
        r.font.size = Pt(size); r.font.name = FONT
        r.font.color.rgb = color; r.font.bold = bold; r.font.italic = italic
    return tb


def card(slide, x, y, w, h, fill=CARD, border=LINE, radius=None):
    sh = slide.shapes.add_shape(1, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.fill.solid(); sh.fill.fore_color.rgb = fill
    sh.line.color.rgb = border; sh.line.width = Pt(1)
    sh.shadow.inherit = False
    return sh


def header(slide, kicker, title, accent=BLUE):
    bar = slide.shapes.add_shape(1, Inches(0.7), Inches(0.62), Inches(0.09), Inches(0.52))
    bar.fill.solid(); bar.fill.fore_color.rgb = accent
    bar.line.fill.background(); bar.shadow.inherit = False
    text(slide, 0.95, 0.55, 11.5, 0.32, kicker.upper(), size=10.5, color=accent, bold=True)
    text(slide, 0.95, 0.82, 11.5, 0.55, title, size=27, color=INK, bold=True)


def footer(slide, n, total, label="Real-Time Transfer Scam Guard  ·  Chinese Can Fly"):
    text(slide, 0.7, 7.02, 8, 0.28, label, size=9, color=DIM)
    text(slide, 11.6, 7.02, 1.0, 0.28, f"{n} / {total}", size=9, color=DIM, align=PP_ALIGN.RIGHT)


# ============================================================ 1 · 标题
def slide_title(prs, total):
    s = blank(prs)
    band = s.shapes.add_shape(1, 0, 0, Inches(W), Inches(2.35))
    band.fill.solid(); band.fill.fore_color.rgb = RGBColor(0x0F, 0x1A, 0x2E)
    band.line.fill.background(); band.shadow.inherit = False

    text(s, 0.9, 0.75, 11.5, 0.35, "IBM Z DATATHON 2026  ·  TEAM CHINESE CAN FLY",
         size=11, color=RGBColor(0x93, 0xB4, 0xE8), bold=True)
    text(s, 0.9, 1.15, 11.5, 0.85, "Real-Time Transfer Scam Guard",
         size=40, color=WHITE, bold=True)

    text(s, 0.9, 2.75, 11.2, 0.7,
         "Stopping scam-driven transfers inside the bank's authorisation path,\nbefore the money leaves.",
         size=19, color=INK, spacing=1.25)

    card(s, 0.9, 3.95, 11.5, 0.62, fill=RGBColor(0xEE, 0xF2, 0xFF),
         border=RGBColor(0xC7, 0xD2, 0xFE))
    text(s, 1.15, 4.10, 11.0, 0.35,
         "Track: Real-Time AI for Critical Decisions   ·   Core principle: data analysed immediately → AI influences decisions while it matters",
         size=12.5, color=RGBColor(0x37, 0x30, 0xA3), bold=True)

    for i, (t, sub, c) in enumerate([
            ("APPROVE", "release", GREEN),
            ("CONFIRM", "pause + alert the family", AMBER),
            ("BLOCK", "hold + audit record", RED)]):
        x = 0.9 + i * 3.9
        card(s, x, 4.95, 3.6, 1.15)
        text(s, x + 0.25, 5.12, 3.2, 0.4, t, size=19, color=c, bold=True)
        text(s, x + 0.25, 5.56, 3.2, 0.35, sub, size=12, color=DIM)

    text(s, 0.9, 6.45, 11.5, 0.4,
         "Runs on IBM LinuxONE (s390x)  ·  Telum on-chip AI  ·  pervasive encryption  ·  container native",
         size=11.5, color=DIM)
    return s


# ============================================================ 2 · 问题
def slide_problem(prs, n, total):
    s = blank(prs)
    header(s, "the problem", "Older people send the money themselves", RED)

    steps = [("Victim tricked", "phone scam, hours of pressure"),
             ("Transfer authorised", "valid PIN, valid device"),
             ("Funds cleared", "irreversible"),
             ("Bank / family notice", "too late")]
    x0, wid, gap = 0.9, 2.75, 0.28
    for i, (t, sub) in enumerate(steps):
        x = x0 + i * (wid + gap)
        crit = (i == 1)
        card(s, x, 1.85, wid, 1.25,
             fill=RGBColor(0xFE, 0xF2, 0xF2) if crit else CARD,
             border=RED if crit else LINE)
        text(s, x + 0.2, 2.02, wid - 0.4, 0.4, t, size=14, color=RED if crit else INK, bold=True)
        text(s, x + 0.2, 2.45, wid - 0.4, 0.5, sub, size=10.5, color=DIM)
        if i < 3:
            text(s, x + wid - 0.02, 2.26, gap + 0.04, 0.3, "›", size=20, color=DIM,
                 align=PP_ALIGN.CENTER)

    card(s, 0.9, 3.30, 11.5, 0.98, fill=RGBColor(0xFE, 0xF2, 0xF2), border=RGBColor(0xFE, 0xCA, 0xCA))
    text(s, 1.15, 3.42, 11.0, 0.34,
         "The only effective intervention point is the few seconds BEFORE authorisation.",
         size=13.5, color=RED, bold=True)
    text(s, 1.15, 3.80, 11.0, 0.38,
         "$4.885 billion reported lost by older Americans in 2024 across 147,127 complaints, "
         "up 43% on 2023.  FBI IC3, 2025",
         size=10.5, color=RGBColor(0x8a, 0x3a, 0x3a))

    pts = [("It looks normal to the bank", "Valid credentials, valid device, correct PIN. Nothing in the payment itself is anomalous."),
           ("Existing systems target card fraud", "They detect misuse after the fact. They are not built for a customer being talked into paying right now."),
           ("The family is never involved", "The adult children who could actually stop it have no way in.")]
    for i, (t, d) in enumerate(pts):
        x = 0.9 + i * 3.9
        card(s, x, 4.52, 3.6, 1.80)
        text(s, x + 0.25, 4.68, 3.1, 0.4, t, size=13, color=INK, bold=True)
        text(s, x + 0.25, 5.10, 3.1, 1.1, d, size=10.5, color=DIM, spacing=1.15)

    footer(s, n, total)
    return s


# ============================================================ 3 · 方案
def slide_solution(prs, n, total):
    s = blank(prs)
    header(s, "the solution", "Three outcomes, decided in the authorisation path", BLUE)

    cards = [("APPROVE", "Release immediately", "Risk below 0.55.\nNo friction added to normal payments.", GREEN,
              RGBColor(0xF0, 0xFD, 0xF4), RGBColor(0xBB, 0xF7, 0xD0)),
             ("CONFIRM", "Pause · message the holder · alert the family",
              "Risk 0.55–0.95.\nThe holder gets plain language.\nIf the amount exceeds the guardian limit,\na linked relative is alerted too.", AMBER,
              RGBColor(0xFF, 0xFB, 0xEB), RGBColor(0xFD, 0xE6, 0x8A)),
             ("BLOCK", "Hold and record", "Risk above 0.95.\nTransfer held; an auditable record is written\nwith reason codes.", RED,
              RGBColor(0xFE, 0xF2, 0xF2), RGBColor(0xFE, 0xCA, 0xCA))]
    for i, (t, sub, body, c, fc, bc) in enumerate(cards):
        x = 0.9 + i * 3.9
        card(s, x, 1.8, 3.6, 2.75, fill=fc, border=bc)
        text(s, x + 0.28, 2.0, 3.0, 0.45, t, size=22, color=c, bold=True)
        text(s, x + 0.28, 2.52, 3.05, 0.5, sub, size=11.5, color=INK, bold=True)
        text(s, x + 0.28, 3.15, 3.05, 1.2, body, size=10, color=DIM, spacing=1.2)

    card(s, 0.9, 4.78, 11.5, 1.55)
    text(s, 1.15, 4.95, 5.3, 0.35, "The part nobody else does", size=13, color=PURPLE, bold=True)
    text(s, 1.15, 5.33, 5.3, 0.85,
         "CONFIRM pauses the transfer and brings in the one person\nwho can end the call: the family.",
         size=11, color=INK, spacing=1.2)

    text(s, 6.9, 4.95, 5.3, 0.35, "Every decision is auditable", size=13, color=PURPLE, bold=True)
    text(s, 6.9, 5.33, 5.3, 0.85,
         "Nine reason codes (R01–R09) travel with each decision,\nso a case can be reviewed and the model audited later.",
         size=11, color=INK, spacing=1.2)

    footer(s, n, total)
    return s


# ============================================================ 4 · 架构
def slide_arch(prs, n, total):
    s = blank(prs)
    header(s, "architecture", "Two models, one decision, ~22 ms", BLUE)
    if os.path.exists(ARCH):
        s.shapes.add_picture(ARCH, Inches(0.55), Inches(1.62), width=Inches(12.25))
    text(s, 0.9, 6.72, 11.5, 0.3,
         "Decision and explanation are decoupled: the decision returns in ~22 ms, while IBM Granite explains asynchronously.",
         size=10, color=DIM, italic=True)
    footer(s, n, total)
    return s


# ============================================================ 5 · 实时控制台
def slide_console(prs, n, total):
    s = blank(prs)
    header(s, "the console", "This is the screen, running on LinuxONE", BLUE)
    shot = os.path.join(HERE, "dashboard.png")
    if os.path.exists(shot):
        s.shapes.add_picture(shot, Inches(1.35), Inches(1.5), height=Inches(5.55))
    text(s, 0.9, 7.12, 11.5, 0.3,
         "Every row is a live decision. Right lane: the plain-language message the holder sees, "
         "and the alert the linked relative receives.",
         size=10, color=DIM, italic=True)
    footer(s, n, total)
    return s


# ============================================================ 5 · 为什么是 IBM Z
def slide_ibmz(prs, n, total):
    s = blank(prs)
    header(s, "why ibm z / linuxone", "Not an x86 app ported over", PURPLE)

    items = [("Telum on-chip AI",
              "Both models and the Granite LLM run on the same processor.\n"
              "The accelerator sits on the same die as the CPU, which is why\n"
              "the decision stays fast even while the LLM generates."),
             ("Pervasive encryption",
              "Data encrypted at rest and in transit by the platform,\n"
              "quantum-safe. Scam detection must read sensitive transfer\n"
              "and identity context, so this is a prerequisite."),
             ("Data never leaves",
              "Granite is served locally by llama.cpp with the zDNN/NNPA\n"
              "backend. No external API calls. No customer data leaves the\n"
              "enterprise perimeter."),
             ("Container native",
              "Shipped as a Docker image built on IBM's s390x AI/ML base image.\n"
              "One command to deploy; health-checked and restart-safe.")]
    for i, (t, d) in enumerate(items):
        col, row = i % 2, i // 2
        x = 0.9 + col * 6.0
        y = 1.85 + row * 2.35
        card(s, x, y, 5.6, 2.05)
        text(s, x + 0.3, y + 0.22, 5.0, 0.4, t, size=15, color=PURPLE, bold=True)
        text(s, x + 0.3, y + 0.72, 5.0, 1.2, d, size=10.5, color=DIM, spacing=1.2)

    footer(s, n, total)
    return s


# ============================================================ 6 · 结果
def slide_results(prs, n, total):
    s = blank(prs)
    header(s, "results", "Measured on the LinuxONE instance", GREEN)

    big = [("65.2 %", "fraud recall", GREEN),
           ("96.7 %", "precision on stops", GREEN),
           ("22 ms", "median decision", BLUE),
           ("$18,418", "amount recovered", AMBER)]
    for i, (v, lab, c) in enumerate(big):
        x = 0.9 + i * 2.95
        card(s, x, 1.8, 2.7, 1.35)
        text(s, x + 0.22, 1.98, 2.3, 0.6, v, size=26, color=c, bold=True)
        text(s, x + 0.22, 2.62, 2.3, 0.35, lab, size=11, color=DIM)

    text(s, 0.9, 3.42, 6.0, 0.35, "Offline model quality  (held-out test, 0.11 % positives)",
         size=12, color=INK, bold=True)

    rows = [("Model", "PR-AUC", "ROC-AUC", "Best F1"),
            ("LSTM only", "0.3829", "0.9293", "0.478"),
            ("XGBoost only", "0.0765", "0.9411", "0.161"),
            ("Fusion (0.85 / 0.15)", "0.4277", "0.9654", "0.506")]
    tw, th = 6.0, 0.42
    tb = s.shapes.add_table(len(rows), 4, Inches(0.9), Inches(3.85),
                            Inches(tw), Inches(th * len(rows))).table
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            cell = tb.cell(r, c)
            cell.text = val
            p = cell.text_frame.paragraphs[0]
            p.runs[0].font.size = Pt(10.5)
            p.runs[0].font.name = FONT
            p.runs[0].font.bold = (r == 0 or r == 3)
            p.runs[0].font.color.rgb = INK if r in (0, 3) else DIM

    text(s, 7.3, 3.42, 5.1, 0.35, "Why fusion", size=12, color=INK, bold=True)
    text(s, 7.3, 3.85, 5.1, 2.2,
         "Every single model leaves money on the table:\n\n"
         "· XGBoost alone catches few frauds at usable precision\n"
         "· LSTM alone misses structured signals such as amount\n"
         "  versus the account's own history\n"
         "· The fusion beats both on PR-AUC and on F1, which is\n"
         "  exactly why two frameworks are used rather than one.",
         size=10.5, color=DIM, spacing=1.22)

    text(s, 0.9, 6.35, 11.5, 0.35,
         "587 replayed transfers (single reproducible pass)  ·  3 vCPU + 1 AI accelerator  ·  587-transfer curated stream including 271 labelled frauds",
         size=9.5, color=DIM)
    footer(s, n, total)
    return s


# ============================================================ 7 · 价值
def slide_value(prs, n, total):
    s = blank(prs)
    header(s, "who benefits", "Four audiences, in order of directness", AMBER)

    items = [("Older adults targeted by scams",
              "They act alone and often cannot stop themselves in time. The system pauses the transfer and\n"
              "offers a plain way to say \"I am not sure\" instead of losing their savings."),
             ("Adult children living away",
              "They cannot watch every transfer. They set a guardian limit and get an actionable alert,\n"
              "turning distant worry into a decision they can make from their phone."),
             ("Banks and payment providers",
              "Fewer scam losses and complaints, plus a defensible audit record for regulators. The engine\n"
              "sits in the authorisation path, so it cuts loss without slowing genuine payments."),
             ("Anti-fraud teams and regulators",
              "Every decision carries reason codes. Cases can be reviewed later and the model audited\n"
              "over time, which most regulated markets require.")]
    for i, (t, d) in enumerate(items):
        y = 1.82 + i * 1.23
        card(s, 0.9, y, 11.5, 1.06)
        num = s.shapes.add_shape(1, Inches(1.15), Inches(y + 0.24), Inches(0.42), Inches(0.42))
        num.fill.solid(); num.fill.fore_color.rgb = AMBER
        num.line.fill.background(); num.shadow.inherit = False
        text(s, 1.15, y + 0.31, 0.42, 0.3, str(i + 1), size=12, color=WHITE, bold=True,
             align=PP_ALIGN.CENTER)
        text(s, 1.78, y + 0.16, 10.3, 0.32, t, size=13, color=INK, bold=True)
        text(s, 1.78, y + 0.52, 10.3, 0.5, d, size=10, color=DIM, spacing=1.15)

    footer(s, n, total)
    return s


# ============================================================ 8 · 诚实边界
def slide_limits(prs, n, total):
    s = blank(prs)
    header(s, "scope", "What this prototype is and is not", DIM)

    left = ("What it does", GREEN, RGBColor(0xF0, 0xFD, 0xF4), RGBColor(0xBB, 0xF7, 0xD0),
            ["Streams transfers and scores each one in ~22 ms",
             "Three-way decision with reason codes",
             "Plain-language message for the holder",
             "Guardian alert when the limit is exceeded",
             "Fully containerised, runs on LinuxONE",
             "Granite explanations generated locally, no API calls"])
    right = ("What it does not do (yet)", AMBER, RGBColor(0xFF, 0xFB, 0xEB), RGBColor(0xFD, 0xE6, 0x8A),
             ["No live bank core integration; the stream is historical replay",
              "Guardian notification is simulated, not a real SMS gateway",
              "No production load testing at peak volume",
              "Age and guardian fields are a synthetic scenario overlay",
              "onnxruntime has no s390x wheel, so ONNX is export-only"])

    for i, (title, c, fc, bc, items) in enumerate((left, right)):
        x = 0.9 + i * 6.0
        card(s, x, 1.8, 5.6, 3.65, fill=fc, border=bc)
        text(s, x + 0.3, 1.98, 5.0, 0.35, title, size=14, color=c, bold=True)
        for j, it in enumerate(items):
            text(s, x + 0.3, 2.42 + j * 0.48, 5.0, 0.42, "·  " + it, size=10.5, color=INK,
                 spacing=1.1)

    card(s, 0.9, 5.65, 11.5, 0.9, fill=RGBColor(0xEE, 0xF2, 0xFF), border=RGBColor(0xC7, 0xD2, 0xFE))
    text(s, 1.15, 5.83, 11.0, 0.6,
         "Next 30 days: swap the replay for the bank's authorisation feed, connect a real notification provider, "
         "and run IEEE-CIS + PaySim as the production corpus with time-drift and fairness checks.",
         size=11, color=RGBColor(0x37, 0x30, 0xA3), spacing=1.15)

    footer(s, n, total)
    return s


def main():
    prs = new_deck()
    total = 9
    slide_title(prs, total)
    slide_problem(prs, 2, total)
    slide_solution(prs, 3, total)
    slide_arch(prs, 4, total)
    slide_console(prs, 5, total)
    slide_ibmz(prs, 6, total)
    slide_results(prs, 7, total)
    slide_value(prs, 8, total)
    slide_limits(prs, 9, total)
    prs.save(OUT)
    print(f"已生成 {OUT}  ({os.path.getsize(OUT)/1024:.0f} KB, {len(prs.slides)} 页)")


if __name__ == "__main__":
    main()
