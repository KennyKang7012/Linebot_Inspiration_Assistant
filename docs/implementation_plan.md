# 實作計畫 - 使用 UV 管理的 Line Echo Bot (FastAPI 版)

建立一個基礎的 Line Echo Bot，使用 Python 3.11.7 並透過 `uv` 與 FastAPI 進行開發。

## 建議變更

### 專案初始化
- 使用 `uv init` 初始化專案，指定 Python 版本為 3.11.7。
- 移除 `flask` 與 `gunicorn`。
- 新增套件：`fastapi`, `uvicorn`, `line-bot-sdk`, `python-dotenv`。

### 核心邏輯
#### [MODIFY] [app.py](file:///Users/kennykang/Desktop/VibeProj/Anti/Linebot_Inspiration_Assistant/app.py)
- 改用 FastAPI 實作應用程式。
- 設定 `POST /callback` 路由。
- 實作非同步（async）訊息處理。
- 確保簽章驗證邏輯正確。

#### [KEEP] [.env](file:///Users/kennykang/Desktop/VibeProj/Anti/Linebot_Inspiration_Assistant/.env)
- 維持現有的憑證設定。

## 驗證計畫

### 手動驗證
1.  使用 `uv run uvicorn app:app --reload` 啟動服務。
2.  確認服務在 Port 8000 (預設) 啟動。
3.  確認 Python 版本為 3.11.7。

---

# Fix SSL Certificate Verification Error (Added 2025-12-25)

On macOS, Python often fails to find the local issuer certificates, leading to `SSLCertVerificationError` when making HTTPS requests. Since the LINE Messaging API requires HTTPS, this causes the bot to fail when replying to messages.

## Proposed Changes

### [Linebot Inspiration Assistant]

#### [MODIFY] [app.py](file:///Users/kennykang/Desktop/VibeProj/Anti/Linebot_Inspiration_Assistant/app.py)

Add code to set the `SSL_CERT_FILE` environment variable using `certifi.where()` at the beginning of the script. This ensures that the LINE SDK (which uses `urllib3`) can find the correct CA certificates.

```python
import certifi
import os

# Fix SSL certificate verification error on macOS
os.environ['SSL_CERT_FILE'] = certifi.where()
```

## Verification Plan

### Manual Verification
1. Kill the current running server.
2. Restart the server: `uv run uvicorn app:app --reload`.
3. Send a message to the LINE bot.
4. Verify that the bot replies successfully without the `SSLCertVerificationError`.

---

# 實作語音轉文字功能 (OpenAI Whisper) (新增於 2025-12-25)

此計畫旨在讓 LINE Bot 能夠接收語音訊息，並使用 OpenAI 的 Whisper 模型將其轉換為文字後回傳。

## 使用者評論與確認事項

> [!IMPORTANT]
> 需要在 `.env` 檔案中設定 `OPENAI_API_KEY` 才能運作。
> 請確認已安裝 `ffmpeg`，因為 OpenAI API 可能需要特定的音訊格式處理。

## 建議變更

### 依賴項目

#### [MODIFY] [pyproject.toml](file:///Users/kennykang/Desktop/VibeProj/Anti/Linebot_Inspiration_Assistant/pyproject.toml)
- 新增 `openai` 依賴。

### 環境變數

#### [MODIFY] [.env](file:///Users/kennykang/Desktop/VibeProj/Anti/Linebot_Inspiration_Assistant/.env)
- 新增 `OPENAI_API_KEY` 欄位。

### 核心邏輯

#### [MODIFY] [app.py](file:///Users/kennykang/Desktop/VibeProj/Anti/Linebot_Inspiration_Assistant/app.py)

- **匯入新組件**：
  在檔案開頭匯入必要的 LINE SDK 組件與 OpenAI 客戶端：
  ```python
  from linebot.v3.messaging import MessagingApiBlob
  from linebot.v3.webhooks import AudioMessageContent
  from openai import OpenAI
  import tempfile
  ```

- **初始化 OpenAI 客戶端**：
  ```python
  client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
  ```

