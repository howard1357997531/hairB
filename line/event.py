from linebot.models import *
from linebot import WebhookHandler, LineBotApi
from django.conf import settings
from mainapp.models import AdminSetting
from .models import Reservation
from .tool import text_bubble

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)

week_name = {
    "不設定": "",
    "星期一": "周一",
    "星期二": "周二",
    "星期三": "周三",
    "星期四": "周四",
    "星期五": "周五",
    "星期六": "周六",
    "星期日": "周日",
}
def admin_login(event):
    bubble = {
  "type": "bubble",
  "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "text",
        "text": "設定管理者",
        "weight": "bold",
        "size": "xl",
        "align": "center",
        "color": "#616161"
      },
      {
        "type": "button",
        "action": {
          "type": "uri",
          "label": "前往",
          "uri": "https://liff.line.me/2002009351-5Wwnn08j?name=admin-list"
        },
        "color": "#00897b",
        "style": "primary",
        "margin": "xl"
      }
    ],
    "backgroundColor": "#d7ccc8",
    "paddingBottom": "lg"
  }
}

    flex_message = FlexSendMessage(
        alt_text="設定管理者",
        contents=bubble
    )

    line_bot_api.reply_message(
        event.reply_token,
        flex_message
    )

def about_us_event(event):
    admin_setting = AdminSetting.objects.first()
    company_name = admin_setting.company_name
    company_phone = admin_setting.company_phone
    company_address = admin_setting.company_address
    can_reservation_time = admin_setting.can_reservation_time.split(",")
    rest_day_for_day = admin_setting.rest_day_for_day
    rest_day_for_week = admin_setting.rest_day_for_week
    # rest_day_for_day = "1,2"
    # rest_day_for_week = admin_setting.rest_day_for_week

    # sort
    rest_day_for_day = ','.join(map(str, sorted(map(int, rest_day_for_day.split(",")))))
    
    # 四種情況:
    # 公休日：無
    # 公休日：周一
    # 公休日：每月1,2號
    # 公休日：周一，每月1號
    if len(rest_day_for_day) != 0:
        if rest_day_for_week == "不設定":
            rest_day_for_day = "每月" + rest_day_for_day + "號"
        else:
            rest_day_for_day = "，每月" + rest_day_for_day + "號"

    can_reserve_time_text = f'{can_reservation_time[0]}:{can_reservation_time[1]} ~ {can_reservation_time[2]}:{can_reservation_time[3]}'
    rest_day_text = f"{week_name[rest_day_for_week]}{rest_day_for_day.replace(',', ', ')}"

    if rest_day_for_week == "不設定" and len(rest_day_for_day) == 0:
        rest_day_text = "無"
    
    text=f'''我們致力於提供最頂尖的美髮服務，讓每一位顧客都能在這裡找到屬於自己的時尚~

(我們的服務)
1️⃣剪髮：無論是時尚前衛的造型還是經典的修剪，我們的造型師都能根據您的需求，量身打造最適合您的髮型。

2️⃣染髮：使用高品質的染髮產品，保證顏色持久、健康亮麗，讓您的髮色充滿個性。

3️⃣燙髮：無論是自然卷、浪漫大波浪還是立體感強的造型，我們的技術都能讓您滿意。

4️⃣護髮：針對不同髮質提供專業的護理方案，從頭皮護理到深層修復，全面呵護您的秀髮。

(優質商品)
在時尚髮廊，我們不僅提供頂級的美髮服務，還為顧客精心挑選了各類優質美髮產品，包括：洗髮水、護髮素、修護精華...等等，也可以在 line 裡面直接做購買

(聯絡我們)
地址：{company_address}
電話：{company_phone}
營業時間：{can_reserve_time_text}
公休日：{rest_day_text}'''
    
    # 一進來會用文字方式回復你
    bubble = {
  "type": "bubble",
  "size": "kilo",
  "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "text",
        "text": f"💥 歡迎來到{company_name} 💥",
        "align": "center",
        "color": "#000000"
      },
      {
        "type": "text",
        "wrap": True,
        "text": text,
        "color": "#000000",
        "margin": "lg"
      }
    ],
    "paddingTop": "lg",
    "paddingBottom": "lg"
  },
  "styles": {
    "body": {
      "backgroundColor": "#d1ccca"
    },
    "footer": {
      "backgroundColor": "#d1ccca",
      "separator": True,
      "separatorColor": "#b3b3b3"
    }
  }
}
    text_message = FlexSendMessage(alt_text='髮廊介紹', contents=bubble)
    return line_bot_api.reply_message(event.reply_token, text_message)
    
def location_event(event):
    admin_setting = AdminSetting.objects.first()
    company_name = admin_setting.company_name
    company_address = admin_setting.company_address
    latitude = admin_setting.latitude
    longitude = admin_setting.longitude

    location_message = LocationSendMessage(
        title=company_name,
        address=company_address,
        latitude=latitude,
        longitude=longitude
    )
    line_bot_api.reply_message(
        event.reply_token,
        location_message)
    
def note_for_reservation(event):
    admin_setting = AdminSetting.objects.first()
    can_reservation_time = admin_setting.can_reservation_time.split(",")
    can_reservation_period = admin_setting.can_reservation_period
    today_reservation_limit = admin_setting.today_reservation_limit
    can_reserve_time_text = f'{can_reservation_time[0]}:{can_reservation_time[1]} ~ {can_reservation_time[2]}:{can_reservation_time[3]}'
    
    text = f'''(預約時段)
{can_reserve_time_text}

(可預約時期)
今日(不包括)開始往後算 {can_reservation_period} 天

(當日預約限制)
當日當下時間往後 {today_reservation_limit} 小時內的所有預約，顧客不得預約

(其他)
1. 每個帳號同一天只能預約一種服務
2. 若想取消預約，請點擊(我的預約)，裡面會顯示當日(包括)之後的所有預約，即可選擇想要取消的預約'''
    
    bubble = {
  "type": "bubble",
  "size": "kilo",
  "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "text",
        "text": "💥 預約注意 💥",
        "align": "center",
        "color": "#000000"
      },
      {
        "type": "text",
        "wrap": True,
        "text": text,
        "color": "#000000",
        "margin": "lg"
      }
    ],
    "paddingTop": "lg",
    "paddingBottom": "lg"
  },
  "styles": {
    "body": {
      "backgroundColor": "#d1ccca"
    },
    "footer": {
      "backgroundColor": "#d1ccca",
      "separator": True,
      "separatorColor": "#b3b3b3"
    }
  }
}
    text_message = FlexSendMessage(alt_text='預約注意', contents=bubble)
    return line_bot_api.reply_message(event.reply_token, text_message)

def latest_news(event):
    bubble = text_bubble('尚無最新消息，敬請期待')
    text_message = FlexSendMessage(alt_text='尚無最新消息，敬請期待', contents=bubble)
    return line_bot_api.reply_message(event.reply_token, text_message)

def more_information(event):
    bubble = text_bubble('尚無更多資訊，敬請期待')
    text_message = FlexSendMessage(alt_text='尚無更多資訊，敬請期待', contents=bubble)
    return line_bot_api.reply_message(event.reply_token, text_message)



