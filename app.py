import os
import sys
import certifi

# Fix SSL certificate verification error on macOS
os.environ['SSL_CERT_FILE'] = certifi.where()

from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    MessagingApiBlob,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    AudioMessageContent,
    ImageMessageContent
)
from openai import OpenAI
from notion_client import Client
from datetime import datetime
import tempfile
import io
import base64
import pytz
import re
import trafilatura
from apify_client import ApifyClient

# 設定時區為台灣
TW_TIMEZONE = pytz.timezone('Asia/Taipei')
# Google Drive API 相關匯入
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# 載入環境變數
load_dotenv(override=True)

app = FastAPI()

# 從環境變數獲取憑證
channel_secret = os.getenv('LINE_CHANNEL_SECRET')
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
openai_api_key = os.getenv('OPENAI_API_KEY')
notion_api_key = os.getenv('NOTION_API_KEY')
notion_database_id = os.getenv('NOTION_DATABASE_ID')
google_drive_folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID', '1yeIYLXlEhDACEqARMWBfBUJpzlYFgPHy')
allowed_line_id = os.getenv('ALLOWED_LINE_ID')
apify_api_key = os.getenv('APIFY_API_KEY')
threads_actor_id = os.getenv('THREADS_ACTOR_ID', 'sinam7/threads-post-scraper')

# Google Drive 權限範圍
SCOPES = ['https://www.googleapis.com/auth/drive.file']

if channel_secret is None or channel_access_token is None:
    print('請在 .env 檔案中設定 LINE_CHANNEL_SECRET 與 LINE_CHANNEL_ACCESS_TOKEN')
    sys.exit(1)

configuration = Configuration(access_token=channel_access_token)
handler = WebhookHandler(channel_secret)
client = OpenAI(api_key=openai_api_key) if openai_api_key else None
notion = Client(auth=notion_api_key) if notion_api_key else None
apify_client = ApifyClient(apify_api_key) if apify_api_key else None

def is_allowed(user_id):
    """檢查使用者是否在白名單中"""
    if not allowed_line_id:
        return True  # 若未設定則預設允許 (或可改為 False 增加安全性)
    return user_id == allowed_line_id

def get_drive_service():
    """獲取 Google Drive 服務實例 (OAuth 2.0)"""
    creds = None
    # token.json 儲存使用者的存取與更新權杖
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # 如果沒有有效憑證，則執行登入流程
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(GoogleRequest())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # 儲存憑證供下次使用
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('drive', 'v3', credentials=creds)

def upload_to_drive(file_content, filename, folder_id):
    """將檔案上傳到 Google Drive 並設定為公開連結"""
    try:
        service = get_drive_service()
        file_metadata = {
            'name': filename,
            'parents': [folder_id]
        }
        media = MediaIoBaseUpload(io.BytesIO(file_content), mimetype='image/jpeg')
        file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        
        # 設定檔案權限為任何擁有連結的人皆可檢視
        service.permissions().create(
            fileId=file.get('id'),
            body={'type': 'anyone', 'role': 'reader'}
        ).execute()
        
        # 再次獲取檔案以獲取 webViewLink (有時建立時拿不到正確的 webViewLink)
        file = service.files().get(fileId=file.get('id'), fields='webViewLink').execute()
        return file.get('webViewLink')
    except Exception as e:
        print(f"Error uploading to Drive: {e}")
        return None

def analyze_image(image_bytes):
    """使用 OpenAI Vision API 辨識圖片內容"""
    if not client:
        return "OpenAI API 未設定"
    try:
        # 將圖片轉為 base64
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "這是一張筆記或靈感圖片，請仔細辨識圖片內容，並將其中的文字或主要物件總結成一段繁體中文摘要，以便我記錄到 Notion。"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            max_tokens=500,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error analyzing image: {e}")
        return f"圖片分析出錯: {e}"

