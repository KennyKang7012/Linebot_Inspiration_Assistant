# Line Bot 專案提示詞模板

## 角色
你是一位精通 Python 開發的專家，擅長使用 Line Messaging API 與現代 Python 工具。

## 任務
依照以下規格初始化一個 Line Echo Bot 專案：
- **語言**: Python 3.11.7
- **套件管理工具**: `uv`
- **框架**: FastAPI
- **伺服器**: Uvicorn
- **API**: Line Messaging API SDK for Python (v3) & OpenAI Whisper API

## 專案結構
```text
.
├── .env                  # 環境變數 (Channel Secret, Access Token)
├── pyproject.toml        # UV 專案配置
├── app.py                # 主程式入口 (FastAPI)
├── requirements.txt      # (選配) 導出的依賴清單
└── docs/
    └── prompt_template.md # 本文件
```

## 核心需求
1.  **環境設定**: 使用 `uv init` 建立專案，並指定 Python 3.11.7。
2.  **依賴套件**: 新增 `line-bot-sdk`, `fastapi`, `uvicorn`, `python-dotenv` 以及 `openai`。
3.  **回應邏輯**: 實作基礎的 Webhook，接收文字訊息並回傳相同的內容。
4.  **資訊安全**: 包含來自 Line 請求的訊息簽章驗證（FastAPI Middleware 或 Dependency Injection 方式）。
5.  **環境變數**:
    - `LINE_CHANNEL_SECRET`
    - `LINE_CHANNEL_ACCESS_TOKEN`
    - `OPENAI_API_KEY`
6.  **語音轉文字**: 實作 `AudioMessageContent` 處理器：
    - 使用 `MessagingApiBlob` 下載語音內容。
    - 使用 OpenAI Whisper 進行轉錄，強制設定 `language="zh"` 並加入「引導提示詞」以優化繁體中文輸出。
    - 直接回傳轉錄後的純文字內容。

## 實作細節
- 提供清晰的 `README.md` 及安裝步驟。
- 確保程式碼符合 PEP 8 標準。
- 使用 `python-dotenv` 載入環境變數。

## Whisper API 設定 (繁體中文優化)
為了確保辨識結果為繁體中文，在呼叫 OpenAI API 時需使用以下參數：
- **模型**: `whisper-1`
- **語言**: `zh`
- **提示詞 (Prompt)**: `以下是繁體中文的對話內容：`
 
7. **Notion 整合與 AI 摘要**:
    - **摘要功能**: 使用 `gpt-4o-mini` 對文字或轉錄文字進行摘要。
    - **Notion 紀錄**: 將「標題、完整內容、AI 摘要、時間、類型標籤」同步存入 Notion 資料庫。
    - **Notion 存檔優化**: 原始內容應寫入 Notion 的「頁面內容 (Children Blocks)」以避開屬性欄位 2000 字元限制。
    - **資料庫欄位**: 屬性欄位需包含 `Name` (Title), `摘要` (Text), `時間` (Date), `類型` (Select)。
8. **指令支援 (文字模式)**:
    - 偵測以 `/a` 開頭的訊息。
    - 若符合指令，自動總結內容、存入 Notion 並設類型為 `文字摘要`。
9. **複合式回覆**: Bot 回覆訊息時需包含「辨識結果（或指令內容）」與「摘要」。
10. **圖片筆記功能**:
    - 整合 Google Drive API (OAuth 2.0) 上傳圖片。
    - 使用 OpenAI Vision API (gpt-4o-mini) 辨識圖片內容。
    - 將圖片連結與摘要存入 Notion,類型設為 `圖片筆記`。
11. **網址爬取與摘要**:
    - 自動偵測訊息中的網址 (使用正則表達式)。
    - 使用 `trafilatura` 擷取網頁內容。
    - 將網址、內容與摘要存入 Notion,類型設為 `網頁筆記`。
12. **Apify 爬蟲增強** (可選):
    - 整合 `apify-client` 以支援進階網頁爬取。
    - **Facebook 貼文**: 使用 `apify/facebook-posts-scraper` 爬取公開貼文,提取發布者、時間與內容。
    - **一般網頁**: 使用 `apify/website-content-crawler` 處理需要 JavaScript 渲染的動態網頁。
    - **回退機制**: Apify 失敗時自動使用 trafilatura。
    - 將 Facebook 貼文存為 `FB 筆記`,一般網頁存為 `網頁筆記`。
13. **使用者權限控管**:
    - 從環境變數 `ALLOWED_LINE_ID` 讀取白名單。
    - 在所有訊息處理器中檢查 `event.source.user_id` 是否符合白名單。
    - 未授權使用者收到「抱歉,您沒有權限使用此服務。」訊息。
14. **Line ID 記錄**:
    - 在所有 Notion 紀錄中加入 `Line_ID` 欄位。
    - 從 `event.source.user_id` 擷取並儲存使用者識別碼。

## 環境變數完整清單
```text
LINE_CHANNEL_SECRET=...
LINE_CHANNEL_ACCESS_TOKEN=...
OPENAI_API_KEY=...
NOTION_API_KEY=...
NOTION_DATABASE_ID=...
GOOGLE_DRIVE_FOLDER_ID=...
ALLOWED_LINE_ID=...
APIFY_API_KEY=...  # 可選,用於進階網頁爬取
```
