#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real-Time Transfer Scam Guard — API 服务

- SSE 实时推送每一笔转账的风险评分与三档决策
- 决策在授权路径内毫秒级返回；解释与家属通知在后台并行生成后补推
"""
import asyncio
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse

from .engine import RiskEngine
from .explain import Explainer
from .stream import StreamBuilder

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
STATIC = os.path.join(ROOT, "static")

app = FastAPI(title="Real-Time Transfer Scam Guard", version="1.0")

engine = RiskEngine(os.environ.get("MODEL_DIR", os.path.join(ROOT, "models")))
explainer = Explainer()
stream = StreamBuilder()
pool = ThreadPoolExecutor(max_workers=1)

state = {"speed": 5.0, "idx": 0, "started": None, "running": False}


class Hub:
    def __init__(self):
        self.clients = set()

    def add(self, q):
        self.clients.add(q)

    def drop(self, q):
        self.clients.discard(q)

    def publish(self, event, data):
        for q in list(self.clients):
            try:
                q.put_nowait((event, data))
            except Exception:
                self.clients.discard(q)


hub = Hub()


@app.on_event("startup")
def _load_models():
    t0 = time.time()
    engine.load()
    print(f"[startup] 融合模型加载完成 {time.time()-t0:.1f}s", flush=True)

    t1 = time.time()
    stream.prepare(profile=os.environ.get("STREAM_PROFILE", "demo"))
    print(f"[startup] 转账流就绪 {len(stream)} 笔 / {time.time()-t1:.1f}s", flush=True)

    try:
        explainer.load()
    except Exception as e:
        print(f"[startup] Granite 加载失败（解释降级）: {e}", flush=True)


@app.on_event("startup")
async def _spawn_ticker():
    asyncio.create_task(ticker())


@app.get("/", response_class=HTMLResponse)
def index():
    with open(os.path.join(STATIC, "index.html"), encoding="utf-8") as f:
        return f.read()


@app.get("/api/health")
def health():
    return {"running": state["running"],
            "engine_ready": engine.lstm is not None,
            "explainer_ready": explainer.ready,
            "stream_size": len(stream),
            "skipped_transactions": state.get("errors", 0),
            "state": state}


@app.get("/api/metrics")
def metrics():
    """训练时的离线评估结果，与 benchmark.py / pitch deck 中的数字同源。"""
    m = engine.meta or {}
    return {"offline": m.get("metrics"), "fusion": m.get("fusion"),
            "trained_at": m.get("trained_at"),
            "n_train": m.get("n_train"), "n_test": m.get("n_test"),
            "thresholds": {"block": engine.snapshot()["thresholds"]["block"],
                           "confirm": engine.snapshot()["thresholds"]["confirm"]}}


@app.get("/api/stats")
def stats():
    return {"engine": engine.snapshot(),
            "explainer": explainer.summary(),
            "stream": {"size": len(stream), "idx": state["idx"], "speed": state["speed"]}}


@app.post("/api/control")
def control(payload: dict):
    """控制交易流：running（开始/暂停）、reset（清零重来）、speed（速度）。"""
    if "speed" in payload:
        state["speed"] = max(0.5, min(40.0, float(payload["speed"])))
    if payload.get("reset"):
        state["idx"] = 0
        state["started"] = None
        state["running"] = False
        engine.reset()
    if "running" in payload:
        state["running"] = bool(payload["running"])
        if state["running"]:
            state["started"] = time.time()
    return {"ok": True, "state": state}


async def ticker():
    """全局节拍器：按 speed 推进转账流并广播。

    shortcut: 单笔失败就跳过并计数，不做重试；要保证连续可用时改成带退避的重试。
    """
    while True:
        if not state["running"]:
            await asyncio.sleep(0.2)
            continue
        try:
            if state["idx"] >= len(stream):
                state["idx"] = 0
                state["started"] = None

            ev = stream.events[state["idx"]]
            seq_raw, tab_raw = ev["_seq"], ev["_tab"]
            meta = {k: v for k, v in ev.items() if not k.startswith("_")}

            res = await asyncio.to_thread(engine.score, meta, seq_raw, tab_raw)
            txn_id = f"{meta['user']}-{meta['card']}-{meta['ts']}-{state['idx']}"

            hub.publish("txn", {"id": txn_id, "seq": state["idx"] + 1,
                                "total": len(stream), **meta, **res})

            if res["decision"] != "APPROVE" and not state.get("explain_busy"):
                state["explain_busy"] = True
                hub.publish("explain_pending", {
                    "id": txn_id,
                    "decision": res["decision"],
                    "amount": meta["amount"],
                    "guardian_notified": res["guardian_notified"],
                    "guardian_relation": res["guardian_relation"],
                    "guardian_limit": res["guardian_limit"],
                    "reason_codes": res["reason_codes"][:2],
                })
                asyncio.get_running_loop().run_in_executor(
                    pool, _explain_job, txn_id, meta, res)

            state["idx"] += 1
            if state["started"] is None:
                state["started"] = time.time()

        except Exception as e:                       # noqa: BLE001
            # 关键：异常绝不能中断节拍器，否则演示画面会静止不动
            state["errors"] = state.get("errors", 0) + 1
            print(f"[ticker] 跳过一笔：{type(e).__name__}: {e}", flush=True)
            state["idx"] += 1

        await asyncio.sleep(1.0 / max(state["speed"], 0.5))


def _fallback_text(meta, res):
    """Granite 未就绪时的兜底文案，保证演示界面永远有内容。"""
    top = res["reason_codes"][0]["en"].lower() if res["reason_codes"] else "unusual activity"
    return (f"This transfer was paused because of {top}. "
            f"If you are not sure about it, call your family before sending.")


def _explain_job(txn_id, meta, res):
    if not explainer.ready:
        hub.publish("explain", {"id": txn_id, "decision": res["decision"],
                                "guardian_relation": res.get("guardian_relation"),
                                "guardian_mask": res.get("guardian_mask"),
                                "guardian_limit": res.get("guardian_limit"),
                                "customer": _fallback_text(meta, res),
                                "guardian": "" if not res.get("guardian_notified")
                                            else "A transfer was paused. Please call and check.",
                                "ms": 0, "tokens": 0})
        state["explain_busy"] = False
        return
    try:
        out = explainer.explain(meta, res)
        hub.publish("explain", {"id": txn_id, "decision": res["decision"],
                                "guardian_relation": res.get("guardian_relation"),
                                "guardian_mask": res.get("guardian_mask"),
                                "guardian_limit": res.get("guardian_limit"),
                                **out})
    except Exception as e:
        hub.publish("explain", {"id": txn_id, "decision": res["decision"],
                                "customer": f"(failed: {e})", "guardian": "",
                                "guardian_relation": None, "ms": 0, "tokens": 0})
    finally:
        state["explain_busy"] = False


@app.get("/api/stream")
async def stream_sse():
    q = asyncio.Queue(maxsize=500)
    hub.add(q)

    async def gen():
        try:
            yield "event: hello\ndata: " + json.dumps(
                {"stream_size": len(stream), "speed": state["speed"]}) + "\n\n"
            while True:
                try:
                    event, data = await asyncio.wait_for(q.get(), timeout=15)
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
                    continue
                yield f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
        finally:
            hub.drop(q)

    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache",
                                      "X-Accel-Buffering": "no"})