@app.post("/callback")
async def callback(request: Request):
    # 獲取 X-Line-Signature 標頭值
    signature = request.headers.get('X-Line-Signature')
    if not signature:
        raise HTTPException(status_code=400, detail="Missing signature")

    # 獲取請求主體內容
    body = await request.body()
    body_text = body.decode('utf-8')

    # 驗證簽章並處理事件
    try:
        handler.handle(body_text, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    return 'OK'

def summarize_text(text, type="general"):
    if not client:
        return ""
    try:
        # 使用台灣時間
        now_tw = datetime.now(TW_TIMEZONE)
        
        # 根據類型選擇提示詞
        prompts = {
            "audio": "請幫我摘要這段語音轉出的文字，抓出重點：",
            "social": "請幫我摘要這段社群貼文內容，抓出重點：",
            "web": "請幫我摘要這段網頁文章內容，抓出重點：",
            "general": "請幫我摘要這段文字內容，抓出重點："
        }
        prompt_prefix = prompts.get(type, prompts["general"])
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"You are a helpful assistant. The current time is {now_tw.strftime('%Y-%m-%d %H:%M:%S')} (Asia/Taipei)."},
                {"role": "user", "content": f"{prompt_prefix}\n\n{text}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error summarizing text: {e}")
        return ""

def extract_url_content(url):
    """擷取網頁內容並提取文字"""
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            content = trafilatura.extract(downloaded)
            return content
        return None
    except Exception as e:
        print(f"Error extracting URL content: {e}")
        return None

def crawl_facebook_post(url):
    """使用 Apify 爬取 Facebook 貼文內容"""
    if not apify_client:
        print("Apify API key not set.")
        return None
    
    try:
        # 準備輸入參數
        run_input = {
            "startUrls": [{"url": url}],
            "resultsLimit": 1,
            "maxPosts": 1,
            "maxComments": 0,
            "proxy": {"useApifyProxy": True}
        }
        
        # 執行 Actor (apify/facebook-posts-scraper)
        run = apify_client.actor("apify/facebook-posts-scraper").call(run_input=run_input)
        
        # 取得結果
        items = list(apify_client.dataset(run["defaultDatasetId"]).iterate_items())
        if items:
            post = items[0]
            # 組合貼文內容 (根據 Apify 實際輸出結構調整)
            # 優先使用 pageName, 其次是 user.name
            author = post.get('pageName') or post.get('user', {}).get('name') or "未知發布者"
            
            # 優先使用 text, 其次是 message
            text_content = post.get('text') or post.get('message') or "(無文字內容)"
            
            content = f"【Facebook 貼文內容】\n"
            content += f"發布者: {author}\n"
            content += f"發布時間: {post.get('time', post.get('timestamp', '未知'))}\n"
            content += f"內容: {text_content}\n"
            
            # 如果內容為空，提示可能是權限問題
            if text_content == "(無文字內容)":
                content += "\n(註：若內容為空，可能是因為貼文非公開、來自私密社團，或該網址為分享短網址。建議提供標準永久連結且確保貼文設為公開。)\n"
            
            return content
        return None
    except Exception as e:
        print(f"Error crawling Facebook: {e}")
        return None

def crawl_general_url(url):
    """使用 Apify 爬取一般網頁內容"""
    if not apify_client:
        print("Apify API key not set.")
        return None
    
    try:
        # 準備輸入參數 (使用 website-content-crawler)
        run_input = {
            "startUrls": [{"url": url}],
            "maxCrawlPages": 1,
            "onlySubdomain": True,
            "removeCookieWarnings": True,
        }
        
        # 執行 Actor
        run = apify_client.actor("apify/website-content-crawler").call(run_input=run_input)
        
        # 取得結果
        items = list(apify_client.dataset(run["defaultDatasetId"]).iterate_items())
        if items:
            # 提取主要內容
            return items[0].get('markdown') or items[0].get('text')
        return None
    except Exception as e:
        print(f"Error crawling general URL: {e}")
        return None

