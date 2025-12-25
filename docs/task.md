# 任務：使用 UV 的 Line Echo Bot

- [x] 初始化專案結構 `[x]`
    - [x] 建立 `docs` 目錄
    - [x] 建立 `task.md`
- [x] 建立開發文件 `[x]`
    - [x] 建立 `docs/prompt_template.md` (繁體中文)
- [x] 專案設定 `[x]`
    - [x] 初始化 `uv` 專案 (Python 3.11.7)
    - [x] 新增依賴套件 (`line-bot-sdk`, `fastapi`, `uvicorn`, `python-dotenv`)
- [x] 實作 Line Echo Bot `[x]`
    - [x] 建立 `.env` 存放憑證
    - [x] 將 `app.py` 由 Flask 改為 FastAPI
- [x] 驗證 `[x]`
    - [x] 使用 Mock 資料或 ngrok 進行本地測試
    - [x] 建立 `walkthrough.md`

---

# SSL 憑證錯誤修復任務 (新增於 2025-12-25)

- [x] 研究 SSL 憑證驗證錯誤 (SSLCertVerificationError)
- [x] 確定最佳修復方案 (使用 certifi 設定環境變數)
- [x] 實作修復程式碼 (修改 app.py)
- [x] 驗證修復結果 (成功在本地端重啟並測試)
- [x] 將 .env 排除於版本控制 (已加入 .gitignore 並移出 git index)

---

# 語音轉文字任務 (OpenAI Whisper) (新增於 2025-12-25)

- [x] 新增 `openai` 依賴 <!-- id: 8 -->
- [x] 在 `.env` 中設定 OpenAI API Key <!-- id: 9 -->
- [x] 更新 `app.py` 以處理語音訊息 <!-- id: 10 -->
    - [x] 匯入 `linebot.v3` 的必要類別 <!-- id: 11 -->
    - [x] 實作 `AudioMessageContent` 處理器 <!-- id: 12 -->
    - [x] 使用 `MessagingApiBlob` 下載語音內容 <!-- id: 13 -->
    - [x] 整合 OpenAI Whisper API <!-- id: 14 -->
- [x] 驗證功能是否正常 <!-- id: 15 -->
