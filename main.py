import logging
from fastapi import FastAPI, Request
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import os
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage, BubbleContainer, ImageComponent, MessageAction, PostbackEvent
from datetime import datetime
from contents import messages
from linebot.models import TemplateSendMessage, CarouselTemplate
from dotenv import load_dotenv
import requests

app = FastAPI()

logging.basicConfig(level=logging.INFO)

load_dotenv()

# LINEの設定
line_bot_api = LineBotApi(os.environ.get('LINE_CHANNEL_ACCESS_TOKEN'))
handle = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET'))

# 環境変数から個々の認証情報を読み込む
google_client_email = os.environ.get('GOOGLE_CLIENT_EMAIL')
google_project_id = os.environ.get('GOOGLE_PROJECT_ID')
google_private_key_id = os.environ.get('GOOGLE_PRIVATE_KEY_ID')
google_private_key = os.environ.get('GOOGLE_PRIVATE_KEY').replace('\\n', '\n')

# 認証情報の辞書を作成
google_credentials = {
    "type": "service_account",
    "project_id": google_project_id,
    "private_key_id": google_private_key_id,
    "private_key": google_private_key,
    "client_email": google_client_email,
    "client_id": "",  # 必要に応じて設定
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": ""  # 必要に応じて設定
}

# Googleスプレッドシートの設定
scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_dict(google_credentials, scope)
client = gspread.authorize(creds)
gs = client.open_by_key(os.environ.get('GOOGLE_SPREADSHEET_KEY'))
sheet = gs.worksheet("users")
message_meta_db = gs.worksheet("message_meta_db")
message_data_db = gs.worksheet("message_data_db")
result_sheet = gs.worksheet("result")

home_url = os.environ.get('HOME_URL')

@app.get("/api/test")
async def test():
    url = f"{home_url}/api/webhook"  # 実際のAPIのURLに置き換えてください

    # APIに送信するデータ
    data = {
        'key1': 'value1',
    }

    # POSTリクエストを送信
    response = requests.post(url, json=data)
    print(response.text)

@app.post("/api/webhook")
async def line_webhook(request: Request):
    # リクエストヘッダーとボディを取得
    signature = request.headers.get('X-Line-Signature')
    if not signature:
        return {"status": "failed"}
    
    body = await request.body()
    
    # Webhookハンドラーを使用してイベントを処理
    try:
        handle.handle(body.decode(), signature)
    except InvalidSignatureError:
        return {"status": "Signature validation failed"}

    return {"status": "OK"}

@handle.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    text = event.message.text
    profile = line_bot_api.get_profile(user_id)
    # スプレッドシートを検索
    try:
        cell = sheet.find(user_id)
    except gspread.exceptions.CellNotFound:
        cell = None

    if cell:
        # ユーザーIDが一致する行を更新
        row = cell.row
    else:
        row = find_empty_row(sheet)
        
    message_id = int(sheet.cell(row, 2).value) if sheet.cell(row, 2).value else 1

    # 特定のメッセージをチェック
    if text == "【慰謝料計算をする】":
        message_id = 1
        # LINEプロファイルを取得
        line_name = profile.display_name

        # 現在の日時を取得
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        message_meta = get_data_by_id(message_id)
        reply_messages = create_reply_messages(message_meta["data"])
        line_bot_api.reply_message(event.reply_token, messages=reply_messages)
        
        # ユーザーID、メッセージID、LINE名、日時を入力
        sheet.update(f"A{row}:D{row}", [[user_id, message_id, line_name, now]])
    
    elif text == "【相談のご予約】":
        message_id = 29
        line_name = profile.display_name

        # 現在の日時を取得
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # ユーザーID、メッセージID、LINE名、日時を入力
        sheet.update(f"A{row}:D{row}", [[user_id, message_id, line_name, now]])
        
        message_meta = get_all_data_by_id(message_meta_db, message_id)
        reply_messages = create_reply_messages(message_meta["data_id"])
        line_bot_api.reply_message(event.reply_token, messages=reply_messages)
    else:

        current_message_meta = get_data_by_id(message_id)
        
        headers = get_header_row(sheet) 
        key = current_message_meta["key"]
        if "condition_keys" in current_message_meta:
            condition_keys = current_message_meta["condition_keys"]
            condition_ids = current_message_meta["condition_ids"]
            for condition_key, condition_id in zip(condition_keys, condition_ids):
                if text == condition_key:
                    next_message_meta = get_data_by_id(condition_id)
                    if key in headers and next_message_meta["key"] != "exception":
                        column_number = headers.index(key) + 1  # 列番号を取得
                        # 特定の列にデータを保存
                        sheet.update_cell(row, column_number, text)
                        # messageIdを更新
                        sheet.update_cell(row, 2, next_message_meta["id"])
                        
                    reply_messages = create_reply_messages(next_message_meta["data"])
                    line_bot_api.reply_message(event.reply_token, messages=reply_messages)
                    return
        
        next_message_meta = get_data_by_id(current_message_meta["next"])
        
        if key in headers:
            column_number = headers.index(key) + 1  # 列番号を取得
            # 特定の列にデータを保存
            sheet.update_cell(row, column_number, text)
        # messageIdを更新
        
        sheet.update_cell(row, 2, next_message_meta["id"])
        reply_messages = create_reply_messages(next_message_meta["data"])
        
        if next_message_meta["id"] == 24 :
            result_text = get_result_text(user_id)
            reply_messages.append(TextSendMessage(text=result_text))
        line_bot_api.reply_message(event.reply_token, messages=reply_messages)

        

