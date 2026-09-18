# 小K AI · 本地大模型对话助手

> 一个**从零可跑通**的 AI 全栈最小示例：浏览器聊天界面 → FastAPI 后端 → 本地 Ollama 大模型。
> **不需要任何 API Key，不联网，数据全部留在你自己的电脑上。**

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?logo=fastapi)
![Ollama](https://img.shields.io/badge/Ollama-local-000000)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 目录

- [一、这个项目是什么](#一这个项目是什么)
- [二、全栈架构（先看懂这张图）](#二全栈架构先看懂这张图)
- [三、快速开始（3 步跑起来）](#三快速开始3-步跑起来)
- [四、配置说明](#四配置说明)
- [五、项目结构](#五项目结构)
- [六、接口文档](#六接口文档)
- [七、核心原理讲解](#七核心原理讲解)
- [八、常见问题排查](#八常见问题排查)
- [九、还能怎么扩展](#九还能怎么扩展)
- [许可](#许可)

---

## 一、这个项目是什么

<img width="2874" height="1559" alt="屏幕截图 2026-09-18 222109" src="https://github.com/user-attachments/assets/d44ea056-f4cb-45d9-8922-b00a63231322" />

一个带 Web 界面的 AI 聊天助手。你在浏览器里输入问题，页面会把**完整对话历史**发给后端，后端转交给本机运行的开源大模型（默认 `qwen2.5:3b`），模型逐字生成回答，再以**流式（打字机效果）**回传并渲染成气泡。

**适合谁：**

- 想理解「AI 应用到底是怎么串起来的」的初学者（前端 / 后端 / 模型三层各负责什么）
- 想做一个完全离线、免费、隐私安全的私人聊天助手
- 想以此为骨架继续做 RAG 知识库、Agent 等进阶项目

**已实现的功能：**

| 功能 | 说明 |
| --- | --- |
| 流式打字机输出 | 基于 SSE，模型生成一个 token 就立刻显示一个 |
| 多轮上下文记忆 | 每轮把完整 `messages` 历史发给模型，能接得上上下文 |
| 连接状态指示 | 顶栏圆点实时显示「已连接 / Ollama 未就绪 / 后端未启动」 |
| 代码块高亮显示 | AI 回答里的 ` ``` ` 代码块渲染为深色等宽区块 |
| 空状态引导 | 首屏提供 4 个示例问题，点击即发送 |
| 专属品牌图标 | 蓝紫渐变对话气泡 SVG，内联为页面 logo 与浏览器 favicon |
| 响应式布局 | 窄屏（手机）自动适配 |

---

## 二、全栈架构（先看懂这张图）

```
┌──────────────────────┐   HTTP POST /api/chat   ┌────────────────────┐   HTTP 转发      ┌──────────────────────┐
│      前端（浏览器）     │ ──────────────────────▶ │   后端（FastAPI）    │ ────────────────▶ │   Ollama 本地大模型    │
│  static/index.html   │ ◀────────────────────── │      main.py       │ ◀──────────────── │   qwen2.5:3b 等       │
│  原生 HTML / CSS / JS │   SSE 流式（逐 token）    │   对话中枢 · 转发    │   逐 token 返回     │   跑在你自己的电脑上    │
└──────────────────────┘                          └────────────────────┘                  └──────────────────────┘
        展示层                                          逻辑 / 接口层                              模型 / 推理层
```

**三层各自干什么：**

- **前端（展示层）**：只负责「收集输入 → 发请求 → 把返回渲染成气泡」。它完全不知道模型是什么、在哪跑。
- **后端（逻辑层）**：全栈的核心枢纽。把前端送来的对话历史翻译成模型能懂的格式，调用模型 API，再把模型**流式返回**的每个 token 原样转发给前端。同时负责健康检查、错误处理、鉴权/日志（本项目只实现了前两个）。
- **模型（推理层）**：Ollama 在本地加载开源大模型权重，真正做「理解 + 生成」。

> **为什么不能让浏览器直接调模型？**
> 因为浏览器无法直接、安全地驱动本地进程；而且对话上下文维护、错误兜底、未来的鉴权/限流/计费都需要一个可信的中间层。后端就是连接「人」和「模型」的那座桥。

---

## 三、快速开始（3 步跑起来）

### 前置条件

- **Python 3.9+**（推荐 3.10 及以上）— [下载地址](https://www.python.org/downloads/)
- **Ollama** — 本地大模型运行器，[官网下载](https://ollama.com)，Windows / macOS / Linux 均支持，按向导安装即可

### 第 1 步：拉取模型

安装完 Ollama 后它会自动在后台运行（监听 `http://localhost:11434`）。打开终端执行：

```bash
ollama pull qwen2.5:3b
```

> 约 2GB，中文友好、速度快，是学习与低配机器的首选。
> 想要更好的效果可以拉 `ollama pull qwen2.5:latest`（约 4.7GB，更吃内存）。

### 第 2 步：安装依赖并启动

```bash
git clone https://github.com/yangran-coder/ai-chatbot.git
cd ai-chatbot
```

**Windows（PowerShell / Git Bash）：**

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**macOS / Linux：**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

> 看到 `Uvicorn running on http://127.0.0.1:8000` 即启动成功。
> 开发期建议加 `--reload`（改代码自动重启）；生产部署去掉它。

### 第 3 步：打开浏览器

访问 **http://localhost:8000**

右上角应显示绿色的「已连接 · qwen2.5:3b」，此时直接输入即可对话。首次提问会触发模型加载，可能需要等十几秒，之后就快了。

---

## 四、配置说明

项目根目录提供了 `.env.example`，**复制为 `.env` 即可生效**（`.env` 已被 `.gitignore` 排除，不会误传）：

```bash
cp .env.example .env      # macOS / Linux
copy .env.example .env    # Windows
```

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama 服务地址，一般不用改 |
| `MODEL_NAME` | `qwen2.5:3b` | 使用的模型名，**必须与 `ollama list` 显示的一致** |

改完 `.env` 后**重启后端**生效。

查看本机已装模型：

```bash
ollama list
```

---

## 五、项目结构

```
ai-chatbot/
├── main.py              # 后端：FastAPI 服务，健康检查 + 对话流式转发 + 静态文件托管
├── requirements.txt     # Python 依赖清单
├── .env.example         # 配置模板（复制为 .env 使用）
├── .gitignore           # 排除 .venv / __pycache__ / .env
├── README.md            # 你正在看的这份文档
└── static/
    └── index.html       # 前端：单文件，含 HTML + CSS + JS，零构建
```

**只有 2 个核心源文件**，非常适合逐行读完来理解全栈。

---

## 六、接口文档

后端启动后自带交互式文档：http://localhost:8000/docs （FastAPI 自动生成）

### `GET /api/health` — 健康检查

前端加载时调用，用于判断 Ollama 是否就绪。

```jsonc
// 200 正常
{ "ok": true, "models": ["qwen2.5:3b", "bge-m3:latest"], "model": "qwen2.5:3b" }

// 503 Ollama 未启动 / 未安装
{ "ok": false, "error": "..." }
```

### `POST /api/chat` — 对话（SSE 流式）

**请求体：**

```json
{
  "messages": [
    { "role": "user", "content": "用一句话介绍你自己" },
    { "role": "assistant", "content": "我是小K..." },
    { "role": "user", "content": "再说详细点" }
  ]
}
```

> `messages` 是**完整对话历史**，按时间顺序排列。多轮记忆就是靠每次都把全部历史传过去实现的。

**响应（SSE 流，`Content-Type: text/event-stream`）：**

```
data: {"content": "我是"}

data: {"content": "一个"}

data: {"content": "本地"}

data: [DONE]

```

出错时返回：

```
data: {"error": "Ollama 返回 404：model 'xxx' not found"}

data: [DONE]
```

用 curl 测试（ASCII 内容即可，中文在 Git Bash 下可能被 GBK 编码影响）：

```bash
curl -N -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"hello"}]}'
```

---

## 七、核心原理讲解

### 1. 流式输出是怎么做到的（SSE）

后端用 `httpx` 以 `stream=True` 请求 Ollama，边收边把每个 token 包成 SSE 格式 `data: {...}\n\n` 推给前端；前端用 `fetch` 拿到 `ReadableStream`，用 `TextDecoder` 逐段解码，按 `\n\n` 切包后追加到气泡上——这就是打字机效果。

```python
# main.py
async with client.stream("POST", f"{OLLAMA_BASE_URL}/api/chat", json={...}) as resp:
    async for line in resp.aiter_lines():
        chunk = json.loads(line)
        if "message" in chunk and chunk["message"].get("content"):
            yield f"data: {json.dumps({'content': text}, ensure_ascii=False)}\n\n"
        if chunk.get("done"):
            yield "data: [DONE]\n\n"
```

```javascript
// static/index.html
const reader = resp.body.getReader();
while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  buf += decoder.decode(value, { stream: true });
  const parts = buf.split("\n\n"); buf = parts.pop();
  for (const part of parts) {
    if (!part.startsWith("data: ")) continue;
    const json = JSON.parse(part.slice(6).trim());
    acc += json.content;              // 累加
    bubble.textContent = acc;         // 实时渲染
  }
}
```

### 2. 为什么 AI 能记住前面聊了什么

模型本身是**无状态**的——它只看到你这一次传进来的 `messages`。所以前端维护一个全局 `messages` 数组，每轮对话都把「之前所有轮次 + 本次提问」一起发过去，模型才表现出「有记忆」。

### 3. 前端为什么不用 npm / 打包

后端最后一行把 `static/` 目录整个托管成了网站根：

```python
app.mount("/", StaticFiles(directory="static", html=True), name="static")
```

所以 `index.html` 是纯原生 HTML/CSS/JS 单文件，**改完刷新浏览器就生效，零构建、零依赖**。对理解全栈链路非常友好。

> 注意：这行必须放在所有 `/api` 路由之后，否则会覆盖 API 路径。

### 4. 错误处理（本项目踩过的坑）

Ollama 在「模型名不存在」时会返回 **404 且不是流式响应**。如果后端不显式判断状态码，前端就会收到一段空响应——表现为「发消息没反应，但终端显示 200 OK」，极难排查。本项目已在 `event_stream()` 中显式捕获非 200 状态和流中的错误对象，并转成 `{"error": ...}` 推送给前端显示成红色气泡。

---

## 八、常见问题排查

| 现象 | 原因 | 解决办法 |
| --- | --- | --- |
| 右上角「Ollama 未就绪」 | Ollama 没启动，或没拉模型 | 终端执行 `ollama list`，确认有输出；确认托盘里 Ollama 在运行 |
| 发消息没反应、终端显示 200 | 通常是 `MODEL_NAME` 与实际模型名不一致 | `ollama list` 核对，改 `.env` 的 `MODEL_NAME` 后重启 |
| 报错 `ModuleNotFoundError: No module named 'dotenv'` | 依赖没装全 | `pip install -r requirements.txt`（已包含 `python-dotenv`） |
| `Address already in use` / 端口被占用 | 8000 端口被别的进程占用 | 换端口：`uvicorn main:app --port 8001` |
| 首次提问特别慢 | 模型首次加载进显存/内存 | 正常现象，第二次起会快很多 |
| 回答质量一般 | 3b 是小模型 | 换更大的模型，如 `ollama pull qwen2.5:latest` |
| 修改了 `.env` 没生效 | 环境变量只在启动时读取 | 重启后端服务 |
| 内存吃紧 / 卡顿 | 模型太大 | 改用 `qwen2.5:3b`，或关闭其他占用内存的程序 |

---

## 九、还能怎么扩展

按投入产出比排序：

1. **多模型下拉切换** — 后端加一个代理 `/api/tags`，前端做下拉框选择模型。
2. **对话持久化** — 把 `messages` 存到 SQLite / JSON 文件，刷新页面不丢上下文，并支持历史会话列表。
3. **升级为 RAG 知识库**（最有价值）— 把自己的笔记/PDF 切块 → 向量化 → 检索相关片段 → 拼进 prompt 再问模型。你本机的 `bge-m3` 正是用来做向量化的。
4. **接云端大模型** — 把 `OLLAMA_BASE_URL` 换成 DeepSeek / OpenAI 的兼容端点，在 `.env` 里配 API Key（**务必用环境变量，不要硬编码进代码**）。
5. **加停止生成按钮** — 前端用 `AbortController` 中断 `fetch`，后端感知断开。

---

## 许可

[MIT](https://opensource.org/licenses/MIT) — 自由使用、修改与分发。

如果这个项目帮你理解了 AI 全栈开发，欢迎点个 ⭐ Star。
