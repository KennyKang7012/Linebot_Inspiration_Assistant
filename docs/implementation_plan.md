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
