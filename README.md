# Linebot Inspiration Assistant

一個基於 Python 3.11.7 實作的靈感助手 Line Bot，具備語音辨識、AI 摘要與 Notion 自動同步功能。

## ✨ 功能亮點

- **語音轉文字**:整合 OpenAI Whisper API,自動將語音訊息轉換為繁體中文。
- **AI 自動摘要**:使用 GPT-4o-mini 對長文本或語音內容進行重點擷取。
- **Notion 雲端同步**:自動將原始內容與 AI 摘要同步至 Notion 資料庫。
- **文字摘要指令**:支援在 LINE 中輸入 `/a` 指令快速總結文字資訊。
- **圖片筆記**:自動辨識圖片內容並上傳至 Google Drive,同步至 Notion。
- **網址爬取**:自動擷取網頁內容並生成摘要,支援 Facebook 貼文與一般網頁。
- **Apify 爬蟲增強**:整合 Apify 平台,支援 JavaScript 渲染的動態網頁與 Facebook 公開貼文。
- **長文本優化**:自動處理 Notion 2000 字元限制,將長內容完整寫入頁面正文區。

## 🚀 快速開始

### 1. 前置作業
- 確保已安裝 [uv](https://github.com/astral-sh/uv)。
- 擁有 Line Messaging API 憑證 (Channel Secret, Access Token)。
- 擁有 OpenAI API Key。
- 擁有 Notion API Key 與目標 Database ID。
- 擁有 Google Drive API 憑證 (credentials.json)。
- (可選) 擁有 Apify API Token 以啟用進階爬蟲功能。

### 2. 環境設定
編輯專案根目錄下的 `.env` 檔案:
```text
LINE_CHANNEL_SECRET=...
LINE_CHANNEL_ACCESS_TOKEN=...
OPENAI_API_KEY=...
NOTION_API_KEY=...
NOTION_DATABASE_ID=...
GOOGLE_DRIVE_FOLDER_ID=...
ALLOWED_LINE_ID=...
APIPY_API_KEY=...  # 可選,用於進階網頁爬取
```

### 3. 使用方法
- **語音筆記**:直接對 Bot 傳送語音訊息,系統會自動辨識、摘要並存入 Notion。
- **圖片筆記**:傳送圖片給 Bot,系統會自動辨識內容、上傳至 Google Drive 並存入 Notion。
- **文字摘要**:傳送 `/a [要摘要的文字]`,系統會回傳摘要並存入 Notion。
- **網址爬取**:直接貼上網址 (支援 Facebook 貼文與一般網頁),系統會自動爬取、摘要並存入 Notion。

### 4. 啟動服務

本專案提供兩種啟動方式，您可以依據開發環境需求選擇：

#### 方法 A：手動啟動 (標準方式)
適合已有固定 Webhook URL 或使用其他轉發工具的使用者：
```bash
uv run uvicorn app:app --reload
```
伺服器將在 `http://127.0.0.1:8000` 啟動。啟動後需自行處理 Webhook 穿透。

#### 方法 B：自動化啟動 (推薦用於本地開發)
適合需要自動建立 ngrok 通道的開發環境，會自動顯示 Webhook URL：
```bash
uv run run_with_ngrok.py
```

## 📂 專案結構
- `app.py`: 核心邏輯 (FastAPI)。
- `run_with_ngrok.py`: 自動化 ngrok 通道與伺服器啟動腳本。
- `docs/`:
    - `prompt_template.md`: 提示詞規格模板。
    - `implementation_plan.md`: 實作計畫與變更細節。
    - `walkthrough.md`: 成果展示與詳細實作紀錄。
    - `task.md`: 任務追蹤清單。
    - `troubleshooting.md`: 疑難排解與常見問題紀錄。

## 🛠 使用技術
- **Language**: Python 3.11.7
- **AI Platform**: OpenAI (Whisper, GPT-4o-mini)
- **Database**: Notion API
- **Manager**: [uv](https://github.com/astral-sh/uv)
- **Framework**: FastAPI + Uvicorn