@handle.add(PostbackEvent)
def handle_postback(event):
    # PostbackActionから送信されたデータを取得
    postback_data = event.postback.data
    parsed_data = dict(x.split('=') for x in postback_data.split('&'))
    value = parsed_data.get('value')
    id = parsed_data.get('id')
    key = parsed_data.get('key')
    reply_token = event.reply_token

    user_id = event.source.user_id

    # 特定のメッセージをチェック
    if value == "【慰謝料計算をする】":
        # LINEプロファイルを取得
        profile = line_bot_api.get_profile(user_id)
        line_name = profile.display_name
        
        message_id = 1

        # スプレッドシートを検索
        try:
            cell = sheet.find(user_id)
        except gspread.exceptions.CellNotFound:
            cell = None

        if cell:
            # ユーザーIDが一致する行を更新
            row = cell.row
        else:
            row = find_empty_row(sheet)

        # 現在の日時を取得
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # ユーザーID、メッセージID、LINE名、日時を入力
        sheet.update(f"A{row}:D{row}", [[user_id, message_id, line_name, now]])
    else :
        # LINEプロファイルを取得
        profile = line_bot_api.get_profile(user_id)

        # スプレッドシートを検索
        try:
            cell = sheet.find(user_id)
        except gspread.exceptions.CellNotFound:
            cell = None
        logging.info(cell)

        if cell:
            # ユーザーIDが一致する行を更新
            row = cell.row
        else:
            row = find_empty_row(sheet)
        
        logging.info(row)
        
        # スプレッドシートのヘッダーを取得
        headers = get_header_row(sheet)
        if key in headers:
            column_number = headers.index(key) + 1  # 列番号を取得
            # 特定の列にデータを保存
            sheet.update_cell(row, column_number, value)

    # ユーザーID、メッセージID、LINE名、日時を入力
    sheet.update(f"A{row}:D{row}", [[user_id, message_id, line_name, now]])
        
    line_bot_api.reply_message(reply_token, messages=[])
    # line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
    
def get_header_row(sheet):
    # 1行目のデータ（ヘッダー行）を取得
    return sheet.row_values(1)

def find_empty_row(sheet):
    # すべての行を取得
    all_rows = sheet.get_all_values()
    for idx, row in enumerate(all_rows):
        # 空白の行（すべてのセルが空）を見つけたら、その行番号を返す
        if all(cell == '' for cell in row):
            return idx + 1  # インデックスは0始まりなので1を加える
    return len(all_rows) + 1  # 空白の行がなければ、最後の行の次の行番号を返す

# def create_reply_messages(ids):
#     messages = []
#     for message_data_id in ids:
#         message_data = get_data_by_id(id)
#         if message_data["type"] == "text":
#             message = TextSendMessage(text=message_data["alt_text"])
#         elif message_data["type"] == "flex":
#             message = create_flex_message(message_data["alt_text"], message_data["images"], message_data["values"])
#         messages.append(message)
        
#     return messages
def create_reply_messages(data):
    messages = []
    for message_data in data:
        if message_data["type"] == "text":
            message = TextSendMessage(text=message_data["alt_text"])
        elif message_data["type"] == "flex":
            message = create_flex_message(message_data["alt_text"], message_data["images"], message_data["values"])
        messages.append(message)
        
    return messages

def get_all_data_by_id(sheet, search_id):
    # ヘッダー行（キー）を取得
    keys = sheet.row_values(1)

    # A列（ID列）で指定されたIDを検索
    try:
        cell = sheet.find(search_id, in_column=1)
    except gspread.exceptions.CellNotFound:
        return "ID not found"

    # 指定されたIDの行データを取得
    row_values = sheet.row_values(cell.row)

    # キーと値を対応付けた辞書を作成
    data_dict = dict(zip(keys, row_values))
    return data_dict

def get_data_by_id(id):
    reply_message_meta = next((obj for obj in messages.reply_message_metas if obj["id"] == id), None)
    return reply_message_meta

def create_flex_message(alt_text, images, values):
    bubbles = []
    for img, val in zip(images, values):
        bubble = {
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": f"{home_url}/{img}",
                "size": "full",
                "aspectRatio": "1:1",
                "aspectMode": "cover",
                "action": {
                    "type": "message",
                    "label": val,
                    "text": val
                }
            }
        }
        bubbles.append(bubble)
        
    message = FlexSendMessage(
        alt_text=alt_text,
        contents={
            "type": "carousel",
            "contents": bubbles
        }
    )
        
    return message

