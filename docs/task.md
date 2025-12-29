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

---

# Notion 整合任務 (新增於 2025-12-25)

- [x] 新增 `notion-client` 依賴
- [x] 在 `.env` 中設定 Notion API Key 和 Database ID
- [x] 更新 `app.py`
    - [x] 匯入 `notion_client`
    - [x] 實作 `save_to_notion` 函式
    - [x] 在語音處理流程中呼叫 Notion 儲存功能
- [x] 驗證功能

---

# Notion 整合功能增強 (新增於 2025-12-26)

- [ ] 更新 Notion 資料庫 schema (需使用者手動操作)
    - [x] 新增 `內容` (Text/Rich Text) 欄位
    - [x] 新增 `摘要` (Text/Rich Text) 欄位
    - [x] 新增 `時間` (Date) 欄位
    - [x] 新增 `類型` (Select) 欄位，並新增選項 `語音筆記`
- [x] 更新 `app.py`
    - [x] 新增 `summarize_text` 函式 (OpenAI)
    - [x] 更新 `save_to_notion` 函式以支援新欄位
    - [x] 在 `handle_audio_message` 中整合摘要與儲存流程
- [x] 驗證功能

---

# 文字摘要與 Notion 整合優化 (新增於 2025-12-27)

- [x] 規劃開發文件與系統設計 (PLANNING)
    - [x] 建立並更新 `task.md` 與 `implementation_plan.md`
    - [x] 設計 `/a` 指令偵測邏輯
    - [x] 設計 Notion 頁面內容 (Children) 寫入邏輯
- [x] 實作文字摘要指令功能 (EXECUTION)
    - [x] 修改 `handle_message` 以支援指令辨識
    - [x] 實作 `summarize_text` 調用 OpenAI API
- [x] 優化 Notion 存檔機制 (EXECUTION)
    - [x] 修改 `save_to_notion` 函數
    - [x] 將原始內容寫入 Notion 頁面子區塊 (Page Content)
- [x] 驗證與測試 (VERIFICATION)
    - [x] 測試 `/a` 指令是否正確觸發
    - [x] 驗證 Notion 頁面內容是否包含長文字
    - [x] 更新 `walkthrough.md` 展示成果

---

# 圖片筆記功能 (Google Drive + OpenAI Vision + Notion) (新增於 2025-12-29)

- [ ] 規劃與設定 (PLANNING)
    - [x] 研究 Google Drive API (OAuth 2.0) 整合
    - [x] 研究 OpenAI Vision API
    - [x] 建立實作計畫並翻譯為繁體中文
- [x] 實作開發 (EXECUTION) [x]
    - [x] 配置環境變數 (Google Drive, OpenAI, Notion) [x]
    - [x] 實作 Google Drive 上傳輔助功能 (OAuth 流程) [x]
    - [x] 實作 OpenAI Vision 辨識輔助功能 [x]
    - [x] 更新 Notion 整合功能以支援圖片筆記 [x]
    - [x] 在 `app.py` 中處理圖片訊息 [x]
- [x] 驗證與測試 (VERIFICATION) [x]
    - [x] 測試圖片上傳至 Google Drive 功能 [x]
    - [x] 測試 OpenAI Vision 辨識準確率 (已優化 Prompt) [x]
    - [x] 測試 Notion 紀錄建立 (包含圖片連結與摘要) [x]
    - [x] 最終端對端流程驗證 [x]
    - [x] 修正時區為台灣 (Asia/Taipei) [x]
    - [x] 同步雲端連結至 Notion「圖片連結」欄位 [x]

---

# 網址自動爬取與摘要功能 (新增於 2025-12-29)

- [x] 規劃與設定 (PLANNING)
    - [x] 新增 `trafilatura` 套件依賴
    - [x] 撰寫並更新實作計畫與相關文件
- [x] 實作開發 (EXECUTION)
    - [x] 實作 `extract_url_content` 協助函數
    - [x] 實作網址偵測邏輯 (Regex)
    - [x] 更新 `handle_message` 以支援網址自動處理
    - [x] 整合爬取、摘要與 Notion 儲存流程
- [x] 驗證與測試 (VERIFICATION)
    - [x] 測試不同網站的爬取效果
    - [x] 驗證 Notion 紀錄是否正確
    - [x] 更新 `walkthrough.md` 展示成果

---

# 記錄使用者 Line ID 功能 (新增於 2025-12-29)

- [x] 規劃與設定 (PLANNING)
    - [x] 更新 Notion 資料庫 schema (需使用者手動新增 `Line_ID` 欄位)
    - [x] 更新實作計畫 `implementation_plan.md`
- [x] 實作開發 (EXECUTION)
    - [x] 修改 `save_to_notion` 函式以接收 `line_id` 參數
    - [x] 更新所有訊息處理器 (`handle_message`, `handle_audio_message`, `handle_image_message`) 擷取 `event.source.user_id`
- [x] 驗證與測試 (VERIFICATION)
    - [x] 驗證 Notion 紀錄是否包含正確的 `Line_ID`
    - [x] 更新 `walkthrough.md`

---

# 使用者權限控管功能 (新增於 2025-12-29)

- [x] 規劃與設定 (PLANNING)
    - [x] 在 `.env` 中新增 `ALLOWED_LINE_ID`
    - [x] 更新實作計畫 `implementation_plan.md`
- [x] 實作開發 (EXECUTION)
    - [x] 修改 `handle_message`, `handle_audio_message`, `handle_image_message`
    - [x] 實作權限檢查邏輯：若非指定 ID 則不執行後續動作或提示錯誤
- [x] 驗證與測試 (VERIFICATION)
    - [x] 驗證指定 ID 可正常使用
    - [x] 驗證其他 ID 被阻擋
    - [x] 更新 `walkthrough.md`

---

# Apify 爬蟲功能增強 (新增於 2025-12-30)

- [x] 規劃與設定 (PLANNING)
    - [x] 研究 Apify API 整合方式
    - [x] 選擇適合的 Apify Actors (Facebook Posts Scraper, Website Content Crawler)
    - [x] 規劃 Facebook 與一般網頁的爬取邏輯
- [x] 實作開發 (EXECUTION)
    - [x] 新增 `apify-client` 依賴套件
    - [x] 在 `.env` 中新增 `APIFY_API_KEY`
    - [x] 實作 `crawl_facebook_post` 函式 (使用 apify/facebook-posts-scraper)
    - [x] 實作 `crawl_general_url` 函式 (使用 apify/website-content-crawler)
    - [x] 更新 `handle_message` 以支援 Facebook 網址偵測與分類
    - [x] 實作回退機制 (Apify 失敗時使用 trafilatura)
- [x] 驗證與測試 (VERIFICATION)
    - [x] 測試 Facebook 公開貼文爬取
    - [x] 測試一般網頁爬取 (新聞、部落格等)
    - [x] 驗證 Notion 紀錄類型正確 (FB 筆記 vs 網頁筆記)
    - [x] 更新開發文件至 `docs` 資料夾