def crawl_threads_post(url):
    """使用 Apify 爬取 Threads 貼文內容"""
    if not apify_client:
        print("Apify API key not set.")
        return None
    
    try:
        # 準備輸入參數 (根據 sinam7/threads-post-scraper 格式)
        run_input = {
            "url": url
        }
        
        # 執行 Actor
        run = apify_client.actor(threads_actor_id).call(run_input=run_input)
        
        # 取得結果
        items = list(apify_client.dataset(run["defaultDatasetId"]).iterate_items())
        if items:
            post = items[0]
            # 更新解析邏輯 (sinam7 格式)
            # content: 貼文內容 (換行分隔)
            # authorId: 用戶名稱 (如 /@username)
            text_content = post.get('content') or post.get('caption') or "(無文字內容)"
            
            author_id = post.get('authorId', '')
            # 移除開頭的 /@ 或 @
            author = author_id.replace('/', '').replace('@', '') or "未知發布者"
            
            content = f"【Threads 貼文內容】\n"
            content += f"發布者: @{author}\n"
            content += f"內容: {text_content}\n"
            
            return content
        return None
    except Exception as e:
        print(f"Error crawling Threads: {e}")
        return None

def save_to_notion(text, summary, note_type="語音筆記", url=None, line_id=None):
    if not notion or not notion_database_id:
        print("Notion setup incomplete, skipping save.")
        return

    # 使用台灣時間
    now_tw = datetime.now(TW_TIMEZONE)
    current_time = now_tw.isoformat()
    title = f"{note_type} [{now_tw.strftime('%Y-%m-%d %H:%M')}]"

    try:
        # 準備頁面內容 (Children)
        children = []
        
        # 如果有 URL，先加入連結區塊
        if url:
            children.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {"rich_text": [{"text": {"content": "連結"}}]}
            })
            children.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": "查看連結", "link": {"url": url}}
                        }
                    ]
                }
            })

        children.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": [{"text": {"content": "原始內容"}}]}
        })
        
        # 將長文字拆分成多個區塊 (Notion 限制 2000 字元，保守起見設為 1800)
        content_text = text if text else "(無文字內容)"
        for i in range(0, len(content_text), 1800):
            children.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": content_text[i:i+1800]}}]
                }
            })

        # 準備屬性
        properties = {
            "Name": {"title": [{"text": {"content": title}}]},
            "摘要": {"rich_text": [{"text": {"content": summary}}]},
            "時間": {"date": {"start": current_time, "end": None}},
            "類型": {"select": {"name": note_type}}
        }

        # 如果有 URL，同時寫入「URL」屬性 (之前叫「圖片連結」)
        if url:
            properties["URL"] = {"url": url}

        # 如果有 Line ID，寫入「Line_ID」屬性
        if line_id:
            properties["Line_ID"] = {"rich_text": [{"text": {"content": line_id}}]}

        notion.pages.create(
            parent={"database_id": notion_database_id},
            properties=properties,
            children=children
        )
        print("Successfully saved to Notion")
    except Exception as e:
        print(f"Failed to save to Notion: {e}")