- **新增語音訊息處理邏輯**：
  保留原有的 `handle_message` (處理文字)，並**新增**一個處理器：
  ```python
  @handler.add(MessageEvent, message=AudioMessageContent)
  def handle_audio_message(event):
      with ApiClient(configuration) as api_client:
          line_messaging_api = MessagingApi(api_client)
          line_messaging_api_blob = MessagingApiBlob(api_client)
          
          # 1. 取得語音內容
          message_content = line_messaging_api_blob.get_message_content(event.message.id)
          
          # 2. 存入暫存檔並交由 Whisper 識別
          with tempfile.NamedTemporaryFile(suffix='.m4a', delete=True) as tf:
              tf.write(message_content)
              tf.flush()
              
              with open(tf.name, "rb") as audio_file:
                  transcript = client.audio.transcriptions.create(
                      model="whisper-1", 
                      file=audio_file,
                      language="zh",
                      prompt="以下是繁體中文的對話內容："
                  )
          
          # 3. 回傳辨識結果
          line_messaging_api.reply_message(
              ReplyMessageRequest(
                  reply_token=event.reply_token,
                  messages=[TextMessage(text=transcript.text)]
              )
          )
  ```

## 驗證計畫

### 自動化測試
- 目前無自動化測試，主要依賴手動測試。

### 手動驗證
1. 啟動 `uvicorn app:app --reload`。
2. 在 LINE Bot 中傳送一段語音訊息。
3. 確認 Bot 是否回傳正確的文字內容。

---

# Notion 整合計畫 (新增於 2025-12-25)

本計畫描述如何整合 Notion API 以儲存語音訊息轉出的文字。

## 需要使用者審查

> [!IMPORTANT]
> 您需要提供 **Notion Integration Token** (API Key) 和 **Database ID**。
> 1. 請至 [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations) 建立整合。
> 2. 將目標資料庫分享給該整合。
> 3. 複製 "Internal Integration Token" 和 Database ID (從資料庫網址取得)。

## 建議變更

### 設定
#### [MODIFY] [.env.example](file:///Users/kennykang/Desktop/VibeProj/Anti/Linebot_Inspiration_Assistant/.env.example)
- 新增 `NOTION_API_KEY`
- 新增 `NOTION_DATABASE_ID`

### 依賴項目
- 在 `pyproject.toml` 中新增 `notion-client` (透過 `uv add notion-client`)

### 程式碼變更
#### [MODIFY] [app.py](file:///Users/kennykang/Desktop/VibeProj/Anti/Linebot_Inspiration_Assistant/app.py)
- 從 `notion_client` 匯入 `Client`。
- 使用環境變數初始化 Notion client。
- 建立輔助函式 `save_to_notion(text: str)`：
    - 在指定資料庫中建立新頁面。
    - 將標題 (或文字屬性) 設定為轉錄的文字。
    - 選擇性加入時間戳記或標籤。
- 更新 `handle_audio_message`：
    - 在 `client.audio.transcriptions.create` 成功回傳後，呼叫 `save_to_notion(transcript.text)`。
    - 優雅地處理潛在錯誤 (如 Notion API 失敗)，確保使用者仍能收到回覆。

## 驗證計畫

### 自動化測試
- 此小功能暫無自動化測試計畫。

### 手動驗證
1.  **環境設定**：在 `.env` 中加入真實的金鑰。
2.  **發送語音訊息**：向 Line 機器人發送語音訊息。
3.  **檢查 Line**：確認機器人回覆文字內容。
4.  **檢查 Notion**：確認 Notion 資料庫中出現包含正確文字的新頁面。

---

# Notion 整合功能增強 (2025-12-26)

本計畫詳述如何增強 Notion 整合功能，加入摘要、時間戳記與分類標籤。

## 需要使用者審查

> [!IMPORTANT]
> **資料庫 Schema 更新需求**
> 請務必至 Notion 資料庫新增以下欄位 (大小寫需完全一致)：
> 1.  **內容** (Text / Rich Text): 儲存完整轉錄文字。
> 2.  **摘要** (Text / Rich Text): 儲存 AI 產生的摘要。
> 3.  **時間** (Date): 儲存訊息時間。
> 4.  **類型** (Select): 儲存類型標籤。請新增選項「語音筆記」。
> 5.  **Name** (Title): 將儲存自動生成的標題 (例如：「語音筆記 [YYYY-MM-DD HH:MM]」)。

## 建議變更

