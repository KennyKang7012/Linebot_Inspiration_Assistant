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
