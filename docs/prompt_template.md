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
 
+7. **Notion 整合與 AI 摘要**:
+    - **摘要功能**: 使用 `gpt-4o-mini` 對轉錄文字進行摘要。
+    - **Notion 紀錄**: 將「標題、完整內容、AI 摘要、時間、類型標籤」同步存入 Notion 資料庫。
+    - **資料庫欄位**: 需包含 `Name` (Title), `內容` (Text), `摘要` (Text), `時間` (Date), `類型` (Select)。
+8. **複合式回覆**: Bot 回覆訊息時需包含「辨識結果」與「摘要」。