### 程式碼變更
#### [MODIFY] [app.py](file:///Users/kennykang/Desktop/VibeProj/Anti/Linebot_Inspiration_Assistant/app.py)

1.  **新增 `summarize_text(text: str) -> str`**:
    -   呼叫 OpenAI Chat Completion API (如 `gpt-4o-mini` 或 `gpt-3.5-turbo`) 進行摘要。
    -   Prompt: "請幫我摘要這段語音轉出的文字，抓出重點："

2.  **更新 `save_to_notion(text: str, summary: str)`**:
    -   接收 `summary` 參數。
    -   取得目前 ISO 格式時間。
    -   建構 Notion payload 以填入：
        -   `Name`: "語音筆記 [YYYY-MM-DD HH:MM]"
        -   `內容`: `text`
        -   `摘要`: `summary`
        -   `時間`: 當前時間
        -   `類型`: "語音筆記"

3.  **更新 `handle_audio_message`**:
    -   轉錄完成後，呼叫 `summarize_text`。
    -   呼叫 `save_to_notion(transcript.text, summary)`。

## 驗證計畫

### 手動驗證
1.  **更新 Schema**: 使用者手動在 Notion 新增欄位。
2.  **發送語音訊息**: 發送語音訊息。
3.  **驗證**: 檢查 Notion 是否出現包含所有正確填入欄位的新資料。

---

# 實作完成通知 (2025-12-26)

本專案的所有功能需求（Line Echo Bot、SSL 修復、語音轉文字、Notion 整合、AI 自動摘要）均已實作並驗證完成。

- **目前狀態**: 已部署並可正常運行。
- **維護建議**: 如需更改摘要邏輯，可調整 `app.py` 中的 `summarize_text` 提示詞。

---

# 文字摘要指令與 Notion 整合優化計畫 (新增於 2025-12-27)

本計畫旨在為 LINE Bot 增加 `/a` 指令支援，當使用者傳送以 `/a` 開頭的文字時，系統會自動總結內容並存入 Notion。同時，為了解決 Notion 屬性欄位（Property）的字數限制，我們將原始內容改為存放在 Notion 的「頁面內容（Page Content）」中。

## 使用者建議 / 關鍵設計決策

> [!IMPORTANT]
> **Notion 長度限制解決方案**：Notion 的 `rich_text` 屬性欄位有 2000 字元的限制。我們將改用 `children` 參數在建立頁面時直接寫入內容區塊，這樣可以支援更長的文本。

## 擬議變更

### Line Bot 應用程式 (`app.py`)

#### [MODIFY] [app.py](file:///Users/kennykang/Desktop/VibeProj/Anti/Linebot_Inspiration_Assistant/app.py)

- **指令辨識**：在 `handle_message` 函數中加入邏輯，判斷訊息是否以 `/a` (不分大小寫) 開頭。
- **摘要邏輯**：如果是指令訊息，則呼叫 `summarize_text` 取得摘要。
- **Notion 整合優化**：
    - 修改 `save_to_notion` 函數，接受 `note_type` 參數（預設為 "語音筆記"，若為指令則傳入 "文字摘要"）。
    - 移除 `properties` 中的 `內容` 欄位。
    - 在 `notion.pages.create` 中加入 `children` 參數，將原始內容以 `paragraph` 或 `code` 區塊形式寫入頁面。
- **回覆邏輯**：在 LINE 中回傳摘要結果給使用者。

## 驗證計畫

### 手動驗證步驟
1. **指令測試**：傳送 `/a 這是一段測試文字` 至 LINE Bot，確認是否收到摘要回覆。
2. **長文字測試**：傳送一段超過 2000 字的文字（附帶 `/a` 指令），確認 Notion 頁面是否成功建立且內容完整。
3. **Notion 確認**：
    - 確認「類型」屬性是否正確（文字摘要 vs 語音筆記）。
    - 確認原始內容出現在 Notion 頁面的正文區（而不是屬性欄位）。
    - 確認摘要仍保留在屬性欄位。

---

# 圖片筆記功能實作計畫 (新增於 2025-12-29)

實作一個功能，讓使用者上傳圖片到 LINE 後，將其儲存在 Google Drive 並透過 OpenAI Vision API 產生摘要，最後記錄到 Notion。

## 需要使用者確認