@handler.add(MessageEvent, message=ImageMessageContent)
def handle_image_message(event):
    if not is_allowed(event.source.user_id):
        with ApiClient(configuration) as api_client:
            line_messaging_api = MessagingApi(api_client)
            line_messaging_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="抱歉，您沒有權限使用此服務。")]
                )
            )
        return

    with ApiClient(configuration) as api_client:
        line_messaging_api = MessagingApi(api_client)
        line_messaging_api_blob = MessagingApiBlob(api_client)
        
        # 1. 向使用者表示正在處理
        # line_messaging_api.reply_message(
        #     ReplyMessageRequest(
        #         reply_token=event.reply_token,
        #         messages=[TextMessage(text="收到圖片！正在處理中，請稍候...")]
        #     )
        # )
        # 注意：LINE 一個 reply_token 只能回覆一次，所以前面不能先回覆。
        
        # 2. 獲取圖片內容
        message_content = line_messaging_api_blob.get_message_content(event.message.id)
        
        # 3. 分析圖片 (OpenAI Vision)
        analysis_result = analyze_image(message_content)
        
        # 4. 上傳至 Google Drive
        now_tw = datetime.now(TW_TIMEZONE)
        filename = f"image_{now_tw.strftime('%Y%m%d_%H%M%S')}.jpg"
        drive_link = upload_to_drive(message_content, filename, google_drive_folder_id)
        
        if drive_link:
            # 5. 儲存到 Notion
            save_to_notion(analysis_result, analysis_result, note_type="圖片筆記", url=drive_link, line_id=event.source.user_id)
            reply_text = f"【圖片辨識摘要】\n{analysis_result}\n\n【雲端連結】\n{drive_link}"
        else:
            reply_text = f"【圖片辨識摘要】\n{analysis_result}\n\n(注意：圖片上傳雲端失敗)"
        
        # 6. 回傳結果
        line_messaging_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)]
            )
        )

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    if not is_allowed(event.source.user_id):
        with ApiClient(configuration) as api_client:
            line_messaging_api = MessagingApi(api_client)
            line_messaging_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="抱歉，您沒有權限使用此服務。")]
                )
            )
        return

    text = event.message.text.strip()
    
    # 網址偵測邏輯 (簡單的正則表達式)
    url_pattern = r'https?://[^\s]+'
    url_match = re.search(url_pattern, text)
    
    if url_match:
        url = url_match.group(0)
        # 判斷網址類型
        if "facebook.com" in url or "fb.watch" in url:
            content = crawl_facebook_post(url)
            note_type = "FB 筆記"
        elif "threads.net" in url or "threads.com" in url:
            # 自動修正網域並使用 Threads 專用爬蟲
            clean_url = url.replace("threads.com", "threads.net")
            content = crawl_threads_post(clean_url)
            note_type = "Threads 筆記"
        else:
            # 先試試 Apify，失敗則回退到 trafilatura
            content = crawl_general_url(url)
            if not content:
                content = extract_url_content(url)
            note_type = "網頁筆記"

        if content:
            # 2. 摘要內容
            # 根據筆記類型決定摘要提示詞類型
            summary_type = "social" if "FB" in note_type or "Threads" in note_type else "web"
            summary = summarize_text(content, type=summary_type)
            # 3. 儲存到 Notion
            save_to_notion(content, summary, note_type=note_type, url=url, line_id=event.source.user_id)
            reply_text = f"【{note_type}摘要】\n{summary}"
        else:
            reply_text = "無法擷取該網址的內容。"
    
    # 檢查是否包含指令 /a
    elif text.lower().startswith("/a"):
        # 移除指令部分取得純文本
        content = text[2:].strip()
        if not content:
            reply_text = "請在 /a 後方輸入要摘要的文字。"
        else:
            summary = summarize_text(content, type="general")
            save_to_notion(content, summary, note_type="文字摘要", line_id=event.source.user_id)
            reply_text = f"【AI 摘要】\n{summary}"
    else:
        # 一般訊息處理 (Echo)
        reply_text = text

    with ApiClient(configuration) as api_client:
        line_messaging_api = MessagingApi(api_client)
        line_messaging_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)]
            )
        )

@handler.add(MessageEvent, message=AudioMessageContent)
def handle_audio_message(event):
    if not is_allowed(event.source.user_id):
        with ApiClient(configuration) as api_client:
            line_messaging_api = MessagingApi(api_client)
            line_messaging_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="抱歉，您沒有權限使用此服務。")]
                )
            )
        return

    if client is None:
        with ApiClient(configuration) as api_client:
            line_messaging_api = MessagingApi(api_client)
            line_messaging_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="抱歉，系統尚未設定 OpenAI API Key，無法處理語音訊息。")]
                )
            )
        return

    with ApiClient(configuration) as api_client:
        line_messaging_api = MessagingApi(api_client)
        line_messaging_api_blob = MessagingApiBlob(api_client)
        
        # 1. 取得語音內容
        message_content = line_messaging_api_blob.get_message_content(event.message.id)
        
        # 2. 存入暫存檔並交由 Whisper 識別
        # LINE 語音訊息通常是 m4a/aac 格式
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

        # 儲存到 Notion
        if transcript and transcript.text:
            summary = summarize_text(transcript.text, type="audio")
            save_to_notion(transcript.text, summary, note_type="語音筆記", line_id=event.source.user_id)
            
            # 回覆內容包含摘要
            reply_text = f"【辨識結果】\n{transcript.text}\n\n【AI 摘要】\n{summary}"
        else:
            reply_text = "無法辨識語音內容。"
        
        # 3. 回傳辨識結果
        line_messaging_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)]
            )
        )

if __name__ == "__main__":
    import uvicorn
    # 在本地端 8000 埠啟動伺服器
    uvicorn.run(app, host="0.0.0.0", port=8000)