def get_result_text(user_id):
    result_data = get_all_data_by_id(result_sheet, user_id)
    
    if result_data["accidentType"] == "死亡":
        laywer_based_death_money = result_data["laywerBasedDeathMoney"]
        death_money = result_data["deathMoney"]
        laywer_based_death_lost_profits = result_data["laywerBasedDeathLostProfits"]
        death_lost_profits =  result_data["deathLostProfits"]
        laywer_based_total = result_data["laywerBasedTotal"]
        total = result_data["total"]
        difference = result_data["difference"]

        # メッセージを作成
        message = (
            f"診断結果\n"
            f"✓死亡慰謝料\n"
            f"（弁護士基準）{laywer_based_death_money}万円\n"
            f"（自賠責基準）{death_money}万円\n"
            f"✓死亡遺失利益\n"
            f"（弁護士基準）{laywer_based_death_lost_profits}万円\n"
            f"（自賠責基準）{death_lost_profits}万円\n"
            f"✓総額\n"
            f"（弁護士基準）{laywer_based_total}万円\n"
            f"（自賠責基準）{total}万円\n"
            f"自賠責基準の場合、慰謝料{total}万円のところ、弁護士に依頼することで{difference}万円増額の総額{laywer_based_total}万円受け取ることができる可能性があります。\n"
            f"※こちらの結果はあくまで目安となります。詳しくは弁護士にご相談ください。"
        )
    
    else :
        laywer_based_hospitalization_money = result_data["laywerBasedHospitalizationMoney"]
        hospitalization_money = result_data["hospitalizationMoney"]
        laywer_based_work_lost_money = result_data["laywerBasedWorkLostMoney"]
        work_lost_money =   result_data["workLostMoney"]
        laywer_based_aftereffect_money = result_data["laywerBasedAftereffectMoney"]
        aftereffect_money = result_data["aftereffectMoney"]
        laywer_based_lost_profits = result_data["laywerBasedLostProfits"]
        lost_profits = result_data["lostProfits"]
        laywer_based_total = result_data["laywerBasedTotal"]
        total = result_data["total"]
        difference = result_data["difference"]

        # メッセージを作成
        message = (
            f"診断結果\n"
            f"✓入通院慰謝料\n"
            f"（弁護士基準）{laywer_based_hospitalization_money}万円\n"
            f"（自賠責基準）{hospitalization_money}万円\n"
            f"✓休業損害\n"
            f"（弁護士基準）{laywer_based_work_lost_money}万円\n"
            f"（自賠責基準）{work_lost_money}万円\n"
            f"✓後遺障害慰謝料\n"
            f"（弁護士基準）{laywer_based_aftereffect_money}万円\n"
            f"（自賠責基準）{aftereffect_money}万円\n"
            f"✓逸失利益\n"
            f"（弁護士基準）{laywer_based_lost_profits}万円\n"
            f"（自賠責基準）{lost_profits}万円\n"
            f"✓総額\n"
            f"（弁護士基準）{laywer_based_total}万円\n"
            f"（自賠責基準）{total}万円\n"
            f"自賠責基準の場合、慰謝料{total}万円のところ、弁護士に依頼することで{difference}万円増額の総額{laywer_based_total}万円受け取ることができる可能性があります。\n"
            f"※こちらの結果はあくまで目安となります。詳しくは弁護士にご相談ください。"
        )
    
    return message

def get_death_result_text(user_id):
    result_data = get_all_data_by_id(result_sheet, user_id)
    # 各変数に値を割り当て
    laywer_based_death_money = result_data["laywerBasedDeathMoney"]
    death_money = result_data["deathMoney"]
    laywer_based_death_lost_profits = result_data["laywerBasedDeathLostProfits"]
    death_lost_profits =  result_data["deathLostProfits"]
    laywer_based_total = result_data["laywerBasedTotal"]
    total = result_data["total"]
    difference = result_data["difference"]

    # メッセージを作成
    message = (
        f"診断結果\n"
        f"✓死亡慰謝料\n"
        f"（弁護士基準）{laywer_based_death_money}万円\n"
        f"（自賠責基準）{death_money}万円\n"
        f"✓死亡遺失利益\n"
        f"（弁護士基準）{laywer_based_death_lost_profits}万円\n"
        f"（自賠責基準）{death_lost_profits}万円\n"
        f"✓総額\n"
        f"（弁護士基準）{laywer_based_total}万円\n"
        f"（自賠責基準）{total}万円\n"
        f"自賠責基準の場合、慰謝料{total}万円のところ、弁護士に依頼することで{difference}万円増額の総額{laywer_based_total}万円受け取ることができる可能性があります。\n"
        f"※こちらの結果はあくまで目安となります。詳しくは弁護士にご相談ください。"
    )
    
    return message