> [!IMPORTANT]
> - **Google OAuth 驗證**：我將使用提供的 `credentials.json` 進行 OAuth 2.0 驗證。
> - **初始設定**：第一次執行時，程式可能需要在終端機提示您進行授權（開啟瀏覽器登入 Google 帳號），完成後會產生 `token.json` 以供後續自動登入。
> - **權限設定**：請確保您的 Google Cloud Console 專案中已啟動 **Google Drive API**。

## 預計變更內容

### 依賴套件
- 新增 Google API 用戶端程式庫：`google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`。

### 環境變數
- `GOOGLE_CREDENTIALS_FILE`：預設為 `credentials.json`。
- `GOOGLE_TOKEN_FILE`：預設為 `token.json`。
- `GOOGLE_DRIVE_FOLDER_ID`：`1yeIYLXlEhDACEqARMWBfBUJpzlYFgPHy`。

### 實作細節

#### [修改] [app.py](file:///Users/kennykang/Desktop/VibeProj/Anti/Linebot_Inspiration_Assistant/app.py)
- 匯入 Google Drive API 程式庫 (`googleapiclient.discovery`, `google_auth_oauthlib.flow` 等)。
- 實作 `get_drive_service()`：
    - 使用 `credentials.json` 處理 OAuth 2.0 流程。
    - 讀取/儲存 `token.json` 以實現持久化存取。
- 實作 `upload_to_drive(file_obj, filename, folder_id)`：
    - 將檔案上傳到指定資料夾。
    - 設定檔案權限為「任何擁有連結的人皆可查看」。
    - 回傳公開的 `webViewLink`。
- 實作 `analyze_image(image_bytes)`：
    - 使用 `gpt-4o-mini` 的視覺能力 (Vision) 來摘要圖片內容。
- 更新 `handle_message` 以支援 `ImageMessageContent`：
    - 從 LINE 下載圖片。
    - 上傳到 Google Drive。
    - 使用 OpenAI Vision 辨識內容。
    - 使用 `save_to_notion(image_url, analysis_result, note_type="圖片筆記")` 儲存到 Notion。

#### [修改] [pyproject.toml](file:///Users/kennykang/Desktop/VibeProj/Anti/Linebot_Inspiration_Assistant/pyproject.toml)
- 新增 Google API 相關依賴。

## 驗證計畫

### 手動驗證
1. **Google OAuth 流程**：啟動程式並在瀏覽器中完成授權（若有提示），確認產生 `token.json`。
2. **Google Drive 上傳**：傳送圖片給 Bot，確認圖片出現在指定雲端硬碟資料夾且可公開存取。
3. **OpenAI Vision**：確認 Bot 回傳合理的圖片內容摘要。
4. **Notion 紀錄**：確認 Notion 中建立了包含圖片連結與摘要的新分頁。
5. **端到端測試**：傳送圖片給 LINE Bot，確認其回覆摘要且資料正確儲存。

---

# 網址自動爬取與摘要功能實作計畫 (新增於 2025-12-29)

本計畫旨在實現當使用者在 LINE 貼上網址時，機器人能自動爬取網頁內容、進行 AI 摘要並存入 Notion。

## 待辦事項與使用者確認
- [x] 需要新增 `trafilatura` 套件來負責網頁內容擷取。
- [ ] 網址偵測邏輯：當訊息「包含網址」或「僅為網址」時觸發爬取流程。
- [ ] 若訊息不包含網址且不屬於指令（如 `/a`），則維持原有的 Echo 功能。
- [x] 使用者已將 Notion「圖片連結」欄位更名為「URL」，將統一使用此欄位。

## 預計變更

### [Component] 依賴管理
#### [MODIFY] [pyproject.toml](file:///Users/kennykang/Desktop/VibeProj/Anti/Linebot_Inspiration_Assistant/pyproject.toml)
- 新增 `trafilatura` 套件。

### [Component] LINE Bot 核心邏輯
#### [MODIFY] [app.py](file:///Users/kennykang/Desktop/VibeProj/Anti/Linebot_Inspiration_Assistant/app.py)
- **匯入**: 新增 `import trafilatura` 與 `import re`。
- **新增函式 `extract_url_content(url)`**: 
  - 使用 `trafilatura.fetch_url` 下載網頁。
  - 使用 `trafilatura.extract` 提取乾淨的文字內容。
