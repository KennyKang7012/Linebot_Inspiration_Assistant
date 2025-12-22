# Linebot Inspiration Assistant

一個基於 Python 3.11.7 實作的基礎 Line Echo Bot，使用現代化的 `uv` 與 FastAPI 進行開發。

## 🚀 快速開始

### 1. 前置作業
- 確保已安裝 [uv](https://github.com/astral-sh/uv)。
- 擁有一個 Line Messaging API 的 Channel（包含 Channel Secret 與 Channel Access Token）。

### 2. 環境設定
編輯專案根目錄下的 `.env` 檔案並填入您的憑證：
```text
LINE_CHANNEL_SECRET=您的_Channel_Secret
LINE_CHANNEL_ACCESS_TOKEN=您的_Channel_Access_Token
```

### 3. 安裝與執行
使用 `uv` 自動安裝依賴並啟動伺服器：
```bash
uv run uvicorn app:app --reload
```
伺服器將預設在 `http://127.0.0.1:8000` 啟動。

### 4. Webhook 設定
使用 `ngrok` 或其他工具將本地端服務暴露：
```bash
ngrok http 8000
```
將產生的 URL 後方加上 `/callback`（例如 `https://xxxx.ngrok-free.app/callback`），設定為 Line Developers Console 中的 Webhook URL。

## 📂 專案結構
- `app.py`: Line Echo Bot 核心邏輯 (FastAPI 實作)。
- `.env`: 環境變數設定。
- `pyproject.toml`: `uv` 專案配置與依賴 (指定 Python 3.11.7)。
- `docs/`: 開發文件與提示詞模板。
    - `prompt_template.md`: 專案設計提示詞。
    - `implementation_plan.md`: 實作計畫。
    - `walkthrough.md`: 詳細實作紀錄。
    - `task.md`: 任務追蹤清單。

## 🛠 使用技術
- **Language**: Python 3.11.7
- **Manager**: [uv](https://github.com/astral-sh/uv)
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **ASGI Server**: [Uvicorn](https://www.uvicorn.org/)
- **SDK**: [line-bot-sdk-python](https://github.com/line/line-bot-sdk-python)
