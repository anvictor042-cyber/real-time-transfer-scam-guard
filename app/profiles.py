#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real-Time Transfer Scam Guard — 合成客户画像层

说明（诚实标注）：公开交易语料不含年龄/亲属字段。为了演示「老年人诈骗防护」
这一产品场景，我们在**不修改交易与标签**的前提下，为每个 (user, card) 叠加
一层**合成画像**（年龄带、守护额度、关联家属、数字活跃度）。
这与 Design Doc 中 "in-house synthetic transfer and device events" 的表述一致。

⚠️ 这些字段是场景参数，不参与欺诈标签，也不影响模型训练的公平性判断。
"""
import hashlib

# 年龄带权重：让大多数账户落在「易受骗人群」
_AGE_BANDS = [("65+", 0.55), ("55-64", 0.25), ("under-55", 0.20)]
_GUARDIAN_RELATIONS = ["daughter", "son", "niece", "nephew", "spouse"]


def _h(user, card, salt=""):
    """稳定哈希，保证同一账户每次运行拿到同一画像"""
    raw = f"{user}:{card}:{salt}".encode()
    return int(hashlib.sha256(raw).hexdigest()[:12], 16)


def profile_for(user, card):
    """返回该账户的合成画像（确定性，可复现）"""
    h = _h(user, card)
    pick = (h % 1000) / 1000.0

    age_band = "65+"
    acc = 0.0
    for band, w in _AGE_BANDS:
        acc += w
        if pick < acc:
            age_band = band
            break

    relation = _GUARDIAN_RELATIONS[(h >> 8) % len(_GUARDIAN_RELATIONS)]

    # 守护额度：65+ 人群默认更低（更容易触发 Confirm + 家属通知）
    # 额度参照「该人群单笔可承受损失」，而非账户余额
    if age_band == "65+":
        limit = 50 + (h >> 4) % 120          # $50 – $170
    elif age_band == "55-64":
        limit = 150 + (h >> 4) % 250         # $150 – $400
    else:
        limit = 400 + (h >> 4) % 1100        # $400 – $1,500

    digital = ["low", "medium", "high"][(h >> 12) % 3]

    return {
        "account": f"U{user}/C{card}",
        "age_band": age_band,
        "guardian_relation": relation,
        "guardian_mask": f"+86 138****{(h >> 16) % 10000:04d}",
        "guardian_limit": int(limit),
        "digital_activity": digital,
        "protected": age_band in ("65+", "55-64"),
    }
