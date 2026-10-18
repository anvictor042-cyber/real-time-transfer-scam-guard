#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成架构图 PNG（用于 Pitch Deck 与视频）"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "architecture.png")

BG = "#f7f9fc"
INK = "#1a2433"
DIM = "#5c6b80"
BLUE = "#2563eb"
PURPLE = "#7c3aed"
AMBER = "#d97706"
GREEN = "#16a34a"
RED = "#dc2626"
GRAY = "#e2e8f0"

fig, ax = plt.subplots(figsize=(16, 7.75), dpi=170)
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.set_xlim(0, 16)
ax.set_ylim(0.0, 7.75)
ax.axis("off")


def box(x, y, w, h, label, sub=None, fc="white", ec=GRAY, tc=INK, fs=12, sfs=9.5, lw=1.6):
    p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                       linewidth=lw, edgecolor=ec, facecolor=fc, zorder=2)
    ax.add_patch(p)
    if sub:
        ax.text(x + w / 2, y + h * 0.63, label, ha="center", va="center",
                fontsize=fs, color=tc, weight="bold", zorder=3)
        ax.text(x + w / 2, y + h * 0.3, sub, ha="center", va="center",
                fontsize=sfs, color=DIM, zorder=3, linespacing=1.4)
    else:
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center",
                fontsize=fs, color=tc, weight="bold", zorder=3)


def arrow(x1, y1, x2, y2, color="#94a3b8", lw=1.8):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                 mutation_scale=15, linewidth=lw,
                                 color=color, zorder=1,
                                 shrinkA=2, shrinkB=2))


# 标题由幻灯片本身提供，图里不再重复

# ---------------- platform band (right) ----------------
band = FancyBboxPatch((12.35, 1.05), 3.3, 6.5, boxstyle="round,pad=0.03,rounding_size=0.15",
                      linewidth=1.6, edgecolor="#c7d2fe", facecolor="#eef2ff", zorder=0)
ax.add_patch(band)
ax.text(14.0, 7.22, "IBM LinuxONE  (s390x)", ha="center", fontsize=11.5,
        weight="bold", color="#3730a3")
for i, (t, s) in enumerate([
        ("Telum on-chip AI", "NNPA · on-die, no GPU bus"),
        ("Pervasive encryption", "at rest & in transit · quantum-safe"),
        ("Container native", "Docker image, one-command deploy"),
        ("Data never leaves", "Granite runs locally, no API calls"),
]):
    y = 6.35 - i * 1.28
    box(12.6, y, 2.8, 1.0, t, s, fc="white", ec="#c7d2fe", fs=9.6, sfs=8, lw=1.1)

# ---------------- pipeline ----------------
box(0.35, 6.3, 2.0, 0.95, "Transfer", "initiated", fc="white")
arrow(2.38, 6.78, 2.72, 6.78)

box(2.75, 6.3, 2.15, 0.95, "Event stream", "real time", fc="#eff6ff", ec="#bfdbfe")
arrow(4.93, 6.78, 5.27, 6.78)

box(5.3, 6.05, 2.85, 1.45, "Real-time features",
    "behaviour · relationship · context\namount vs own history · velocity · hour\nrecipient novelty · channel",
    fc="#eff6ff", ec="#bfdbfe", fs=11.5, sfs=8.3)

# split to two models
arrow(6.72, 6.02, 6.72, 5.35)
ax.plot([6.72, 6.72], [5.35, 5.1], color="#94a3b8", lw=1.8, zorder=1)
ax.plot([4.85, 8.35], [5.1, 5.1], color="#94a3b8", lw=1.8, zorder=1)
arrow(4.85, 5.1, 4.85, 4.35)
arrow(8.35, 5.1, 8.35, 4.35)

box(3.6, 3.35, 2.5, 1.0, "LSTM", "7-step sequence window\nTensorFlow / Keras",
    fc="#f5f3ff", ec="#ddd6fe", fs=11.5, sfs=8.3)
box(7.1, 3.35, 2.5, 1.0, "XGBoost", "structured risk (GBDT)",
    fc="#f5f3ff", ec="#ddd6fe", fs=11.5, sfs=8.3)

# merge
ax.plot([4.85, 4.85], [3.35, 3.05], color="#94a3b8", lw=1.8, zorder=1)
ax.plot([8.35, 8.35], [3.35, 3.05], color="#94a3b8", lw=1.8, zorder=1)
ax.plot([4.85, 8.35], [3.05, 3.05], color="#94a3b8", lw=1.8, zorder=1)
arrow(6.6, 3.05, 6.6, 2.55)

box(5.15, 1.62, 2.9, 0.93, "Weighted fusion 0.85 / 0.15",
    "risk score + 9 reason codes  ·  ~22 ms", fc="#ecfdf5", ec="#a7f3d0", fs=11, sfs=8.3)

# decision branches
arrow(6.6, 1.6, 6.6, 1.3)
ax.plot([2.6, 10.6], [1.3, 1.3], color="#94a3b8", lw=1.8, zorder=1)
for x in (2.6, 6.6, 10.6):
    arrow(x, 1.3, x, 0.85)

box(1.55, 0.10, 2.1, 0.78, "APPROVE", "release", fc="#f0fdf4", ec="#bbf7d0",
    tc=GREEN, fs=11.5, sfs=8.5)
box(5.55, 0.10, 2.1, 0.78, "CONFIRM", "pause\nholder message + relative alert",
    fc="#fffbeb", ec="#fde68a", tc=AMBER, fs=11.5, sfs=8.2)
box(9.55, 0.10, 2.1, 0.78, "BLOCK", "hold + audit record", fc="#fef2f2", ec="#fecaca",
    tc=RED, fs=11.5, sfs=8.5)

# side annotations: explainer (async) + guardian
ax.annotate("", xy=(5.12, 2.02), xytext=(4.55, 2.02),
            arrowprops=dict(arrowstyle="-|>", color="#c4b5fd", lw=1.5))

ax.text(1.15, 2.62, "IBM Granite  (llama.cpp · local)", fontsize=9, color="#6d28d9",
        weight="bold", ha="left")
ax.text(1.15, 2.30, "explanation generated asynchronously —\nnever blocks the decision path",
        fontsize=8, color=DIM, ha="left", linespacing=1.35)

plt.tight_layout(pad=0.2)
plt.savefig(OUT, facecolor=BG, bbox_inches="tight")
print(f"已生成 {OUT}")
print(f"尺寸: {os.path.getsize(OUT)/1024:.0f} KB")
