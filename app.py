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
    AudioMessageContent
)
from openai import OpenAI
from notion_client import Client
from datetime import datetime
import tempfile

# 載入環境變數
load_dotenv()

app = FastAPI()

# 從環境變數獲取憑證
channel_secret = os.getenv('LINE_CHANNEL_SECRET')
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
openai_api_key = os.getenv('OPENAI_API_KEY')
notion_api_key = os.getenv('NOTION_API_KEY')
notion_database_id = os.getenv('NOTION_DATABASE_ID')

if channel_secret is None or channel_access_token is None:
    print('請在 .env 檔案中設定 LINE_CHANNEL_SECRET 與 LINE_CHANNEL_ACCESS_TOKEN')
    sys.exit(1)

if openai_api_key is None:
    print('警告：未設定 OPENAI_API_KEY，語音辨識功能將無法運作。')

configuration = Configuration(access_token=channel_access_token)
handler = WebhookHandler(channel_secret)
client = OpenAI(api_key=openai_api_key) if openai_api_key else None
notion = Client(auth=notion_api_key) if notion_api_key else None

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

def summarize_text(text):
    if not client:
        return ""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"請幫我摘要這段語音轉出的文字，抓出重點：\n\n{text}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error summarizing text: {e}")
        return ""

def save_to_notion(text, summary, note_type="語音筆記"):
    if not notion or not notion_database_id:
        print("Notion setup incomplete, skipping save.")
        return

    current_time = datetime.now().isoformat()
    title = f"{note_type} [{datetime.now().strftime('%Y-%m-%d %H:%M')}]"

    try:
        # 將長文字拆分成多個區塊（Notion 單個區塊限制為 2000 字元，雖然正文可以有很多區塊）
        # 這裡我們簡單處理，如果真的超級長再細分，目前先以單一 paragraph 寫入
        children = [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {"rich_text": [{"text": {"content": "原始內容"}}]}
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": text[:2000]} # 安全起見先截斷，若要支援更長需循環建立 block
                        }
                    ]
                }
            }
        ]
        
        # 如果超過 2000 字，追加後續區塊
        if len(text) > 2000:
            for i in range(2000, len(text), 2000):
                children.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": text[i:i+2000]}}]
                    }
                })

        notion.pages.create(
            parent={"database_id": notion_database_id},
            properties={
                "Name": {"title": [{"text": {"content": title}}]},
                "摘要": {"rich_text": [{"text": {"content": summary}}]},
                "時間": {"date": {"start": current_time, "end": None}},
                "類型": {"select": {"name": note_type}}
            },
            children=children
        )
        print("Successfully saved to Notion")
    except Exception as e:
        print(f"Failed to save to Notion: {e}")

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    text = event.message.text.strip()
    
    # 檢查是否包含指令 /a
    if text.lower().startswith("/a"):
        # 移除指令部分取得純文本
        content = text[2:].strip()
        if not content:
            reply_text = "請在 -a 後方輸入要摘要的文字。"
        else:
            summary = summarize_text(content)
            save_to_notion(content, summary, note_type="文字摘要")
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
            summary = summarize_text(transcript.text)
            save_to_notion(transcript.text, summary, note_type="語音筆記")
            
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
