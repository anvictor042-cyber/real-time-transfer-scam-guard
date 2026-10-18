#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real-Time Transfer Scam Guard — 双受众实时解释

与常见反欺诈系统不同，本模块的 LLM 输出对象不是风控分析师，而是：
  ① 当事老人 —— 用听得懂的话劝阻
  ② 关联家属 —— 一条可执行的提醒

工程要点：解释与决策解耦。决策毫秒级返回；解释在后台线程池生成，
不阻塞授权路径。这是"实时"与"可解释"能同时成立的前提。
"""
import os
import threading
import time

def _granite_path():
    """Granite GGUF：环境变量 → IBM 镜像内置位置 → 仓库 models/。"""
    import os as _os
    for c in (_os.environ.get("GRANITE_PATH"),
              "/home/ibm-user/granite-4.0-h-350m-base-be.f16.gguf",
              _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),
                            "models", "granite-4.0-h-350m-base-be.f16.gguf")):
        if c and _os.path.exists(c):
            return c
    return ""


MODEL_PATH = _granite_path()

# ---------------------------------------------------------------------------
# ① 面向老人的通俗提示（少样本续写；Granite base 无 chat template）
# ---------------------------------------------------------------------------
_CUSTOMER_HEAD = """You are a calm banking assistant. Explain the pause in one plain sentence an older person can act on.

Transfer:
$340, online, 01:00, new recipient, two transfers in ten minutes
Risk 0.62 (needs confirmation)
Message: We paused this payment because it is larger than usual and goes to someone new. Please check with your family before it is sent.

Transfer:
$2,400, online, 02:00, first time to this recipient, six transfers in four minutes
Risk 0.96 (high)
Message: We stopped this payment. Six transfers went out in four minutes and this one is far larger than usual. Please call us before sending any money.
"""

# ---------------------------------------------------------------------------
# ② 面向家属的通知
# ---------------------------------------------------------------------------
_GUARDIAN_HEAD = """You are a bank alerting a family member about a paused transfer.

Transfer:
$340, online, 01:00, new recipient
Risk 0.62 (needs confirmation)
Alert: A $340 transfer from your parent was paused. Please call them before it is released.

Transfer:
$2,400, online, 02:00, first time to this recipient, six transfers in four minutes
Risk 0.96 (high)
Alert: A $2,400 transfer from your parent was stopped. Please call them now.
"""


def _describe(txn, result):
    """把结构化信号压成一句客观描述，喂给模型"""
    bits = [f"${txn['amount']:.2f}", txn.get("channel", "transfer").replace(" Transaction", "").lower()]
    hour = int(txn.get("hour", 0))
    bits.append(f"{hour:02d}:00")
    codes = {c["code"] for c in result.get("reason_codes", [])}
    if "R01" in codes or "R09" in codes:
        bits.append("amount far above usual")
    if "R02" in codes:
        bits.append("several transfers in a very short window")
    if "R03" in codes:
        bits.append("unusual hour")
    if "R06" in codes:
        bits.append("first time to this recipient")
    if "R05" in codes:
        bits.append("after a failed attempt")
    return ", ".join(bits)


# 350M 模型会直接抄示例。生成结果必须和决策自洽，否则用模板兜底，
# 绝不能让界面上出现「BLOCK：这笔转账看起来正常，会放行」这种矛盾。
_REASSURING = ("normal", "go through", "goes through", "nothing unusual",
               "no action", "usual payment", "looks fine")

_FALLBACK = {
    "CONFIRM": ("We paused this payment because it is larger than usual or goes to "
                "someone new. Please check with your family before it is sent.",
                "A transfer from your parent was paused. Please call them before it is released."),
    "BLOCK": ("We stopped this payment. It is far larger than usual, and the recent "
              "transfers on this account are unusual. Please call us before sending any money.",
              "A transfer from your parent was stopped. Please call them now."),
}


def _consistent(text, decision):
    """文案是否与决策一致：不能在被拦截时告诉用户没事。"""
    if not text or len(text.strip()) < 12:
        return False
    low = text.lower()
    if decision in ("CONFIRM", "BLOCK"):
        if any(w in low for w in _REASSURING):
            return False
    return True


def build_customer_prompt(txn, result):
    level = "high" if result["risk"] >= 0.9 else "needs confirmation"
    return (f"{_CUSTOMER_HEAD}\n"
            f"Transfer:\n{_describe(txn, result)}\n"
            f"Risk {result['risk']:.2f} ({level})\n"
            f"Message:")


def build_guardian_prompt(txn, result):
    level = "high" if result["risk"] >= 0.9 else "needs confirmation"
    return (f"{_GUARDIAN_HEAD}\n"
            f"Transfer:\n{_describe(txn, result)}\n"
            f"Risk {result['risk']:.2f} ({level})\n"
            f"Alert:")


class Explainer:
    def __init__(self, model_path=MODEL_PATH):
        self.model_path = model_path
        self.llm = None
        self._lock = threading.Lock()
        self.ready = False
        self.stats = {"generated": 0, "total_ms": 0.0, "total_tokens": 0}
        self._stats_lock = threading.Lock()

    def load(self):
        from llama_cpp import Llama
        t0 = time.time()
        cpu = os.cpu_count() or 3
        # 只占 2 个线程，给决策路径留出 CPU。3 vCPU 上这是有意的取舍：
        # 解释可以慢，决策不能慢。
        self.llm = Llama(
            model_path=self.model_path,
            n_ctx=2048, n_batch=256,
            n_threads=2,
            verbose=False,
        )
        self.ready = True
        print(f"[explainer] Granite 就绪 {time.time()-t0:.1f}s", flush=True)
        return self

    def _gen(self, prompt, max_tokens=48):
        with self._lock:                       # llama.cpp 单实例，串行
            out = self.llm.create_completion(
                prompt=prompt, temperature=0.0, max_tokens=max_tokens,
                stop=["\n\n", "\nTransfer:", "\nMessage:", "\nAlert:"],
                stream=False,
            )
        return (out["choices"][0]["text"].strip(), out["usage"]["completion_tokens"])

    def explain(self, txn, result):
        """一次调用生成两个受众的文案（调用方放线程池执行）"""
        if not self.ready:
            return {"customer": "(explainer not ready)", "guardian": "", "ms": 0, "tokens": 0}

        t0 = time.time()
        decision = result.get("decision", "CONFIRM")
        fb_c, fb_g = _FALLBACK.get(decision, ("", ""))

        customer, t1 = self._gen(build_customer_prompt(txn, result), 44)
        if not _consistent(customer, decision):
            customer = fb_c

        guardian, t2 = ("", 0)
        if result.get("guardian_notified"):
            guardian, t2 = self._gen(build_guardian_prompt(txn, result), 40)
            if not _consistent(guardian, decision):
                guardian = fb_g
        ms = (time.time() - t0) * 1000

        with self._stats_lock:
            self.stats["generated"] += 1
            self.stats["total_ms"] += ms
            self.stats["total_tokens"] += t1 + t2

        return {"customer": customer, "guardian": guardian,
                "ms": round(ms, 1), "tokens": t1 + t2}

    def summary(self):
        with self._stats_lock:
            s = dict(self.stats)
        n = max(s["generated"], 1)
        return {"generated": s["generated"],
                "avg_ms": round(s["total_ms"] / n, 1) if s["generated"] else 0,
                "avg_tokens": round(s["total_tokens"] / n, 1) if s["generated"] else 0}
