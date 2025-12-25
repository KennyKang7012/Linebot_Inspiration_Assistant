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
