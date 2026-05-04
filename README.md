# 手相解读 ToC Web MVP

无需登录注册的手相解读 Web 首版。用户拍照或上传手掌图片后，后端创建分析任务，AI Provider 输出结构化 JSON，前端用固定的 `palm_vintage_bw_v1` 模板渲染为极简复古中文报告页。

## 项目结构

```text
backend/   FastAPI API、上传校验、7 天本地留存、AI Provider 适配层
frontend/  Vue3 + Vite 拍照上传页、任务轮询页、公开分享结果页
```

## 本地启动

后端：

```bash
cd backend
uv sync
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

前端：

```bash
cd frontend
npm install
npm run dev
```

访问 `http://127.0.0.1:5173`。

## AI 接入

默认 `PALM_AI_PROVIDER=mock`，用于完整跑通产品链路，不产生模型调用费用。切换真实多模态模型时复制 `backend/.env.example` 为 `backend/.env`，并配置：

```env
PALM_AI_PROVIDER=openai_compatible
PALM_AI_API_KEY=你的模型Key
PALM_AI_BASE_URL=https://api.openai.com/v1
PALM_AI_MODEL=gpt-4o-mini
```

真实 Provider 使用 OpenAI-compatible `/chat/completions` 协议，要求模型只返回 JSON，不返回 HTML/CSS。前端不会执行 AI 生成的页面代码，只把结构化字段渲染进固定模板。

## API

- `POST /api/v1/palm-readings`：上传 `image` 文件，支持 `jpg/png/webp`，默认最大 `10MB`。
- `GET /api/v1/palm-readings/{readingId}`：查询任务状态与结果。
- `GET /api/v1/public-readings/{shareToken}`：访问公开分享结果。

图片和结果本地保存在 `backend/data`，默认 7 天过期。首版不做登录、后台管理和支付逻辑，但记录了 `tier=free`、`paymentStatus=free`，方便后续扩展收费。

## 验证

```bash
cd backend
uv run pytest -q

cd frontend
npm run build
```