- **修改 `handle_message`**:
  - 加入正則表達式偵測訊息是否包含網址（例如使用 `re.search`）。
  - 若偵測到網址：
    1. 執行爬取 `extract_url_content`。
    2. 調用 OpenAI 摘要 `summarize_text`。
    3. 呼叫 `save_to_notion`，將網址存入 Notion 的「URL」欄位（原「圖片連結」），`note_type` 設為「網頁筆記」。
  - 若偵測不到網址：
    1. 檢查是否為 `/a` 指令。
    2. 若都不是，則回傳原訊息 (Echo)。

## 驗證計畫

### 自動化測試
- 無（目前以手動測試為主）。

### 手動驗證
1. 在 LINE 發送一個新聞網址（例如：BBC, 科技新報）。
2. 確認機器人回覆「正在爬取內容...」或直接回覆摘要。
3. 檢查 Notion 資料庫，確認：
-   無（目前以手動測試為主）。

### 手動驗證
1.  在 LINE 發送一個新聞網址（例如：BBC, 科技新報）。
2.  確認機器人回覆「正在爬取內容...」或直接回覆摘要。
3.  檢查 Notion 資料庫，確認：
    -   「類型」為「網頁筆記」。
    -   「摘要」包含 AI 生成的重點。
    -   「URL」欄位正確存入原始網址。
    -   頁面內容包含擷取到的原始文字。
4.  測試純文字（如 "哈囉"）：機器人應回覆 "哈囉"。
5.  測試文字摘要指令（如 "/a 測試內容"）：機器人應進行摘要運作。

---

# 記錄使用者 Line ID 功能實作計畫 (新增於 2025-12-29)

本計畫旨在將發送訊息的使用者其唯一識別碼 (Line ID) 儲存至 Notion 資料庫中，以便後續分析或管理。

## 需要使用者審查

> [!IMPORTANT]
> **Notion 資料庫 Schema 更新**
> 請手動在 Notion 資料庫中新增一個欄位：
> -   **Line_ID** (Text / Rich Text): 用於儲存使用者的 `user_id`。

## 預計變更

### [Component] LINE Bot 核心邏輯
#### [MODIFY] [app.py](file:///Users/kennykang/Desktop/VibeProj/Anti/Linebot_Inspiration_Assistant/app.py)
-   **修改 `save_to_notion`**:
    -   新增參數 `line_id: str = None`。
    -   在 `properties` 中加入 `"Line_ID": {"rich_text": [{"text": {"content": line_id}}]}`。
-   **更新處理器**:
    -   在 `handle_message` (文字)、`handle_audio_message` (語音)、`handle_image_message` (圖片) 中，從 `event.source.user_id` 擷取 Line ID。
    -   在呼叫 `save_to_notion` 時傳入此 ID。

## 驗證計畫

### 手動驗證
1.  在 LINE 發送文字訊息（帶或不帶指令）、語音訊息或圖片。
2.  檢查 Notion 資料庫，確認「Line_ID」欄位是否正確填入使用者的識別碼。

---

# 使用者權限控管功能實作計畫 (新增於 2025-12-29)

為了避免 LINE Bot 被不當的使用者濫用，本計畫將實作白名單機制，僅允許特定的 Line ID 使用靈感助手的功能。

## 預計變更

### 環境變數
#### [MODIFY] [.env](file:///Users/kennykang/Desktop/VibeProj/Anti/Linebot_Inspiration_Assistant/.env)
- 新增 `ALLOWED_LINE_ID=U4504155baed0514607af81f92b439900`。

#### [MODIFY] [.env.example](file:///Users/kennykang/Desktop/VibeProj/Anti/Linebot_Inspiration_Assistant/.env.example)
- 新增 `ALLOWED_LINE_ID` 範例供參考。

### [Component] LINE Bot 核心邏輯
#### [MODIFY] [app.py](file:///Users/kennykang/Desktop/VibeProj/Anti/Linebot_Inspiration_Assistant/app.py)
- **新增 `is_allowed(user_id)` 輔助函式**: 檢查傳入的 `user_id` 是否與 `ALLOWED_LINE_ID` 相符。
- **更新所有處理器**: 
  - 在 `handle_message`, `handle_audio_message`, `handle_image_message` 的最開始調用 `is_allowed`。
  - 若 `is_allowed` 回傳 `False`，則回覆「您沒有權限使用此服務」並結束處理。

