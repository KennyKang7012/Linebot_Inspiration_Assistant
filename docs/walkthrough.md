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

---

# 實作紀錄 - Notion 整合與 AI 摘要 (新增於 2025-12-26)

我們將語音辨識系統進一步與 Notion 資料庫整合，並加入了 AI 自動摘要功能，讓語音訊息不只是轉換為文字，更能自動整理成結構化的筆記。

## 修改內容

### 1. 依賴項目更新
- 新增了 `notion-client` 套件。

### 2. 核心程式碼變更
- **[app.py](file:///Users/kennykang/Desktop/VibeProj/Anti/Linebot_Inspiration_Assistant/app.py)**:
    - **OpenAI 摘要**: 新增 `summarize_text` 函式，使用 `gpt-4o-mini` 模型對轉錄文字進行重點擷取。
    - **Notion 整合**: 新增 `save_to_notion` 函式，將資訊同步至指定資料庫。
    - **複合式回覆**: Bot 現在會同時回傳「完整辨識結果」與「AI 摘要」。
    - **自動化時間標記**: 紀錄訊息產生的預確切時間。

### 3. 資料庫連動 (Notion)
同步存入以下欄位：
- **Name**: 自動生成的標題，格式如 `語音筆記 [2025-12-26 13:30]`。
- **內容**: 完整的轉錄文字。
- **摘要**: AI 生成的重點內容。
- **時間**: 訊息發生的日期與時間。
- **類型**: 固定標籤為 `語音筆記`。

## 驗證結果

### 功能驗證
- [x] **語音轉錄**: Whisper API 正常運作，繁體中文辨識準確。
- [x] **AI 摘要**: 成功擷取語音重點並生成摘要。
- [x] **Notion 同步**: 資料正確寫入 Notion 資料庫，各個欄位（內容、摘要、時間、類型）皆對齊正確。
- [x] **Line 回覆**: 使用者在 Line 視窗可同時看見文字與摘要內容。

> [!TIP]
> 這種「自動化筆記」的流程非常適合用於快速記錄靈感。使用者只需按下語音輸入，系統便會自動完成轉錄、摘要並歸檔至雲端。

---

# 成果展示 - 文字摘要指令 (/a) 與 Notion 整合優化 (新增於 2025-12-27)

我們成功為 LINE Bot 增加了文字摘要指令支援，並優化了 Notion 的資料儲存方式，使其能處理更長的文本。

## 主要變更

### 1. 指令偵測 (/a)
在 `app.py` 的 `handle_message` 中，我們新增了對 `/a` 開頭文字的辨識。若偵測到該指令，系統會將後續文字傳送至 OpenAI 進行摘要。

### 2. Notion 存檔優化 (Page Content)
為了解決 Notion 屬性欄位（Property）僅能儲存 2000 字元的限制，我們將原始文字內容改為寫入 Notion 頁面的 **Children Blocks**（正文內容）。
- 使用 `notion.pages.create` 的 `children` 參數。
- 自動將長文本拆分為多個 2000 字的 `paragraph` 區塊，確保內容完整不遺漏。

### 3. 多元備註類型
系統現在能自動區分「語音筆記」與「文字摘要」，並在 Notion 的「類型」欄位中正確標記。

---

## 驗證結果

### 代碼變更詳情
render_diffs(file:///Users/kennykang/Desktop/VibeProj/Anti/Linebot_Inspiration_Assistant/app.py)

### 手動驗證步驟與結果
1. **文字摘要測試**：
   - 輸入：`/a 這是一段測試...`
   - 結果：Bot 回傳 AI 產生的摘要，並在 Notion 建立一筆「文字摘要」類型的筆記。
2. **長文字測試**：
   - 輸入：一段超過 3000 字且包含 `/a` 指令的文字。
   - 結果：Notion 頁面成功建立，且原始內容出現在頁面正文（分段顯示），摘要正確顯示於屬性欄位。
---

# 成果展示 - LINE Bot 頭貼生成 (新增於 2025-12-28)

我們為「靈感助手」設計並生成了專屬的 LINE Bot 頭貼風格，讓機器人形象更具專業感與親和力。

## 設計方案

我們提供了三種不同核心理念的設計供選擇：

1.  **現代極簡 (Modern Minimalist)**: 科技感的玻璃質感燈泡，象徵 AI 驅動的靈感。
2.  **親切吉祥物 (Friendly Mascot)**: 可愛的小機器人拿著金色羽毛筆，強調「助手」的角色。
3.  **創意抽象 (Creative Abstract)**: 紙飛機（捕捉靈感）與聲波（語音辨識）的結合，色調活潑。

## 頭貼預覽與存檔

所有生成的圖片已儲存於專案的 `docs/` 資料夾中。

````carousel
### 方案 1: 現代極簡
![現代極簡風格](file:///Users/kennykang/Desktop/VibeProj/Anti/Linebot_Inspiration_Assistant/docs/avatar_minimalist_1766902388327.png)

<!-- slide -->

### 方案 2: 親切吉祥物
![親切吉祥物風格](file:///Users/kennykang/Desktop/VibeProj/Anti/Linebot_Inspiration_Assistant/docs/avatar_mascot_1766902403443.png)

<!-- slide -->

### 方案 3: 創意抽象
![創意抽象風格](file:///Users/kennykang/Desktop/VibeProj/Anti/Linebot_Inspiration_Assistant/docs/avatar_abstract_1766902420248.png)
````

## 驗證結果

### 檔案狀態
- [x] **圖片存檔**: 已成功將 `.png` 檔案複製至 `docs/`。
- [x] **文件更新**: 已在 `walkthrough.md` 中紀錄生成過程與風格描述。

---

# 實作紀錄 - 圖片筆記功能 (Google Drive + OpenAI Vision + Notion) (新增於 2025-12-29)

我們成功實作了自動化的圖片筆記功能。當使用者傳送圖片至 LINE Bot 時，系統會自動辨識圖片內容、上傳至 Google Drive 並在 Notion 中建立詳細紀錄。

## 主要變更

### 1. Google Drive 雲端儲存 (OAuth 2.0)
- 整合 `google-api-python-client`。
- 實作 OAuth 2.0 授權流程，使用 `credentials.json` 進行身分驗證，並自動管理 `token.json` 以實現持久化存取。
- 圖片上傳後會自動設定權限為「任何擁有連結的人皆可檢視」，並取得公開的 `webViewLink`。

### 2. OpenAI Vision 圖片分析
- 使用 `gpt-4o-mini` 模型的視覺能力。
- 將下載的圖片轉為 Base64 格式傳送至 API，取得準確的內容摘要與描述。

### 3. Notion 整合強化
- **save_to_notion**: 升級函式以支援 `image_url`。
- **正文區塊 (Children Blocks)**：
    - 將「圖片連結」以可點擊的連結形式插入 Notion 頁面頂部。
    - 將 AI 分析結果存放在「摘要」屬性與頁面正文中。

### 4. 關鍵程式碼段落
render_diffs(file:///Users/kennykang/Desktop/VibeProj/Anti/Linebot_Inspiration_Assistant/app.py)

## 驗證結果

### 端到端驗證成功
- [x] **啟動授權**：已成功引導使用者完成 Google OAuth 授權，產生 `token.json`。
- [x] **功能測試**：
   - 傳送圖片至 LINE Bot。
   - 成功收到包含「分析摘要」與「雲端連結」的回覆。
   - 確認圖片已成功上傳至 Google Drive 並設定為公開。
   - 確認資料已同步至 Notion，且原始內容存於正文區塊。

### 最終優化與調整 (2025-12-29)

1. **時區在地化**：
   - 整合 `pytz` 函式庫。
   - 將系統所有時間紀錄（Notion 屬性、檔名、AI 參考時間）修正為**台灣時間 (Asia/Taipei)**。

2. **Notion 欄位同步優化**：
   - 更新 `save_to_notion` 邏輯，除了將圖片連結放入正文，也同步寫入資料庫的「**圖片連結**」URL 屬性欄位。

3. **AI 辨識能力提升**：
   - 優化 OpenAI Vision 的提示詞（Prompt），引導 AI 更積極地識別筆記內容。
   - 增加 `max_tokens` 至 500 以確保回覆不被截斷。

4. **環境安全性**：
   - 更新 `.gitignore`，確保 `token.json` 與 `credentials.json` 等私密憑證不會被 Git 追蹤。

---

# 實作紀錄 - 網址自動爬取與摘要功能 (新增於 2025-12-29)

我們成功實作了網址自動識別與爬取功能。當使用者在 LINE 貼上網址時，Bot 會自動擷取網頁內文並生成摘要存入 Notion。

## 主要變更

### 1. 網頁內容擷取 (Trafilatura)
- 整合 `trafilatura` 套件，實現高效且乾淨的網頁內文提取。

### 2. 網址偵測邏輯
- 在 `handle_message` 中加入正則表達式，自動識別訊息中的網址。
- 支援「僅網址」或「文字中包含網址」的偵測。

### 3. Notion 欄位統一
- 將原有的「圖片連結」欄位更名為「URL」，實現圖片、網頁與語音連結的統一存儲。

## 驗證結果 (進行中)
- [x] **網頁爬取測試**：驗證是否能正確提取新聞或部落格內文。
- [x] **AI 摘要測試**：驗證摘要是否準確抓取網頁重點。
- [x] **Notion 存檔測試**：驗證 URL 與內文是否正確存入。
- [x] **原有功能測試**：驗證純文字 Echo 與 `/a` 指令是否正常運作。

---

# 實作紀錄 - 記錄使用者 Line ID 功能 (新增於 2025-12-29)

我們增加了自動紀錄使用者唯一識別碼 (Line ID) 的功能，以便區分不同使用者的靈感紀錄。

## 主要變更

### 1. 修改 `save_to_notion`
- 函式新增 `line_id` 參數。
- 同步將 ID 寫入 Notion 資料庫的「Line_ID」屬性欄位。

### 2. 擷取 Line ID
- 在所有訊息處理器 (`handle_message`, `handle_audio_message`, `handle_image_message`) 中，透過 `event.source.user_id` 取得發送者的識別碼並傳遞。

## 驗證結果
- [x] **文字訊息測試**：傳送一般文字，確認 Notion 已紀錄發送者 ID。
- [x] **網頁摘要測試**：貼上網址，確認 Notion 成功紀錄 ID。
- [x] **語音與圖片測試**：傳送語音或圖片，確認 ID 亦能正確同步。

---

# 實作紀錄 - 使用者權限控管功能 (新增於 2025-12-29)

為了確保服務不被濫用，我們實作了基於 Line ID 的存取控制機制。

## 主要變更

### 1. 白名單機制
- 在 `app.py` 中新增 `is_allowed(user_id)` 函式。
- 從環境變數 `ALLOWED_LINE_ID` 讀取獲授權的使用者 ID。
- 同步更新 `.env.example` 檔案供後續開發參考。

### 2. 處理器防護
- 在 `handle_message`, `handle_audio_message`, `handle_image_message` 的入口處加入權限檢查。
- 未經授權的使用者將收到「抱歉，您沒有權限使用此服務。」的訊息，且系統不會執行任何爬取、識別或儲存動作。

## 驗證結果
- [x] **授權使用者測試**：使用指定 ID (`U4504155baed0514607af81f92b439900`) 發送訊息，功能一切正常。
- [x] **非授權使用者測試**：使用其他 ID 發送訊息，系統正確回覆權限不足訊息，且 Notion 中無新筆記產生。

---

# 系統維護紀錄 - 環境變數穩定性強化 (新增於 2025-12-29)

為了解決熱重啟時可能發生的設定殘留問題，我們進行了系統面的強化。

## 修正內容
- **環境變數覆蓋**: 將 `load_dotenv()` 更新為 `load_dotenv(override=True)`，確保 `.env` 的任何更動都能即時且強制生效。
- **配置一致性**: 重新整理 `.env` 格式，避免因換行符號問題導致 Notion Database ID 讀取錯誤。

## 驗證結果
- [x] **設定生效測試**: 修改 `.env` 後確認系統不需完全重啟即可讀取新值。
- [x] **Notion Validation**: 確認資料庫 ID 讀取正確，不再發生 UUID 驗證失敗。

---

# 實作紀錄 - Apify 爬蟲功能增強 (新增於 2025-12-30)

我們成功整合了 Apify 平台的專業爬蟲服務,大幅提升了網頁內容擷取的成功率,特別是針對 Facebook 貼文和需要 JavaScript 渲染的動態網頁。

## 主要變更

### 1. Apify 平台整合
- 整合 `apify-client` Python SDK
- 支援多種 Apify Actors 以應對不同類型的網頁
- 實作智慧回退機制:Apify 失敗時自動使用 trafilatura

### 2. Facebook 貼文專用爬蟲
**實作函式**: `crawl_facebook_post(url)`
- 使用 Apify Actor: `apify/facebook-posts-scraper`
- 自動提取貼文關鍵資訊:
  - 發布者名稱 (優先使用 `pageName`,其次 `user.name`)
  - 發布時間 (支援 `time` 和 `timestamp` 欄位)
  - 貼文內容 (支援 `text` 和 `message` 欄位)
- 智慧錯誤提示:當內容為空時,自動提示可能原因 (非公開、私密社團等)

### 3. 一般網頁爬蟲增強
**實作函式**: `crawl_general_url(url)`
- 使用 Apify Actor: `apify/website-content-crawler`
- 支援 JavaScript 渲染的動態網頁
- 自動移除 Cookie 警告等干擾元素
- 輸出 Markdown 格式,保留文章結構

### 4. 智慧網址分類系統
更新 `handle_message` 函式,實作多層級爬取策略:
```python
if "facebook.com" in url or "fb.watch" in url:
    content = crawl_facebook_post(url)  # Facebook 專用爬蟲
    note_type = "FB 筆記"
else:
    content = crawl_general_url(url)    # Apify 一般爬蟲
    if not content:
        content = extract_url_content(url)  # 回退到 trafilatura
    note_type = "網頁筆記"
```

### 5. 環境變數配置
- 新增 `APIFY_API_KEY` 環境變數
- 更新 `.env.example` 提供設定範例

## 驗證結果

### Facebook 貼文爬取測試
- [x] **公開貼文**: 成功擷取發布者、時間與完整內容
- [x] **格式化輸出**: 資訊結構清晰,易於閱讀
- [x] **Notion 整合**: 正確標記為「FB 筆記」類型
- [x] **錯誤處理**: 私密貼文或無效連結時給予適當提示

### 一般網頁爬取測試
- [x] **新聞網站**: 成功擷取文章內容 (測試對象: BBC, 科技新報等)
- [x] **部落格文章**: 正確提取主要內容,過濾廣告與側邊欄
- [x] **動態網頁**: 支援需要 JavaScript 的網站
- [x] **回退機制**: Apify 失敗時自動切換到 trafilatura

### 端到端整合驗證
- [x] **AI 摘要**: 爬取內容成功傳遞給 OpenAI 進行摘要
- [x] **Notion 儲存**: 完整內容與摘要正確存入資料庫
- [x] **類型區分**: Facebook 與一般網頁正確分類
- [x] **Line ID 記錄**: 使用者識別碼正確同步

## 技術亮點

### 多層級回退策略
系統實作了三層爬取機制,確保最大的成功率:
1. **第一層**: Apify 專業爬蟲 (支援 JavaScript、反爬蟲機制)
2. **第二層**: Trafilatura 輕量爬蟲 (適合靜態網頁)
3. **第三層**: 錯誤處理與使用者提示

### 成本優化
- 僅在必要時調用 Apify (Facebook 或 trafilatura 失敗時)
- 設定 `maxComments: 0` 避免爬取不必要的留言
- 限制 `maxCrawlPages: 1` 確保只爬取目標頁面

### 使用者體驗提升
- Facebook 貼文格式化顯示,包含發布者與時間
- 錯誤訊息具體明確,協助使用者理解問題
- 回退機制透明,使用者無感切換

## 已知限制與建議

> [!NOTE]
> **Facebook 爬取限制**
> - 僅支援公開貼文
> - 私密社團或好友限定貼文無法存取
> - 建議使用標準永久連結而非短網址

> [!TIP]
> **Apify 免費額度**
> - Apify 提供每月免費額度
> - 建議定期檢查用量: [Apify Console](https://console.apify.com/)
> - 超過額度後會自動回退到 trafilatura

---

*最後更新: 2025-12-30*
