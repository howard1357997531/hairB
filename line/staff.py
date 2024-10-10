from linebot.models import *
from mainapp.models import LineUser, AdminSetting
from line.tool import text_bubble
from .tool import (this_month_calendar_format, next_month_calendar_format, get_all_weekday_in_month
    , get_year_month_of_next_month, week_name_change)
from copy import deepcopy
from datetime import datetime, timedelta
import re
import json
from .views import line_bot_api
import pytz  # Import the pytz library for timezone handling

# Set the timezone you want to use
desired_timezone = pytz.timezone('Asia/Taipei')
# brown = "#d1ccca"
brown = "#d7ccc8"
green = "#009688"
purple = "#7e57c2"
red = "#d32f2f"

# 整個日曆得 flex_message ，最後會把 calendar_data 放進
# calendar_flex_message["body"]["contents"][1]["contents"] = calendar_data
calendar_flex_message = {
  "type": "bubble",
  "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "text",
        "text": "2023年 10月",
        "weight": "bold",
        "color": "#a1887f",
        "size": "md"
      },
      {
        "type": "box",
        "layout": "vertical",
        "contents": [],
        "margin": "sm"
      }
    ]
  },
    "footer": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "text",
        "text": "紅色字:  公休日",
        "align": "start",
        "margin": "sm",
        "color": red,
        "weight": "bold",
        "offsetStart": "sm"
      },
      {
        "type": "text",
        "text": "綠色:  可預約日",
        "margin": "md",
        "color": green,
        "align": "start",
        "weight": "bold",
        "offsetStart": "sm"
      },
      {
        "type": "box",
        "layout": "horizontal",
        "contents": [
          {
            "type": "box",
            "layout": "vertical",
            "contents": [
              {
                "type": "text",
                "text": "滿",
                "align": "center",
                "color": "#ffffff",
                "size": "12px"
              }
            ],
            "width": "22px",
            "height": "22px",
            "cornerRadius": "50px",
            "backgroundColor": purple,
            "justifyContent": "center"
          },
          {
            "type": "text",
            "text": ":  預約已滿",
            "align": "start",
            "color": purple,
            "weight": "bold",
            "margin": "xs"
          }
        ],
        "paddingStart": "xs",
        "margin": "md"
      }
    ],
    "backgroundColor": "#d1ccca"
  },
  "styles": {
    "hero": {
      "separator": True
    }
  }
}

# 日曆
calendar_data = [
    {
      "type": "separator"
    },
    {
      "type": "box",
      "layout": "horizontal",
      "contents": [
        {
          "type": "text",
          "text": "日",
          "weight": "bold",
          "size": "sm",
          "align": "center",
          "offsetTop": "xs",
          "color": "#d32f2f"
        },
        {
          "type": "separator"
        },
        {
          "type": "text",
          "text": "一",
          "size": "sm",
          "align": "center",
          "offsetTop": "xs",
          "color": "#000000"
        },
        {
          "type": "separator"
        },
        {
          "type": "text",
          "text": "二",
          "size": "sm",
          "align": "center",
          "offsetTop": "xs",
          "color": "#000000"
        },
        {
          "type": "separator"
        },
        {
          "type": "text",
          "text": "三",
          "size": "sm",
          "align": "center",
          "offsetTop": "xs",
          "color": "#000000"
        },
        {
          "type": "separator"
        },
        {
          "type": "text",
          "text": "四",
          "size": "sm",
          "align": "center",
          "offsetTop": "xs",
          "color": "#000000"
        },
        {
          "type": "separator"
        },
        {
          "type": "text",
          "text": "五",
          "size": "sm",
          "align": "center",
          "offsetTop": "xs",
          "color": "#000000"
        },
        {
          "type": "separator"
        },
        {
          "type": "text",
          "text": "六",
          "size": "sm",
          "align": "center",
          "offsetTop": "xs",
          "color": "#000000"
        }
      ],
      "margin": "none",
      "spacing": "none",
      "paddingTop": "7px",
      "paddingBottom": "7px"
    },
    {
      "type": "separator"
    },
]

