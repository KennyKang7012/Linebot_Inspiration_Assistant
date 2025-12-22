# Line Bot 專案提示詞模板

## 角色
你是一位精通 Python 開發的專家，擅長使用 Line Messaging API 與現代 Python 工具。

## 任務
依照以下規格初始化一個 Line Echo Bot 專案：
- **語言**: Python 3.11.7
- **套件管理工具**: `uv`
- **框架**: FastAPI
- **伺服器**: Uvicorn
- **API**: Line Messaging API SDK for Python (v3)

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
2.  **依賴套件**: 新增 `line-bot-sdk`, `fastapi`, `uvicorn`, 以及 `python-dotenv`。
3.  **回應邏輯**: 實作基礎的 Webhook，接收文字訊息並回傳相同的內容。
4.  **資訊安全**: 包含來自 Line 請求的訊息簽章驗證（FastAPI Middleware 或 Dependency Injection 方式）。
5.  **環境變數**:
    - `LINE_CHANNEL_SECRET`
    - `LINE_CHANNEL_ACCESS_TOKEN`

## 實作細節
- 提供清晰的 `README.md` 及安裝步驟。
- 確保程式碼符合 PEP 8 標準。
- 使用 `python-dotenv` 載入環境變數。
