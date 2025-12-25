# 專案實作紀錄 - Line Echo Bot (FastAPI 版)

本專案已成功建立一個基礎的 Line Echo Bot，使用 Python 3.11.7 並透過 `uv` 與 FastAPI 進行開發。

## 完成事項

### 1. 專案初始化與文件
- 已將開發文件與程式碼由 Flask 遷移至 FastAPI。
- 指定 Python 版本為 3.11.7。
- 已建立 `docs` 資料夾並包含相關繁體中文文件。

### 2. 環境與依賴
- 已安裝以下關鍵套件：
    - `line-bot-sdk`: 用於與 Line Messaging API 互動。
    - `fastapi`: 非同步網頁框架。
    - `uvicorn`: ASGI 伺服器。
    - `python-dotenv`: 載入環境變數。

### 3. 核心程式碼
- `app.py`: 改用 FastAPI 實作，支援非同步處理。
- `.env`: 維持憑證設定。

## 驗證結果

### 本地端執行測試
- 執行 `uv run uvicorn app:app --reload` 後，伺服器成功在埠號 8000 啟動。

## 後續步驟
- 請使用者在 `.env` 中填入正確的憑證。
- 使用 `ngrok` 將本地端 8000 埠暴露到外網。

---

# 修復記錄 - SSL 憑證驗證錯誤 (新增於 2025-12-25)

我已經修復了 LINE Bot 在嘗試回覆訊息時發生的 `SSLCertVerificationError` 錯誤。

## 修改內容

### [Linebot Inspiration Assistant]

#### [app.py](file:///Users/kennykang/Desktop/VibeProj/Anti/Linebot_Inspiration_Assistant/app.py)

- 導入了 `certifi` 函式庫。
- 設定了 `SSL_CERT_FILE` 環境變數，使其指向 `certifi` 提供的 CA 憑證包。這對於 Python 在 macOS 上正確執行 SSL 憑證驗證是必要的。

```python
import certifi
import os

# 修復 macOS 上的 SSL 憑證驗證錯誤
os.environ['SSL_CERT_FILE'] = certifi.where()
```

## 驗證結果

### 手動驗證
- [x] 重啟 Uvicorn 伺服器：`uv run uvicorn app:app --reload`。
- [x] 現已可以正常處理 LINE 訊息回覆，不再出現 SSL 錯誤。

> [!NOTE]
> 這個錯誤是因為 macOS 上的 Python 預設 SSL 函式庫無法直接存取系統的根憑證。透過 `certifi.where()` 明確指定憑證路徑可以解決此問題。

---

# 實作紀錄 - 語音轉文字功能 (OpenAI Whisper) (新增於 2025-12-25)

我已經成功實作了語音轉文字功能，讓 LINE Bot 能夠將收到的語音訊息轉換為文字後回傳。

## 修改內容

### 1. 依賴項目更新
- 新增了 `openai` 套件。

### 2. 核心程式碼變更
- **[app.py](file:///Users/kennykang/Desktop/VibeProj/Anti/Linebot_Inspiration_Assistant/app.py)**:
    - 引入了 `MessagingApiBlob` 與 `AudioMessageContent`。
    - 實作了 `handle_audio_message` 處理器，直接回傳辨識出的文字。
    - 使用 `tempfile` 暫存下載的語音內容。
    - 呼叫 OpenAI Whisper API (`whisper-1` 模型) 進行識別，並加入 `language` 與 `prompt` 參數優化為繁體中文輸出。

### 3. 環境變數
- **[.env.example](file:///Users/kennykang/Desktop/VibeProj/Anti/Linebot_Inspiration_Assistant/.env.example)**:
    - 新增了 `OPENAI_API_KEY` 的範例設定。

## 驗證結果

### 程式碼靜態檢查
- [x] 語法檢查通過。
- [x] 邏輯流程與實作計畫一致。

### 手動驗證步驟 (待執行)
> [!IMPORTANT]
> 請在 `.env` 中填入正確的 `OPENAI_API_KEY`。
1. 啟動伺服器：`uv run uvicorn app:app --reload`。
2. 傳送語音訊息給 Bot。
3. 確認 Bot 是否正確回傳辨識後的文字。

---

# 實作紀錄 - 公開網址配置 (ngrok) (新增於 2025-12-26)

為了解決 VS Code 內建 Port Forwarding 在 macOS 環境可能遇到的 `ENOENT` 錯誤，並順利將本地伺服器公開給 LINE Platform 存取，我們採用了 `ngrok` 方案。

## 遇到的問題

1.  **VS Code Port Forwarding 失敗**: 嘗試使用 `remote.forwardPorts` 設定時，出現 `spawn /Applications/Antigravity.app/Contents/Resources/app/bin/code-tunnel ENOENT` 錯誤。
2.  **SSL 憑證錯誤**: `pyngrok` 在首次執行嘗試下載 ngrok binary 時，因 macOS Python 的 SSL 憑證問題出現 `SSL: CERTIFICATE_VERIFY_FAILED`。

## 解決方案

### 1. 建立自動化啟動腳本
我們建立了 `run_with_ngrok.py`，整合了伺服器啟動與通道建立的流程：
- 自動啟動 `ngrok` HTTP 通道指向 8000 埠。
- 顯示公開的 Webhook URL。
- 啟動 `uvicorn` 伺服器。

### 2. 修復 SSL 憑證問題
在 `run_with_ngrok.py` 中加入了與 `app.py` 相同的 `certifi` 修復代碼：
```python
import certifi
import os
os.environ['SSL_CERT_FILE'] = certifi.where()
```

## 使用說明

現在啟動專案請使用以下指令（取代原本的 `uv run uvicorn...`）：

```bash
uv run run_with_ngrok.py
```

### 執行後步驟
1.  終端機會顯示類似以下的資訊：
    ```
    * ngrok tunnel "https://xxxx-xx-xx-xx.ngrok-free.app" -> "http://127.0.0.1:8000"
    * Webhook URL: https://xxxx-xx-xx-xx.ngrok-free.app/callback
    ```
2.  複製 `Webhook URL`。
3.  前往 LINE Developers Console，貼上網址並點擊 **Verify**。
