"""
AI 智能对话助手 —— 全栈最小可运行示例
=====================================
架构（理解全栈链路的关键）：

    浏览器 (前端 HTML/JS)
        │  HTTP /api/chat  (JSON + SSE 流式)
        ▼
    FastAPI 后端 (本文件)
        │  HTTP  /api/chat  (OpenAI 兼容协议)
        ▼
    Ollama 本地大模型  (默认 qwen2.5，跑在你自己的电脑上)

为什么要分层？
- 前端只管「展示 + 发请求」，不接触模型细节；
- 后端是「中枢」，负责把前端的对话历史翻译成模型能懂的格式，并做流式转发；
- 模型在本地运行，不需要任何 API Key，数据不出本机。
"""

import os
import json
import httpx
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, JSONResponse
from dotenv import load_dotenv  # 读取项目根目录下的 .env（可选）

load_dotenv()  # 若存在 .env 则加载其中的环境变量

app = FastAPI(title="AI 对话助手", version="1.0")

# ---------- 配置（可用环境变量覆盖，见 .env.example） ----------
# Ollama 默认监听本机 11434 端口；模型名可在 .env 里改
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen2.5:3b")


# ---------- 健康检查：前端加载时判断 Ollama 是否已就绪 ----------
@app.get("/api/health")
async def health():
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            models = [m["name"] for m in r.json().get("models", [])]
            return {"ok": True, "models": models, "model": MODEL_NAME}
    except Exception as e:
        # 503 表示服务暂时不可用（通常是 Ollama 没启动或没装）
        return JSONResponse(status_code=503, content={"ok": False, "error": str(e)})


# ---------- 核心接口：对话（SSE 流式返回，打字机效果） ----------
@app.post("/api/chat")
async def chat(request: Request):
    body = await request.json()
    # messages 格式：[{"role": "user"|"assistant", "content": "..."}]
    messages = body.get("messages", [])

    async def event_stream():
        try:
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream(
                    "POST",
                    f"{OLLAMA_BASE_URL}/api/chat",
                    json={"model": MODEL_NAME, "messages": messages, "stream": True},
                ) as resp:
                    # 关键修复：Ollama 对未知模型/参数错误会返回非 200（如 404），
                    # 且它不是流式 chunk，必须在这里显式捕获，否则前端只会收到空响应。
                    if resp.status_code != 200:
                        body = await resp.aread()
                        try:
                            err = json.loads(body).get("error", body.decode("utf-8", "ignore"))
                        except Exception:
                            err = body.decode("utf-8", "ignore")
                        yield f"data: {json.dumps({'error': f'Ollama 返回 {resp.status_code}：{err}'}, ensure_ascii=False)}\n\n"
                        yield "data: [DONE]\n\n"
                        return
                    async for line in resp.aiter_lines():
                        if not line:
                            continue
                        try:
                            chunk = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        # Ollama 也可能在流中返回错误对象，同样要显式暴露
                        if "error" in chunk:
                            yield f"data: {json.dumps({'error': str(chunk['error'])}, ensure_ascii=False)}\n\n"
                            yield "data: [DONE]\n\n"
                            return
                        # Ollama 每个 chunk 的 message.content 是一小段文本
                        if "message" in chunk and chunk["message"].get("content"):
                            text = chunk["message"]["content"]
                            # SSE 格式：以 "data: " 开头，两个换行结尾
                            yield f"data: {json.dumps({'content': text}, ensure_ascii=False)}\n\n"
                        if chunk.get("done"):
                            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ---------- 静态前端（放在最后挂载，避免覆盖上面的 /api 路由） ----------
app.mount("/", StaticFiles(directory="static", html=True), name="static")