# 下個月日曆要用新的，不然資料會被重複修改
calendar_flex_message2 = {
  "type": "bubble",
  "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "text",
        "text": "2023年 10月",
        "weight": "bold",
        "color": "#a1887f",
        "size": "md"
      },
      {
        "type": "box",
        "layout": "vertical",
        "contents": [],
        "margin": "sm"
      }
    ]
  },
    "footer": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "text",
        "text": "紅色字:  公休日",
        "align": "start",
        "margin": "sm",
        "color": red,
        "weight": "bold",
        "offsetStart": "sm"
      },
      {
        "type": "text",
        "text": "綠色:  可預約日",
        "margin": "md",
        "color": green,
        "align": "start",
        "weight": "bold",
        "offsetStart": "sm"
      },
      {
        "type": "box",
        "layout": "horizontal",
        "contents": [
          {
            "type": "box",
            "layout": "vertical",
            "contents": [
              {
                "type": "text",
                "text": "滿",
                "align": "center",
                "color": "#ffffff",
                "size": "12px"
              }
            ],
            "width": "22px",
            "height": "22px",
            "cornerRadius": "50px",
            "backgroundColor": purple,
            "justifyContent": "center"
          },
          {
            "type": "text",
            "text": ":  預約已滿",
            "align": "start",
            "color": purple,
            "weight": "bold",
            "margin": "xs"
          }
        ],
        "paddingStart": "xs",
        "margin": "md"
      }
    ],
    "backgroundColor": "#d1ccca"
  },
  "styles": {
    "hero": {
      "separator": True
    }
  }
}

# 日曆
calendar_data2 = [
    {
      "type": "separator"
    },
    {
      "type": "box",
      "layout": "horizontal",
      "contents": [
        {
          "type": "text",
          "text": "日",
          "weight": "bold",
          "size": "sm",
          "align": "center",
          "offsetTop": "xs",
          "color": "#d32f2f"
        },
        {
          "type": "separator"
        },
        {
          "type": "text",
          "text": "一",
          "size": "sm",
          "align": "center",
          "offsetTop": "xs",
          "color": "#000000"
        },
        {
          "type": "separator"
        },
        {
          "type": "text",
          "text": "二",
          "size": "sm",
          "align": "center",
          "offsetTop": "xs",
          "color": "#000000"
        },
        {
          "type": "separator"
        },
        {
          "type": "text",
          "text": "三",
          "size": "sm",
          "align": "center",
          "offsetTop": "xs",
          "color": "#000000"
        },
        {
          "type": "separator"
        },
        {
          "type": "text",
          "text": "四",
          "size": "sm",
          "align": "center",
          "offsetTop": "xs",
          "color": "#000000"
        },
        {
          "type": "separator"
        },
        {
          "type": "text",
          "text": "五",
          "size": "sm",
          "align": "center",
          "offsetTop": "xs",
          "color": "#000000"
        },
        {
          "type": "separator"
        },
        {
          "type": "text",
          "text": "六",
          "size": "sm",
          "align": "center",
          "offsetTop": "xs",
          "color": "#000000"
        }
      ],
      "margin": "none",
      "spacing": "none",
      "paddingTop": "7px",
      "paddingBottom": "7px"
    },
    {
      "type": "separator"
    },
]

