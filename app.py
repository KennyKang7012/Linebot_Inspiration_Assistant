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
import tempfile

# 載入環境變數
load_dotenv()

app = FastAPI()

# 從環境變數獲取憑證
channel_secret = os.getenv('LINE_CHANNEL_SECRET')
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
openai_api_key = os.getenv('OPENAI_API_KEY')

if channel_secret is None or channel_access_token is None:
    print('請在 .env 檔案中設定 LINE_CHANNEL_SECRET 與 LINE_CHANNEL_ACCESS_TOKEN')
    sys.exit(1)

if openai_api_key is None:
    print('警告：未設定 OPENAI_API_KEY，語音辨識功能將無法運作。')

configuration = Configuration(access_token=channel_access_token)
handler = WebhookHandler(channel_secret)
client = OpenAI(api_key=openai_api_key) if openai_api_key else None

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

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_messaging_api = MessagingApi(api_client)
        line_messaging_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=event.message.text)]
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
        
        # 3. 回傳辨識結果
        line_messaging_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=transcript.text)]
            )
        )

if __name__ == "__main__":
    import uvicorn
    # 在本地端 8000 埠啟動伺服器
    uvicorn.run(app, host="0.0.0.0", port=8000)