## 驗證計畫

### 手動驗證
1. 使用 ID 為 `U4504155baed0514607af81f92b439900` 的帳號發送訊息，確認一切運作正常。
2. 使用其他帳號發送訊息，確認機器人回覆權限不足訊息且不執行爬取或儲存動作。

---

# Apify 爬蟲功能增強實作計畫 (新增於 2025-12-30)

本計畫旨在增強網頁爬取能力，特別針對 Facebook 貼文和需要 JavaScript 渲染的動態網頁，透過整合 Apify 平台的專業爬蟲服務來提升內容擷取的成功率與品質。

## 需要使用者審查

> [!IMPORTANT]
> **Apify API 金鑰需求**
> - 需要註冊 Apify 帳號並取得 API Token: [https://console.apify.com/account/integrations](https://console.apify.com/account/integrations)
> - Apify 提供免費方案，每月有一定額度的免費爬取次數
> - 將 API Token 設定於 `.env` 檔案中的 `APIFY_API_KEY` 變數

> [!WARNING]
> **Facebook 爬取限制**
> - 僅能爬取**公開貼文**，私密貼文或社團貼文可能無法存取
> - 建議使用標準的 Facebook 永久連結 (例如: `https://www.facebook.com/username/posts/123456`)
> - 短網址 (如 `fb.watch`) 可能導致爬取結果不完整

## 預計變更

### 依賴套件
#### [MODIFY] [pyproject.toml](file:///Users/kennykang/Desktop/VibeProj/Anti/Linebot_Inspiration_Assistant/pyproject.toml)
- 新增 `apify-client` 套件

### 環境變數
#### [MODIFY] [.env](file:///Users/kennykang/Desktop/VibeProj/Anti/Linebot_Inspiration_Assistant/.env)
- 新增 `APIFY_API_KEY` 欄位

#### [MODIFY] [.env.example](file:///Users/kennykang/Desktop/VibeProj/Anti/Linebot_Inspiration_Assistant/.env.example)
- 新增 `APIFY_API_KEY` 範例供參考

### [Component] LINE Bot 核心邏輯
#### [MODIFY] [app.py](file:///Users/kennykang/Desktop/VibeProj/Anti/Linebot_Inspiration_Assistant/app.py)

**新增匯入**:
```python
from apify_client import ApifyClient
```

**初始化 Apify 客戶端**:
```python
apify_client = ApifyClient(apify_api_key) if apify_api_key else None
```

**新增 `crawl_facebook_post(url)` 函式**:
- 使用 Apify Actor: `apify/facebook-posts-scraper`
- 輸入參數:
  - `startUrls`: 包含目標 Facebook 貼文網址
  - `resultsLimit`: 1 (僅爬取單一貼文)
  - `maxComments`: 0 (不爬取留言以節省配額)
  - `proxy`: 使用 Apify 代理伺服器
- 輸出格式化:
  - 提取發布者名稱 (`pageName` 或 `user.name`)
  - 提取發布時間 (`time` 或 `timestamp`)
  - 提取貼文內容 (`text` 或 `message`)
  - 若內容為空，提示可能的原因 (非公開、私密社團等)

**新增 `crawl_general_url(url)` 函式**:
- 使用 Apify Actor: `apify/website-content-crawler`
- 輸入參數:
  - `startUrls`: 包含目標網頁網址
  - `maxCrawlPages`: 1 (僅爬取單一頁面)
  - `onlySubdomain`: True (限制在同一子網域)
  - `removeCookieWarnings`: True (移除 Cookie 警告)
- 輸出: 返回 Markdown 格式或純文字內容

**更新 `handle_message` 函式**:
- 在網址偵測邏輯中加入 Facebook 判斷:
  ```python
  if "facebook.com" in url or "fb.watch" in url:
      content = crawl_facebook_post(url)
      note_type = "FB 筆記"
  else:
      # 先嘗試使用 Apify，失敗則回退到 trafilatura
      content = crawl_general_url(url)
      if not content:
          content = extract_url_content(url)
      note_type = "網頁筆記"
  ```

## 驗證計畫

### 自動化測試
- 無 (目前以手動測試為主)

### 手動驗證

#### Facebook 貼文測試
1. 在 LINE 發送一個公開的 Facebook 貼文連結
2. 確認機器人回覆包含:
   - 發布者名稱
   - 發布時間
   - 貼文內容
   - AI 生成的摘要
3. 檢查 Notion 資料庫:
   - 「類型」欄位為「FB 筆記」
   - 「URL」欄位包含原始 Facebook 連結
   - 頁面內容包含完整的貼文資訊

#### 一般網頁測試
1. 在 LINE 發送一個新聞或部落格網址
2. 確認使用 Apify 爬取成功 (或回退到 trafilatura)
3. 確認摘要品質與 Notion 儲存正確

#### 回退機制測試
1. 暫時停用 Apify API Key (註解或移除)
2. 發送網址，確認系統自動使用 trafilatura
3. 確認功能仍正常運作

#### 錯誤處理測試
1. 發送私密 Facebook 貼文連結
2. 確認系統回覆適當的錯誤訊息
3. 發送無效或無法存取的網址
4. 確認系統不會崩潰並給予適當回饋

---

# 使用 Apify 整合 Threads 爬蟲計畫 (新增於 2025-12-30)

本計畫概述了在 Linebot 靈感助手（Linebot Inspiration Assistant）中加入 Threads 支援的步驟。我們將選用 Apify 的 `sinam7/threads-post-scraper` Actor，此方案**無需支付固定月費**，僅按爬取結果計費（Pay-per-result），且可完美搭配 Apify 每月贈送的 $5 免費額度。

## 預計變更

### 設定檔
#### [修改] [.env.example](file:///Users/kennykang/Desktop/VibeProj/Anti/Linebot_Inspiration_Assistant/.env.example)
- 在範例環境變數中加入 `THREADS_ACTOR_ID` (預設為 `sinam7/threads-post-scraper`)。

### 應用程式邏輯
#### [修改] [app.py](file:///Users/kennykang/Desktop/VibeProj/Anti/Linebot_Inspiration_Assistant/app.py)
- 從環境變數中讀取 `THREADS_ACTOR_ID`。
- 實作 `crawl_threads_post(url)` 函數：
    - 使用 `apify_client` 呼叫 Actor `sinam7/threads-post-scraper`。
    - 輸入格式：`{"url": url}`。
    - 從結果中提取貼文文字 (`text`) 與作者資訊。
- 更新 `handle_message` 函數：
    - 加入對 `threads.net` 網址的偵測邏輯。
    - 將偵測到的 Threads 網頁導向至 `crawl_threads_post`。
    - 將 `note_type` 設定為「Threads 筆記」。

## 驗證計畫

### 手動驗證
- **測試 Threads 連結**:
    1. 傳送一個 Threads 貼文網址（例如 `https://www.threads.net/@zuck/post/C_A5V-Sst-T`）給 Line 機器人。
    2. 驗證機器人是否能成功擷取內容並回傳摘要。
    3. 檢查 Notion 資料庫，確保已新增「Threads 筆記」入口，且包含正確的 URL、原始文字與摘要。
- **錯誤處理測試**:
    1. 傳送一個無效或私人的 Threads 網址（可能需要權限）。
    2. 驗證機器人是否能優雅地處理錯誤。

## 實際執行修正紀錄 (2025-12-30)

### 1. 欄位解析修正
- `sinam7/threads-post-scraper` 的回傳欄位與預期不同。
- **修正**: 將解析邏輯從 `text`/`author` 更新為 `content`/`authorId`。

### 2. 提示詞優化
- **問題**: 摘要總是顯示「語音轉出的文字」。
- **修正**: 更新 `summarize_text` 函式，新增 `type` 參數以支援不同情境的提示詞 (social, web, audio)。

### 3. 用戶體驗優化
- **問題**: 使用者分享 `threads.com` 連結被誤判為一般網頁。
- **修正**: 在 `handle_message` 中加入自動轉換邏輯，將 `threads.com` 替換為 `threads.net`。
- **問題**: Notion 儲存失敗。
- **修正**: 將 Notion 內容分塊大小限制從 2000 字調降為 1800 字。