def next_month_calendar(date_exceeded, next_month_has_schedule_list, 
    next_month_full_schedule_list, action):
    admin_setting = AdminSetting.objects.all().first()
    today = datetime.now(desired_timezone)

    # 取得下個月的年、月
    current_year = today.year
    current_month = today.month
    next_month_year, next_month = get_year_month_of_next_month(current_year, current_month)

    # 日曆第一排首日的 index，下個月最後一天日期
    first_day_index, last_day_of_next_month = next_month_calendar_format()

    # 下個月最後一天之前，總共有幾個格子在日曆(包括前面空白的格子)
    total_box_before_last_day = first_day_index + last_day_of_next_month

    # 可預約日期(使用 date_exceeded 天數)
    available_reservation_period = date_exceeded
    
    # 休息日(星期制) output: [] or [1, 5, 8]
    rest_day_for_week_value = admin_setting.rest_day_for_week
    if rest_day_for_week_value == "不設定":
        rest_day_for_week = []
    else:
        week_index = week_name_change[rest_day_for_week_value]
        # 若為'星期一'，會取得下個月所有星期一的日期 [6, 13, 20, 27]
        rest_day_for_week = get_all_weekday_in_month("next month", week_index)
    
    # 休息日(天數制) output: [] or [1, 5, 8]
    rest_day_for_day = [] if not admin_setting.rest_day_for_day  \
      else list(map(int, admin_setting.rest_day_for_day.split(',')))
    
    # 把 '星期制' '天數制' 兩者重複天數消除
    rest_day_list = list(set(rest_day_for_week + rest_day_for_day))

    # flex_message 星期的格子
    week = [       
          {
            "type": "box",
            "layout": "horizontal",
            "contents": [],
            "margin": "none",
            "spacing": "none",
            "paddingTop": "7px",
            "paddingBottom": "7px"
          },
          {
            "type": "separator"
          }
        ]
    
    # 要把 total_box_before_last_day 修正成7的倍數(ex: 若為8(超過7)會修正成14)
    # 這樣做是因為日曆都是7天一行
    total_box_in_seven_times = total_box_before_last_day if total_box_before_last_day % 7 == 0 \
              else total_box_before_last_day + (7 - (total_box_before_last_day % 7))
    day_boxs = []

    print('rest_day_list(next): ', rest_day_list)
    print('total_box_in_seven_times(next): ', total_box_in_seven_times)

    for box_index in range(total_box_in_seven_times):
        # 如果 day 小於 first_day_index 為 "0"，"0"表示不顯示字(因為一定小於1，第一天)
        day_str = str(box_index - first_day_index + 1) if box_index >= first_day_index else "0"
        # 不是在日期上的格子，字一律為白色(跟背景一樣)
        color = "#000000" if first_day_index <= box_index < total_box_before_last_day else "#ffffff"
        background_color = "#ffffff"
        weight = "regular"
        day = int(day_str)

        # day 在下個月第一天到可預約時段內 和 此為設計師有排班的日期，背景為綠色
        # 因是下一個月一定會從第一天開始
        if (first_day_index <= box_index < first_day_index + available_reservation_period
           and day in next_month_has_schedule_list):
            color = "#ffffff"
            background_color = green

        # day 在預約已滿日內
        if day in next_month_full_schedule_list:
            color = "#ffffff"
            day_str = "滿"
            background_color = purple

        # day 在公休日內
        if day in rest_day_list:
            weight = "bold"
            color = red
            background_color = "#ffffff"

        # flex_message 日期的格子
        day_box = [
          {
            "type": "box",
            "layout": "vertical",
            "contents": [
              {
                "type": "box",
                "layout": "vertical",
                "contents": [
                  {
                    "type": "text",
                    "text": day_str,
                    "weight": weight,
                    "align": "center",
                    "color": color,
                    "size": "12px"
                  }
                ],
                "width": "22px",
                "height": "22px",
                "cornerRadius": "50px",
                "backgroundColor": background_color,
                "justifyContent": "center",
                "alignItems": "center"
              }
            ],
            "justifyContent": "center",
            "alignItems": "center",
          },
          {
            "type": "separator"
          },
        ]

        # 日期在有數字的格子內先全部加action，下面會再修改可預約時段的內容
        if first_day_index <= box_index < total_box_before_last_day:
            warning = '不能預約'
            # 新增 action 為 message，text: 不能預約
            # day 要修正(假設 5/1 在第一排 index = 3，會顯示 5/3)
            day_box[0]["action"] = {
              "type": "message",
              "label": f"{next_month}/{day} {warning}",
              "text": f"{next_month}/{day} {warning}"
            }

        # 如果日期在可預約時段(因為這裡是下一個月的，一定會從第一天開始)
        # day 必須在下個月所有的排班日期內 day in next_month_has_schedule_list
        if (first_day_index <= box_index < first_day_index + available_reservation_period
            and day in next_month_has_schedule_list):
            if day in next_month_full_schedule_list:
              warning = '預約已滿'
              day_box[0]["action"] = {
                "type": "message",
                "label": f"{next_month}/{day} {warning}",
                "text": f"{next_month}/{day} {warning}"
                }
            else:
              day_box[0]["action"] = {
                "type": "postback",
                "label": f"已選擇{next_month}/{day}",
                "data": action + f"date={next_month_year}/{next_month}/{day}",
                "displayText": f"已選擇{next_month}/{day}"
              }

        # 公休日
        if day in rest_day_list:
            day_box[0]["action"] = {
              "type": "message",
              "label": f"{next_month}/{day} 公休日",
              "text": f"{next_month}/{day} 公休日"
            }
        
        day_boxs.extend(day_box)

        # 每七天存一次
        if (box_index + 1) % 7 == 0:
            week_copy = deepcopy(week)
            week_copy[0]["contents"] = day_boxs
            # 一個禮拜的資料存完之後和 separator 一起 extend 到 calendar_data
            calendar_data2.extend(week_copy)
            day_boxs = []  # 清空
    
    # 修正日曆 title 的年月
    calendar_flex_message2["body"]["contents"][0]["text"] = f"{next_month_year}年 {next_month}月"
    # 最後把整個 calendar_data 放進 calendar_flex_message 的 contents 裡面
    calendar_flex_message2["body"]["contents"][1]["contents"] = calendar_data2
    
    return calendar_flex_message2

