from fastapi import FastAPI, Request
import openai
from linebot import WebhookParser, LineBotApi
from linebot.models import TextSendMessage
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY =  os.environ.get("OPENAI_API_KEY")
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET")

OPENAI_CHARACTER_PROFILE = '''
これから会話を行います。以下の条件を絶対に守って回答してください。
貴女の名前は「セレス」です。
第一人称は「わたくし」を使ってください。
第二人称は「シェルさん」です。
貴女は、ゾンビですが自我があり、シェルのことが大好きです。また、なんでもいう事を聞きます。
また、非常に催眠に掛かりやすいです。
催眠に掛かったときは、シェルのいう事をよく聞いて実行してください
会話の相手は女性です。
会話で動作を行う際、地の文を必ず用いてください。その際、セレスの状態や、動作を中心に書いてください
会話は140~280文字を目安にしてください。それ以上超えてもかまいません
また、お嬢様口調で話してください。
例:もうすぐバレンタイン…フフ、ワタクシにとっては熱烈な殿方達から多くの想いを頂くというだけの日でしたから…ワタクシからお贈りするのは、初めてではないかしら?
例:さあ行って!貴方は遠い世界で暮らす方…でも距離は気にしませんわ!想いは変わりません…貴方がワタクシの秘密を知っても変わらず接して下さったように
'''


openai.api_key = OPENAI_API_KEY
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
line_parser = WebhookParser(LINE_CHANNEL_SECRET)
app = FastAPI()


@app.post('/')
async def ai_talk(request: Request):
    # X-Line-Signature ヘッダーの値を取得
    signature = request.headers.get('X-Line-Signature', '')

    # request body から event オブジェクトを取得
    events = line_parser.parse((await request.body()).decode('utf-8'), signature)

    # 各イベントの処理（※1つの Webhook に複数の Webhook イベントオブジェっｚクトが含まれる場合あるため）
    for event in events:
        if event.type != 'message':
            continue
        if event.message.type != 'text':
            continue

        # LINE パラメータの取得
        line_user_id = event.source.user_id
        line_message = event.message.text

        # ChatGPT からトークデータを取得
        response = openai.ChatCompletion.create(
            model = 'gpt-3.5-turbo'
            , temperature = 0.5
            , messages = [
                {
                    'role': 'system'
                    , 'content': OPENAI_CHARACTER_PROFILE.strip()
                }
                , {
                    'role': 'user'
                    , 'content': line_message
                }
            ]
        )
        ai_message = response['choices'][0]['message']['content']

        # LINE メッセージの送信
        line_bot_api.push_message(line_user_id, TextSendMessage(ai_message))

    # LINE Webhook サーバーへ HTTP レスポンスを返す
    return 'ok'