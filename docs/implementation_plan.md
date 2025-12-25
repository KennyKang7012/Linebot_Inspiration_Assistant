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