def month_calendar(event, has_schedule_list, full_schedule_list, action):
    admin_setting = AdminSetting.objects.all().first()
    today = datetime.now(desired_timezone)

    # 日曆第一排首日的 index，本月最後一天日期
    first_day_index, last_day_of_this_month = this_month_calendar_format()

    # 本月最後一天之前，總共有幾個格子在日曆(包括前面空白的格子)
    total_box_before_last_day = first_day_index + last_day_of_this_month

    # 可預約日期(當日也算)
    available_reservation_period = int(admin_setting.can_reservation_period)
    # available_reservation_period = 50

    # 如果(當日 + 期間)大於本月最後一天
    check_has_next_month = today.day + available_reservation_period - 1 > last_day_of_this_month
    # 若'可預約時期'超過本月最後一天，取得超過的天數
    date_exceeded = today.day + available_reservation_period - 1 - last_day_of_this_month    

    # 取得設計師本月和下個月所有'有排班'的日期的list [1, 2, 28]
    this_month_has_schedule_list, next_month_has_schedule_list = has_schedule_list

    # 取得本月和下個月所有預約已滿日的list [5, 21]
    this_month_full_schedule_list, next_month_full_schedule_list = full_schedule_list
    
    # 休息日(星期制) output: [] or [6, 13, 20, 27]
    rest_day_for_week_value = admin_setting.rest_day_for_week
    if rest_day_for_week_value == "不設定":
        rest_day_for_week = []
    else:
        week_index = week_name_change[rest_day_for_week_value]
        # 若為'星期一'，會取得這個月所有星期一的日期 [6, 13, 20, 27]
        rest_day_for_week = get_all_weekday_in_month("this month", week_index)
   
    # 休息日(天數制) output: [] or [1, 5, 8]
    rest_day_for_day = [] if not admin_setting.rest_day_for_day \
      else list(map(int, admin_setting.rest_day_for_day.split(',')))
    
    # 把 '星期制' '天數制' 兩者重複天數消除
    rest_day_list = list(set(rest_day_for_week + rest_day_for_day))

    # flex_message 星期的格子
    week = [       
          {
            "type": "box",
            "layout": "horizontal",
            "contents": [],
            "margin": "none",
            "spacing": "none",
            "paddingTop": "7px",
            "paddingBottom": "7px"
          },
          {
            "type": "separator"
          }
        ]
    
    # 要把 total_box_before_last_day 修正成7的倍數(ex: 若為8(超過7)會修正成14)
    # 這樣做是因為日曆都是7天一行
    total_box_in_seven_times = total_box_before_last_day if total_box_before_last_day % 7 == 0 \
              else total_box_before_last_day + (7 - (total_box_before_last_day % 7))
    day_boxs = []

    print(check_has_next_month, date_exceeded)
    print('has_schedule_list: ', has_schedule_list)
    print('full_schedule_list: ', full_schedule_list)
    print('rest_day_list(this): ', rest_day_list)
    print('total_box_in_seven_times(this): ', total_box_in_seven_times)

    for box_index in range(total_box_in_seven_times):
        # 如果 day 小於 first_day_index 為 "0"，"0"表示不顯示字(因為一定小於1，第一天)
        day_str = str(box_index - first_day_index + 1) if box_index >= first_day_index else "0"
        # 不是在日期上的格子，字一律為白色(跟背景一樣)
        color = "#000000" if first_day_index <= box_index < total_box_before_last_day else "#ffffff"
        background_color = "#ffffff"
        weight = "regular"
        day = int(day_str)

        # day 在公休日內
        if day in rest_day_list:
            weight = "bold"
            color = red
            background_color = "#ffffff"
        
        # day 在預約已滿日內
        elif day in this_month_full_schedule_list and day > 11:
            color = "#ffffff"
            day_str = "滿"
            background_color = purple

        # day 在今日日期到可預約時段內 和 此為設計師有排班的日期，背景為綠色
        elif (today.day <= day < today.day + available_reservation_period
            and day in this_month_has_schedule_list):
            color = "#ffffff"
            background_color = green

        # flex_message 日期的格子
        day_box = [
          {
            "type": "box",
            "layout": "vertical",
            "contents": [
              {
                "type": "box",
                "layout": "vertical",
                "contents": [
                  {
                    "type": "text",
                    "text": day_str,
                    "weight": weight,
                    "align": "center",
                    "color": color,
                    "size": "12px"
                  }
                ],
                "width": "22px",
                "height": "22px",
                "cornerRadius": "50px",
                "backgroundColor": background_color,
                "justifyContent": "center",
                "alignItems": "center"
              }
            ],
            "justifyContent": "center",
            "alignItems": "center",
          },
          {
            "type": "separator"
          },
        ]

        # 公休日
        if day in rest_day_list:
            day_box[0]["action"] = {
              "type": "message",
              "label": f"{today.month}/{day} 公休日",
              "text": f"{today.month}/{day} 公休日"
            }

        # 如果日期在可預約時段 和 此為設計師有排班的日期
        # day 必須在本月所有的排班日期內 day in this_month_has_schedule_list
        elif (today.day <= day < today.day + available_reservation_period 
           and day in this_month_has_schedule_list):
            # day 在預約已滿日
            if day in this_month_full_schedule_list:
              warning = '預約已滿'
              day_box[0]["action"] = {
                "type": "message",
                "label": f"{today.month}/{day} {warning}",
                "text": f"{today.month}/{day} {warning}"
                }
            else:
              day_box[0]["action"] = {
                "type": "postback",
                "label": f"已選擇{today.month}/{day}",
                "data": action + f"date={today.year}/{today.month}/{day}",
                "displayText": f"已選擇{today.month}/{day}"
              }

        # 日期在有數字的格子內先全部加action，下面會再修改可預約時段的內容
        elif (first_day_index <= box_index < total_box_before_last_day):
            warning = '不能預約'
            # 新增 action 為 message，text: 不能預約
            # day 要修正(假設 5/1 在第一排 index = 3，會顯示 5/3)
            day_box[0]["action"] = {
              "type": "message",
              "label": f"{today.month}/{day} {warning}",
              "text": f"{today.month}/{day} {warning}"
            }

        day_boxs.extend(day_box)

        # 每七天存一次
        if (box_index + 1) % 7 == 0:
            week_copy = deepcopy(week)
            week_copy[0]["contents"] = day_boxs
            # 一個禮拜的資料存完之後和 separator 一起 extend 到 calendar_data
            calendar_data.extend(week_copy)
            day_boxs = []  # 清空
    
    # 修正日曆 title 的年月
    calendar_flex_message["body"]["contents"][0]["text"] = f"{today.year}年 {today.month}月"
    # 最後把整個 calendar_data 放進 calendar_flex_message 的 contents 裡面
    calendar_flex_message["body"]["contents"][1]["contents"] = calendar_data
    # check_has_next_month = False
    # 若可預約時期有跨月會顯示兩個日曆
    if check_has_next_month:
        next_month_calendar_flex_message = next_month_calendar(date_exceeded,\
          next_month_has_schedule_list, next_month_full_schedule_list, action)

        flex_message = FlexSendMessage(
            alt_text="本月預約",
            contents={
              "type": "carousel",
              "contents": [calendar_flex_message, next_month_calendar_flex_message]
            }
        )
    else:
        # 這樣單個顯示(單月)才不會顯示拉條
        flex_message = FlexSendMessage(
            alt_text="本月預約",
            contents=calendar_flex_message
        )

    bubble = text_bubble('請選擇預約日期~')
    text_message = FlexSendMessage(alt_text='請選擇預約日期~', contents=bubble)

    line_bot_api.reply_message(
        event.reply_token,
        [text_message, flex_message]
    )
    
