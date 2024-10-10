from linebot.models import *
from linebot import WebhookHandler, LineBotApi
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from urllib.parse import parse_qsl

from .models import *
from mainapp.models import LineUser, AdminSetting, Staff, StaffSchedule, StaffCommonSetting
from mainapp.serializers import StaffScheduleSerializer, StaffCommonSettingSerializer
from line.tool import text_bubble
from .tool import  parse_schedule, parse_two_pair_list, get_year_month_of_next_month
from .staff import month_calendar
import datetime
import pytz  # Import the pytz library for timezone handling

# Set the timezone you want to use
desired_timezone = pytz.timezone('Asia/Taipei')

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
brown = "#d7ccc8"

services = {
    1: {
        'category': '剪髮',
        'img_url': '',
        'title': '剪髮+洗',
        'description': '',
        'price': 399,
        'post_url': 'https://linecorp.com'
    },
    2: {
        'category': '剪髮',
        'img_url': '',
        'title': '剪髮+洗(健康洗)',
        'description': '',
        'price': 499,
        'post_url': 'https://linecorp.com'
    },
    3: {
        'category': '洗髮',
        'img_url': '',
        'title': '一般洗',
        'description': '',
        'price': 150,
        'post_url': 'https://linecorp.com'
    },
    4: {
        'category': '洗髮',
        'img_url': '',
        'title': '健康洗',
        'description': '',
        'price': 250,
        'post_url': 'https://linecorp.com'
    },
    5: {
        'category': '燙髮',
        'img_url': 'https://i.imgur.com/1TydqUs.jpg',
        'title': '柔軟波浪捲髮',
        'description': '推薦給追求慵懶蓬鬆捲髮的人，基本造型都已大致燙成，不需再花時間多做整理，帶點隨興自在的氛圍。幾乎不挑臉型的簡約感捲髮，無論任何人都可以輕鬆挑戰。',
        'price': 2000,
        'post_url': 'https://linecorp.com'
    },
    6: {
        'category': '燙髮',
        'img_url': 'https://i.imgur.com/nGZkwqg.jpg',
        'title': '男孩風髮夾燙',
        'description': '組合男孩風髮型與髮夾燙的最新潮流捲髮，形狀有別於一般的螺旋捲髮，與纏繞於髮捲的螺旋狀燙髮不同，不管長度多短都可以順利上捲，特色是從根部創造出自然捲曲線條。',
        'price': 2200,
        'post_url': 'https://linecorp.com'
    },
    7: {
        'category': '燙髮',
        'img_url': 'https://i.imgur.com/nPfVTML.jpg',
        'title': '中分ｘ捲髮',
        'description': '隨著韓系男生捲髮，大家也逐漸接受大膽中分頭，打造栩栩如生的髮流，是爽朗無比的男生髮型。兩側和頸後一無反顧的推剪，頭頂至瀏海的秀髮則保留一點長度，只加重瀏海部分捲度，其他部分卻維持蓬鬆感，就是這個髮型的關鍵。',
        'price': 2500,
        'post_url': 'https://linecorp.com'
    },
    8: {
        'category': '燙髮',
        'img_url': 'https://i.imgur.com/3xIzfx1.jpg',
        'title': '三七分ｘ髮夾燙',
        'description': '最受短髮男性熱烈歡迎的髮夾燙！會這麼人氣的理由是因為頭髮長度只要有5cm就可以輕鬆燙出，造福了所有短髮男子。讓超短髮的人也能輕易實現捲髮造型。接著只要將頭髮弄成三七分，瀏海往旁邊撥、露出額頭，清新感與時髦感便一次入手。',
        'price': 1800,
        'post_url': 'https://linecorp.com'
    },
    9: {
        'category': '護髮',
        'img_url': 'https://i.imgur.com/vgTu2L0.png',
        'title': '日本哥德式護髮',
        'description': '日本哥德式護髮屬於日系結構四劑式護髮，大量的CMC可使髮質滑順，3種不同保濕因子補充髮芯流失的水分，搭配霧化奈米導入鎖住養分，以下根據4劑用途簡單說明：\n\n\
第一劑會以按摩方式使毛鱗片吸收精華，深層修護毛鱗片。\n\
第二劑將精華導入毛鱗片，保持髮質水分滋潤不流失。\n\
第三劑讓膠原蛋白在頭髮表層形成保護膜，髮質柔順不打結。\n\
最後的第四劑為安瓶，可作為日常居家護理使用。',
        'price': 2000,
        'post_url': 'https://linecorp.com'
    },
    10: {
        'category': '護髮',
        'img_url': 'https://i.imgur.com/mpF6ZNL.png',
        'title': '榖洛絲五劑式護髮',
        'description': '日本原裝進口的榖洛絲五劑式護髮，一次擁有柔順感、光澤度與持久性，填補水蛋白，就像為你的髮絲上一層鍍膜般光滑好摸，號稱護髮界的香奈兒，護髮維持時間在本篇介紹的5種護髮推薦產品中是最久的種類，護髮含洗髮時間約1.5小時，維持時間3~8週，若因為頻繁燙染導致髮尾彈性疲乏，脆弱易斷，那麼深層護髮推薦榖洛絲五劑式護髮，鞏固髮質，兼具改善枯黃毛燥髮質並增添光澤的優點。\n\n\
第1階段：加強滲透-含有特殊雙子行胺基酸、神經醯胺酸，可使受損髮含水量恢復至健康狀態，賦予頭髮彈潤觸感。\n\
第2階段：獨家技術-使用羊毛角蛋白胺基酸與燙髮劑專用α-角蛋白，建立階段1與階段2的架橋作用，完美結合髮芯之中。\n\
第3階段：修復之鑰-添加高保濕滲透成分，加速胺基酸與階段1和階段2結合反應，軟化角質層並柔韌髮絲。\n\
第4階段：溫和淨化-無添加矽靈的胺基酸洗髮精溫和不刺激，使用8種胺基酸黃金比例配方修復受損髮絲。\n\
第5階段：水潤光澤-最後使用高保濕因子成分護髮，將髮芯包覆鎖水呈現柔潤光澤感。',
        'price': 2500,
        'post_url': 'https://linecorp.com'
    },
    11: {
        'category': '護髮',
        'img_url': 'https://i.imgur.com/6PzQ2pe.png',
        'title': '京喚羽5劑式護髮',
        'description': '具備專利技術，凝聚結合技術，有效改善護髮產品無法有效被吸收的情況，讓護髮養分鎖在頭髮本質內，\
使髮質煥然新生！護髮功能3 in 1效果更完整，加強結構，預防頭髮斷裂，達到油水保濕、外層滑順、保有頭髮光澤度的效果，\
毛髮結構強度恢復高達140%，減少毛髮乾燥打結的情況。內部含有諾貝爾得獎成分C60 Fullerene富勒烯，是髮質凍齡關鍵，\
對抗自由基有效預防老化，可有效防禦紫外線傷害！4大角蛋白成分，修護受損髮及強韌髮絲，擁有持久性的修護效果。\
京喚羽護髮適合使用對象包含漂髮過的髮質，或長期染、燙髮，高度受損的髮質，或是海水侵蝕、太陽長期照射頭髮的情況，都很適合喔！',
        'price': 3000,
        'post_url': 'https://linecorp.com'
    },
}

# 判斷會有幾個 flex_message
def check_flex_message_count(count):
    # 取整數
    take_integer = count // 10
    # 取餘數 (備註: 4 % 10 = 4)
    take_remainder = count % 10

    # 小於10
    if count < 10:
        carousel_count = 1
    # 10的倍數(若有10個還是算一個flex_message)
    elif take_remainder == 0:
        carousel_count = take_integer
    # 大於10且不是10倍數
    else:
        carousel_count = take_integer + 1
    
    return carousel_count

# 預約服務
def service_category_event(event):
    bubble = text_bubble('請選擇預約服務~')
    text_message = FlexSendMessage(alt_text='請選擇預約服務~', contents=bubble)
    
    # add_service_id 是需要加購的服務ID
    image_carousel_template_message = TemplateSendMessage(
        alt_text='預約服務',
        template=ImageCarouselTemplate(
            columns=[
                ImageCarouselColumn(
                    image_url='https://i.imgur.com/wsaCcSZ.jpg',
                    # 當在圖片上有動作時，會傳 'action=service&category=按摩調理' 到伺服器
                    action=PostbackAction(
                        label='剪髮',
                        display_text='想了解剪髮',
                        data='action=service&category=剪髮&add_service_id=0'
                    )
                ),
                ImageCarouselColumn(
                    image_url='https://i.imgur.com/9UyToxU.jpg',
                    action=PostbackAction(
                        label='洗髮',
                        display_text='想了解洗髮',
                        data='action=service&category=洗髮&add_service_id=0'
                    )
                ),
                ImageCarouselColumn(
                    image_url='https://i.imgur.com/4bEkmvO.jpg',
                    action=PostbackAction(
                        label='燙髮',
                        display_text='想了解燙髮',
                        data='action=service&category=燙髮&add_service_id=0'
                    )
                ),
                ImageCarouselColumn(
                    image_url='https://i.imgur.com/gSLyzrg.jpg',
                    action=PostbackAction(
                        label='護髮',
                        display_text='想了解護髮',
                        data='action=service&category=護髮&add_service_id=0'
                    )
                )
            ]
        )
    )
    
    line_bot_api.reply_message(
        event.reply_token,
        [text_message, image_carousel_template_message])

# 選擇預約服務  
def select_service_event(event):
    # action=service&category=剪髮&add_service_id=0
    # print('data-original: ',event.postback.data)       # action=select_date&service_id=1&add_service_id=0 (type:str)
    # print('parse_qsl ',parse_qsl(event.postback.data)) # [('action', 'select_date'), ('service_id', '1'), ('add_service_id', '0')]
    data = dict(parse_qsl(event.postback.data))
    print('service:', data)
    bubbles = []

    for serviceId in services:
        if services[serviceId]['category'] == data['category']:
            service = services[serviceId]
            if data['category'] in ['剪髮', '洗髮']:
                bubble = {
                    "type": "bubble",
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                        {
                            "type": "text",
                            "text": service['title'],
                            "size": "xl",
                            "weight": "bold"
                        },
                        {
                            "type": "text",
                            "text": f"$ {service['price']}",
                            "align": "start",
                            "size": "xl",
                            "margin": "lg"
                        }
                        ],
                        "spacing": "sm"
                    },
                    "footer": {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                        {
                            "type": "button",
                            "action": {
                            "type": "postback",
                            "label": "加購護髮",
                            "data": f"action=service&category=護髮&service_id={serviceId}&add_service_id=add",
                            "displayText": "加購護髮"
                            },
                            "style": "secondary",
                            "color": "#78909c"
                        },
                        {
                            "type": "button",
                            "action": {
                            "type": "postback",
                            "label": "預約",
                            "data": f"action=select_designer&service_id={serviceId}&add_service_id=0",
                            "displayText": f"我想預約【{service['title']}】"
                            },
                            "style": "secondary",
                            "color": "#a1887f"
                        }
                        ],
                        "spacing": "md"
                    },
                    "styles": {
                        "body": {
                        "backgroundColor": brown
                        },
                        "footer": {
                        "backgroundColor": brown
                        }
                    }
                }
            elif data['category'] in ['燙髮', '護髮']:
                # add_service_id 要加購的東西的id(不是加購項目的id)
                description = service['description'] if len(service['description']) < 72 else service['description'][:73] + '...'
                
                if data['category'] == '燙髮':
                    label = "加購護髮"
                    color = "#78909c"
                    displayText = "加購護髮"
                    detail_action = f"action=service_detail&category=燙髮&service_id={serviceId}&add_service_id=0"
                    add_action = f"action=service&category=護髮&service_id={serviceId}&add_service_id=add"
                elif  data['category'] == '護髮':
                    # data['add_service_id'] == '0' 表示一開始就是按護髮
                    # data['add_service_id'] == 'add' 表示從其他地方加購過來
                    label = "預約" if data['add_service_id'] == '0' else "加購"
                    color = "#a1887f" if data['add_service_id'] == '0' else "#78909c"
                    service_id = serviceId if data['add_service_id'] == '0' else data['service_id']
                    add_service_id = '0' if data['add_service_id'] == '0' else serviceId
                    displayText = f"我想預約【{service['title']}】" if data['add_service_id'] == '0' \
                        else f"我想預約【{services[int(service_id)]['title']}】\n加購: 【{service['title']}】"
                    detail_action = f"action=service_detail&category=護髮&service_id={service_id}&add_service_id={add_service_id}"
                    add_action = f"action=select_designer&service_id={service_id}&add_service_id={add_service_id}" 
            
                bubble = {
                    "type": "bubble",
                    "hero": {
                        "type": "image",
                        "size": "full",
                        "aspectRatio": "20:13",
                        "aspectMode": "cover",
                        "url": service['img_url']
                    },
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "sm",
                        "contents": [
                        {
                            "type": "text",
                            "text": service['title'],
                            "wrap": True,
                            "weight": "bold",
                            "size": "xl",
                            "align": "center"
                        },
                        {
                            "type": "text",
                            "text": description,
                            "margin": "lg",
                            "wrap": True
                        },
                        {
                            "type": "text",
                            "text": f"$ {service['price']}",
                            "align": "center",
                            "size": "xl",
                            "margin": "xl",
                            "offsetEnd": "sm"
                        }
                        ]
                    },
                    "footer": {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "sm",
                        "contents": [
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                            {
                                "type": "button",
                                "action": {
                                "type": "postback",
                                "label": "詳細資訊",
                                "data": detail_action,
                                "displayText": "詳細資訊"
                                },
                                "color": "#9e9e9e",
                                "style": "secondary"
                            },
                            {
                                "type": "button",
                                "action": {
                                "type": "postback",
                                "label": label,
                                "data": add_action,
                                "displayText": displayText
                                },
                                "color": color,
                                "style": "secondary"
                            }
                            ],
                            "spacing": "md"
                        },
                        {
                            "type": "button",
                            "action": {
                            "type": "postback",
                            "label": "預約",
                            "data": f"action=select_designer&service_id={serviceId}&add_service_id=0",
                            "displayText": f"我想預約【{service['title']}】"
                            },
                            "color": "#a1887f",
                            "style": "secondary",
                            "margin": "md"
                        }
                        ]
                    },
                    "styles": {
                        "body": {
                        "backgroundColor": brown
                        },
                        "footer": {
                        "backgroundColor": brown
                        }
                    }
                }

            #刪除 bubble['footer']["contents"] 第三個
            if data['category'] == '護髮':
                temp = bubble['footer']["contents"]
                temp.pop(1)
                bubble['footer']["contents"] = temp

            bubbles.append(bubble)

    # data['add_service_id'] == '0' 表示沒加購
    alt_text = '請選擇預約項目' if data['add_service_id'] == '0' else '請選擇加購項目'
    flex_message = FlexSendMessage(
        alt_text=alt_text,
        contents={
          "type": "carousel",
          "contents": bubbles
        }
    )

    line_bot_api.reply_message(
        event.reply_token,
        flex_message)

# 服務細節
def service_detail_event(event):
    data = dict(parse_qsl(event.postback.data))
    print('service_detail', data)
    
    category = data['category']
    service_id = data['service_id']
    add_service_id = data['add_service_id']
    # 顯判斷是來自預約還是加購
    detail_id = data['service_id'] if add_service_id == '0' else add_service_id
    bubble = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
            {
                "type": "image",
                "url": services[int(detail_id)]['img_url'],
                "size": "full",
                "aspectMode": "cover",
                "aspectRatio": "2:3",
                "gravity": "top"
            },
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                {
                    "type": "text",
                    "text": services[int(detail_id)]['title'],
                    "color": "#ffffff",
                    "align": "center",
                    "size": "xs",
                    "offsetTop": "3px",
                    "gravity": "top"
                }
                ],
                "position": "absolute",
                "cornerRadius": "20px",
                "offsetTop": "18px",
                "backgroundColor": "#78909c",
                "offsetStart": "15px",
                "height": "25px",
                "maxWidth": "120px",
                "paddingStart": "md",
                "paddingEnd": "md",
                "paddingTop": "xs"
            }
            ],
            "paddingAll": "0px"
        }
    }

    flex_message = FlexSendMessage(
        alt_text="詳細資料",
        contents=bubble
    )
    
    # category = services[int(service_id)]['category']
    service_title = services[int(service_id)]['title']
    add_service_title = services[int(add_service_id)]['title'] if add_service_id != '0' else ""
    displayText = f"我想預約【{service_title}】" if add_service_id == '0' \
                    else f"我想預約【{service_title}】\n加購: 【{add_service_title}】"
    
    if category == "燙髮":
        label = "加購護髮"
        color = "#78909c"
        action = f"action=service&category=護髮&service_id={service_id}&add_service_id=add"
    elif category == '護髮':
        label = "預約" if add_service_id == '0' else "加購"
        color = "#a1887f" if add_service_id == '0' else "#78909c"
        action = f"action=select_designer&service_id={service_id}&add_service_id={add_service_id}"

    bubble2 = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "horizontal",
            "contents": [
            {
                "type": "text",
                "text": services[int(detail_id)]['description'],
                "wrap": True,
                "weight": "bold"
            }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "horizontal",
            "contents": [
            {
                "type": "button",
                "action": {
                "type": "postback",
                "label": label,
                "data": action,
                "displayText": displayText
                },
                "style": "secondary",
                "color": color
            },
            {
                "type": "button",
                "action": {
                "type": "postback",
                "label": "預約",
                "data": f"action=select_designer&service_id={service_id}&add_service_id={add_service_id}",
                "displayText": displayText
                },
                "style": "secondary",
                "color": "#a1887f"
            }
            ],
            "spacing": "md"
        },
        "styles": {
            "body": {
            "backgroundColor": brown
            },
            "footer": {
            "backgroundColor": brown
            }
        }
        }
    # print(service_title, add_service_title, displayText)

    if category == '護髮':
        temp = bubble2["footer"]["contents"]
        temp.pop(1)
        bubble2["footer"]["contents"] = temp

    flex_message2 = FlexSendMessage(
        alt_text="詳細資料",
        contents=bubble2
    )

    line_bot_api.reply_message(
        event.reply_token,
        [flex_message, flex_message2]
    )

# 選擇設計師
def select_designer_event(event):
    data = dict(parse_qsl(event.postback.data))
    print('select_designer', data)

    service_id = data['service_id']
    add_service_id = data['add_service_id']
    line_user = LineUser.objects.filter(is_staff=True).order_by("-become_staff_time")
    action = f"action=select_reservation_date&service_id={service_id}\
&add_service_id={add_service_id}&designer_line_id="
    
    carousel_count = check_flex_message_count(line_user.count())
    carousel_column_total = []

    # 先將所有 ImageCarouselColumn 放進 list 裡
    for user in line_user:
        # ImageCarouselColumn 的 label 有字數限制，最多12字家空格
        name = user.display_name
        name = name if len(name) <= 12 else name[:10] + ".."

        carousel_column_total.append(
            ImageCarouselColumn(
                image_url=user.picture_url,
                action=PostbackAction(
                    label=name,
                    display_text=f'已選擇設計師 {user.display_name}',
                    data=action + user.line_id
                )
            )
        )
    
    bubble = text_bubble('請指定設計師')
    text_message = FlexSendMessage(alt_text='請指定設計師', contents=bubble)
    reply_message_list = [text_message]
    
    # 有幾個 flex 就迭代幾次，每次都會把 template append 到 reply_message_list
    for count in range(carousel_count):
        start = count * 10
        end = (count + 1) * 10
        image_carousel_template_message = TemplateSendMessage(
            alt_text='請指定設計師',
            template=ImageCarouselTemplate(
                columns=carousel_column_total[start: end]
            )
        )
        reply_message_list.append(image_carousel_template_message)

    line_bot_api.reply_message(event.reply_token, reply_message_list)

# 選擇預約日期(日曆)
def select_reservation_date_event(event):
    data = dict(parse_qsl(event.postback.data))
    print("select_reservation_date", data)

    designer_line_id = data.get('designer_line_id')
    line_user = LineUser.objects.filter(line_id=designer_line_id).first()
    staff = Staff.objects.filter(line_user=line_user).first()
    today = datetime.datetime.now(desired_timezone)
    this_month_year, this_month = today.year, today.month
    next_month_year, next_month = get_year_month_of_next_month(this_month_year, this_month)
    
    # 取得此設計師本月和下個月所有的排班日期
    staff_schedule = StaffSchedule.objects.filter(staff=staff)\
    .filter(Q(date__year=this_month_year, date__month=this_month) | Q(date__year=next_month_year, date__month=next_month))
    # 把本月和下月的所有的排班日期分別存進 list
    this_month_day_list = []  # [1, 5, 9]
    next_month_day_list = []

    if staff_schedule:
        for schedule in staff_schedule:
            date = timezone.localtime(schedule.date).strftime('%Y/%m/%d').split('/')
            month = int(date[1])
            day = int(date[2])
            if month == this_month:
                this_month_day_list.append(day)
            elif month == next_month:
                next_month_day_list.append(day)

    has_schedule_list = [this_month_day_list, next_month_day_list]

    full_schedules = staff_schedule.filter(is_full=True)
    # 把本月和下月的預約爆滿的日期分別存進 list
    this_month_full_day_list = []
    next_month_full_day_list = []
    
    if full_schedules.count() != 0:
        for schedule in full_schedules:
            date = timezone.localtime(schedule.date).strftime('%Y/%m/%d').split('/')
            month = int(date[1])
            day = int(date[2])
            if month == this_month:
                this_month_full_day_list.append(day)
            elif month == next_month:
                next_month_full_day_list.append(day)

    full_schedule_list = [this_month_full_day_list, next_month_full_day_list]
    
    service_id = data.get('service_id')
    add_service_id = data.get('add_service_id')
    action = f"action=can_reservation_list&service_id={service_id}\
&add_service_id={add_service_id}&designer_line_id={designer_line_id}&"

    month_calendar(event, has_schedule_list, full_schedule_list, action)

# 某設計師可預約時間列表
def can_reservation_list_event(event):
    # {'action': 'can_reservation_list', 'service_id': '1', 'add_service_id': '0', 'date': '2024/5/14'}
    data = dict(parse_qsl(event.postback.data))
    print("can_reservation_list", data)

    designer_line_id = data.get('designer_line_id')
    date = data.get('date')
    year = int(date.split('/')[0]); month = int(date.split('/')[1]); day = int(date.split('/')[2])

    designer = LineUser.objects.filter(line_id=designer_line_id).first()
    staff = Staff.objects.filter(line_user=designer).first()
    admin_data = AdminSetting.objects.first()
    schedule = StaffSchedule.objects.filter(staff=staff, date__year=year, date__month=month, date__day=day).first()
    schedule_serializer = StaffScheduleSerializer(schedule, many=False)
    common = StaffCommonSetting.objects.filter(staff=staff)
    common_serializer = StaffCommonSettingSerializer(common, many=True)
    # print(admin_data); print(schedule_serializer.data); print(common_serializer.data)

    # 取得此設計師'當天'所有可預約時間
    time_list_org = parse_schedule(admin_data, schedule_serializer.data, common_serializer.data)
    # print(time_list_org) # ['08:00', '10:30', '11:30', '12:00', '13:00', '14:00', '15:00', '16:00']
    # 若是今天，parse_schedule 會自動消除現在時間 + 當日顧客預約限制前的預約，所以即使有剩餘的預約也會 return []
    # 所以會修改 flex_message 的 '可預約時間' 為 '剩餘預約因為超過時間限制，所以不能預約'
    err = f'(當日顧客預約限制)\n當日當下時間往後 {admin_data.today_reservation_limit} 小時內的\n所有預約 ，顧客不得預約'
    title = "可預約時段" if len(time_list_org) != 0 else err

    # 刪除已經被預約的時段
    reservations = Reservation.objects.filter(designer=designer, date__year=year, date__month=month, date__day=day)
    reservation_list = [timezone.localtime(i.date).strftime("%H:%M") for i in reservations]
    # print(reservation_list) # ['08:00', '16:00']

    time_list = [i for i in time_list_org if i not in reservation_list]

    # 不知為何這樣會 error
    # time_list = list(filter(lambda x: x not in reservation_list, time_list_org))
    # print(time_list)

    service_id = data.get('service_id')
    add_service_id = data.get('add_service_id')
    action = f"action=reservation_confirm&service_id={service_id}\
&add_service_id={add_service_id}&designer_line_id={designer_line_id}\
&time_list_org={','.join(time_list_org)}&date={date}&"

    contents = [
      {
        "type": "text",
        "text": date.replace('/', ' / '),
        "weight": "bold",
        "size": "lg",
        "align": "center"
      },
      {
        "type": "separator",
        "color": "#999999",
        "margin": "lg"
      },
      {
        "type": "text",
        "text": title,
        "weight": "bold",
        "size": "md",
        "align": "center",
        "color": "#009688",
        "margin": "lg",
        "wrap": True
      }
    ]

    two_pair_time_list = parse_two_pair_list(time_list)
    # print(two_pair_time_list)

    for i, t in enumerate(two_pair_time_list, start=1): 
        two_pair_box = {
            "type": "box",
            "layout": "horizontal",
            "contents": [
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                {
                    "type": "text",
                    "text": t[0],
                    "align": "center",
                    "color": brown,
                    "weight": "bold",
                    "size": "md"
                }
                ],
                "backgroundColor": "#009688",
                "cornerRadius": "md",
                "paddingAll": "xl",
                "action": {
                    "type": "postback",
                    "label": f"預約{t[0]}",
                    "data": action + f"time={t[0]}",
                    "displayText": f"預約{t[0]}"
                }
            },
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                {
                    "type": "text",
                    "text": t[1],
                    "align": "center",
                    "color": brown,
                    "weight": "bold",
                    "size": "md"
                }
                ],
                "backgroundColor": "#009688",
                "cornerRadius": "md",
                "paddingAll": "xl",
                "action": {
                    "type": "postback",
                    "label": f"預約{t[1]}",
                    "data": action + f"time={t[1]}",
                    "displayText": f"預約{t[1]}"
                }
            }
            ],
            "margin": "lg",
            "spacing": "lg"
        }

        # 檢查最後一個裡面是 ['11:30', '12:00'] or ['13:00', '']
        if i == len(two_pair_time_list) and t[1] == '':
            # 若最後只有一個 box ，第二個 box 背景為咖啡 brown
            two_pair_box["contents"][1] = {
                "type": "box",
                "layout": "vertical",
                "contents": [
                {
                    "type": "text",
                    "text": "no",
                    "align": "center",
                    "color": brown,
                    "weight": "bold",
                    "size": "md"
                }
                ],
                "backgroundColor": brown,
                "cornerRadius": "md",
                "paddingAll": "xl",
            }

        contents.append(two_pair_box)

    bubble = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": contents
        },
        "styles": {
            "body": {
            "backgroundColor": brown
            }
        }
    }
    
    flex_message = FlexSendMessage(
        alt_text="asd",
        contents=bubble
    )

    if len(time_list_org) == 0:
        text = f'有剩餘預約在 ({admin_data.today_reservation_limit} 小時後)之內，但不能預約'
        bubble = text_bubble(text )
        text_message = FlexSendMessage(alt_text=text , contents=bubble)
        line_bot_api.reply_message(event.reply_token, [text_message, flex_message])

    line_bot_api.reply_message(event.reply_token, flex_message)

# 預約確認(您即將預約....)
def reservation_confirm_event(event):
    data = dict(parse_qsl(event.postback.data))
    print("reservation_confirm", data)

    designer_line_id = data.get('designer_line_id')
    date = data.get('date')
    reservation_time= data.get('time')
    service_id = data.get('service_id')
    add_service_id = data.get('add_service_id')
    time_list_org = data.get('time_list_org')
    designer = LineUser.objects.filter(line_id=designer_line_id).first().display_name

    #取得要預約的服務項目資料,會出現1234對應到上面的service
    newline = "" if add_service_id == '0' else "\n加購: "
    service = services[int(data['service_id'])]['title']
    adding_service = "" if add_service_id == '0' \
                        else newline + f"{services[int(add_service_id)]['title']}"
    print('service: ', service, '\nadding_service: ', adding_service)

    bubble = {
"type": "bubble",
"body": {
"type": "box",
"layout": "vertical",
"spacing": "sm",
"contents": [
  {
    "type": "text",
    "margin": "none",
    "wrap": True,
    "text": f'您即將預約: {service}{adding_service}\n設計師: {designer}\
\n預約時段: {date} {reservation_time}\n確認沒問題，請按【確定】',
    "color": "#000000"
  }
]
},
"footer": {
"type": "box",
"layout": "horizontal",
"spacing": "sm",
"contents": [
    {
    "type": "button",
    "action": {
          "type": "postback",
          "label": "重新預約",
          "displayText": "重新預約",
          "data": 'action=service_category'
    },
    "style": "link"
    },
    {
        "type": "button",
        "action": {
            "type": "postback",
            "label": "確定",
            "displayText": "確定",
            "data": f'action=reservation_check_and_save&service_id={service_id}&add_service_id={add_service_id}\
&designer_line_id={designer_line_id}&time_list_org={time_list_org}&date={date}&time={reservation_time}'
        },
        "style": "link"
    }
]
},
"size": "kilo",
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

    flex_message = FlexSendMessage(alt_text='請確認預約項目', contents=bubble)
    line_bot_api.reply_message(event.reply_token, flex_message)

# "123123qweasdasdQFGHJHXD" "wqdasdasdasasdWQEQWE"
# 檢查預約(同一人同一天是否已經預約)
def reservation_check_and_save_event(event):
    data = dict(parse_qsl(event.postback.data))
    print('reservation_check', data)

    # line_id = "123123qweasdasdQFGHJHXD"
    line_id = event.source.user_id # 使用者的 line_id
    designer_line_id = data.get('designer_line_id')
    date = data.get('date')
    reservation_time = data.get('time')
    year = int(date.split('/')[0]); month = int(date.split('/')[1]); day = int(date.split('/')[2])
    hour = int(reservation_time.split(':')[0]); minute = int(reservation_time.split(':')[1])
    service_id = int(data.get('service_id'))
    add_service_id = int(data.get('add_service_id')) 

    line_user = LineUser.objects.filter(line_id=line_id).first()
    designer = LineUser.objects.filter(line_id=designer_line_id).first()
    staff = Staff.objects.filter(line_user=designer).first()
    staff_schedule = StaffSchedule.objects.filter(staff=staff, date__year=year, date__month=month, date__day=day).first()
    service = services[service_id]['title']
    add_service = services[add_service_id]['title'] if add_service_id != 0 else ''
    
    # 檢查'同天同時段同設計師'是否已經被預約過(已經預約過，再次點擊確定會觸發)
    reservation_check = Reservation.objects.filter(
        line_user = line_user,
        designer = designer,
        date = datetime.datetime(year, month, day, hour, minute), 
    )
    
    if reservation_check:
        bubble = text_bubble('已經預約成功了喔，到時候見!')
        text_message = FlexSendMessage(alt_text='已經預約成功了喔，到時候見!', contents=bubble)
        return line_bot_api.reply_message(
            event.reply_token,
            text_message
        )
        
    # 更換預約
    # 先檢查，'同一天同一人和任何設計師'只能預約一個時段
    reservation_check = Reservation.objects.filter(
        line_user = line_user,
        # 不知為何上面有 5 個就行 下面只有 year, month, day 會 error
        date__year=year, date__month=month, date__day=day,
    ).first()

    if reservation_check:
        old_time = timezone.localtime(reservation_check.date).strftime("%H:%M")
        old_designer = reservation_check.designer
        old_service_text = reservation_check.service
        old_add_service_text = "" if not reservation_check.add_service \
                        else "\n加購: " + f"{reservation_check.add_service}"
        
        new_service_text = service
        new_add_service_text = "" if add_service_id == 0 \
                        else "\n加購: " + f"{add_service}"

        bubble = {
"type": "bubble",
"body": {
"type": "box",
"layout": "vertical",
"spacing": "sm",
"contents": [
  {
    "type": "text",
    "margin": "none",
    "wrap": True,
    "text":  f'此天已有預約!!\n\
同帳號同一天只能預約一種服務\n\n\
舊預約:\n\
預約時段: {date} {old_time}\n\
設計師: {old_designer}\n\
預約: {old_service_text}{old_add_service_text}\n\n\
您是否想更換預約為最新選擇?\n\
預約時段: {date} {reservation_time}\n\
設計師: {designer.display_name}\n\
預約: {new_service_text}{new_add_service_text}',
    "color": "#000000"
  }
]
},
"footer": {
"type": "box",
"layout": "horizontal",
"spacing": "sm",
"contents": [
  {
    "type": "button",
    "action": {
          "type": "postback",
          "label": "重新預約",
          "displayText": "重新預約",
          "data": 'action=service_category'
    },
    "style": "link"
  },
  {
    "type": "button",
    "action": {
        "type": "postback",
        "label": "更換預約",
        "displayText": "更換預約",
        "data": f'action=reservation_change&service_id={service_id}&add_service_id={add_service_id}\
&designer_line_id={designer_line_id}&date={date}&time={reservation_time}'
    },
    "style": "link"
  }
]
},
"size": "kilo",
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

        flex_message = FlexSendMessage(alt_text='此天已有預約', contents=bubble)
        return line_bot_api.reply_message(event.reply_token, flex_message)
        
    # 再檢查此設計師此天此時段是否已經被預約(有可以兩個人同時約同時段，因為還沒被預約 can_reservation_list 會顯示時段
    # 但先預約的人會先被寫入資料庫，慢預約的也約同時段，會顯示此時段已被預約)
    reservation_check = Reservation.objects.filter(
        designer = designer,
        date = datetime.datetime(year, month, day, hour, minute)
    )

    if reservation_check:
        bubble = text_bubble('此時段剛剛被預約，下次要快~')
        text_message = FlexSendMessage(alt_text='此時段剛剛被預約，下次要快~', contents=bubble)
        return line_bot_api.reply_message(
            event.reply_token,
            text_message
        )

    # 預約存入資料庫
    Reservation.objects.create(
        line_user = line_user,
        staff_schedule = staff_schedule,
        designer = designer,
        date = datetime.datetime(year, month, day, hour, minute),
        service = service,
        add_service = add_service,
    )

    bubble = text_bubble('沒問題! 感謝您的預約，我已經幫您預約成功了喔，到時候見!')
    text_message = FlexSendMessage(alt_text='沒問題! 感謝您的預約，我已經幫您預約成功了喔，到時候見!', contents=bubble)
  
    line_bot_api.reply_message(
        event.reply_token,
        text_message
    )

# 更換預約
def reservation_change_event(event):
    data = dict(parse_qsl(event.postback.data))
    print('reservation_change', data)

    line_id = event.source.user_id 
    designer_line_id = data.get('designer_line_id')
    date = data.get('date')
    reservation_time = data.get('time')
    year = int(date.split('/')[0]); month = int(date.split('/')[1]); day = int(date.split('/')[2])
    hour = int(reservation_time.split(':')[0]); minute = int(reservation_time.split(':')[1])
    service_id = int(data.get('service_id'))
    add_service_id = int(data.get('add_service_id')) 

    line_user = LineUser.objects.filter(line_id=line_id).first()
    designer = LineUser.objects.filter(line_id=designer_line_id).first()
    service = services[service_id]['title']
    add_service = services[add_service_id]['title'] if add_service_id != 0 else ''

    # 本人'已經換過預約'，然後重複按會跑這
    reservation_check = Reservation.objects.filter(
        line_user=line_user,
        designer = designer,
        date = datetime.datetime(year, month, day, hour, minute),
    )

    if reservation_check:
        text = '已經更換預約成功了喔，到時候見!'
        bubble = text_bubble(text)
        text_message = FlexSendMessage(alt_text=text, contents=bubble)
        return line_bot_api.reply_message(event.reply_token, text_message)

    # 還是要檢查此設計師此天此時段是否已經被預約(有可以兩個人同時約同時段，因為還沒被預約 can_reservation_list 會顯示時段
    # 但先預約的人會先被寫入資料庫，慢預約的也約同時段，會顯示此時段已被預約)
    reservation_check = Reservation.objects.filter(
        designer = designer,
        date = datetime.datetime(year, month, day, hour, minute)
    )

    if reservation_check:
        text = '此時段剛剛被預約，下次要快~'
        bubble = text_bubble(text)
        text_message = FlexSendMessage(alt_text=text, contents=bubble)
        return line_bot_api.reply_message(event.reply_token, text_message)

    # 預約存入資料庫
    staff = Staff.objects.filter(line_user=designer).first()
    staff_schedule = StaffSchedule.objects.filter(staff=staff, date__year=year, date__month=month, date__day=day).first()
    reservation = Reservation.objects.filter(line_user=line_user,
        date__year=year, date__month=month, date__day=day).first()
    reservation.staff_schedule = staff_schedule
    reservation.designer = designer
    reservation.date = datetime.datetime(year, month, day, hour, minute)
    reservation.service = service
    reservation.add_service = add_service
    reservation.save()

    text = '更換預約成功，到時候見!'
    bubble = text_bubble(text)
    text_message = FlexSendMessage(alt_text=text, contents=bubble)
    line_bot_api.reply_message(event.reply_token, text_message)

# 取消預約
def reservation_cancel_event(event):
    data = dict(parse_qsl(event.postback.data))
    print('reservation_cancel', data)

    reservation_id = int(data.get('reservation_id'))
    reservation_title = data.get('reservation_title')
    reservation = Reservation.objects.filter(id=reservation_id).first()

    if not reservation:
        size = None
        text = '此預約已經取消了，請重新預約'
    else:
        size = "nano"
        text = f'已取消 {reservation_title}'
        reservation.delete()

    # 取消預約後，此位設計師此天的 schedule 一定不會滿
    designer_line_id = data.get('designer_line_id')
    date = data.get('date')
    year = int(date.split('/')[0]); month = int(date.split('/')[1]); day = int(date.split('/')[2])

    designer = LineUser.objects.filter(line_id=designer_line_id).first()
    staff = Staff.objects.filter(line_user=designer).first()
    staff_schedule = StaffSchedule.objects.filter(staff=staff, date__year=year, date__month=month, date__day=day).first()

    if staff_schedule.is_full:
        staff_schedule.is_full = False
        staff_schedule.save()
    
    bubble = text_bubble(text, size)
    text_message = FlexSendMessage(alt_text=text, contents=bubble)
    line_bot_api.reply_message(event.reply_token, text_message)

# 我的預約
def my_reservation(event):
    line_id = event.source.user_id
    line_user = LineUser.objects.filter(line_id=line_id).first()

    today = datetime.datetime.now(desired_timezone)
    # 将时间部分替换为 00:00:00，得到今天凌晨的日期时间
    now_datetime = today.replace(hour=0, minute=0, second=0, microsecond=0)

    reservations = Reservation.objects.filter(
        line_user = line_user,
        date__gte = now_datetime
    ).order_by('date')

    if not reservations:
        bubble = text_bubble('您目前沒有預約喔')
        text_message = FlexSendMessage(alt_text='您目前沒有預約喔', contents=bubble)
        return line_bot_api.reply_message(event.reply_token, text_message)       

    bubbles = []

    for i, reservation in enumerate(reservations, start=1):
        date = timezone.localtime(reservation.date).strftime("%Y/%m/%d")
        year = int(date.split('/')[0]); month = int(date.split('/')[1]); day = int(date.split('/')[2])
        date = f'{year} / {month} / {day}'
        reservation_time = timezone.localtime(reservation.date).strftime("%H:%M")
        service = reservation.service
        add_service = reservation.add_service if reservation.add_service else "無"
        designer = reservation.designer.display_name
        designer_line_id = reservation.designer.line_id
        action = f'action=reservation_cancel&designer_line_id={designer_line_id}&&date={date}\
&reservation_id={reservation.id}&reservation_title=預約{i}'

        bubble = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                    {
                        "type": "text",
                        "text": f"預約 {i}",
                        "align": "center",
                        "weight": "bold",
                        "size": "lg",
                        "margin": "md"
                    },
                    {
                        "type": "separator",
                        "color": "#999999",
                        "margin": "lg"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                        {
                            "type": "text",
                            "text": "日期",
                            "size": "md",
                            "weight": "bold",
                            "flex": 0
                        },
                        {
                            "type": "text",
                            "text": date,
                            "size": "md",
                            "align": "end",
                            "weight": "bold",
                            "color": "#009688"
                        }
                        ],
                        "margin": "lg"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                        {
                            "type": "text",
                            "text": "時間",
                            "size": "md",
                            "weight": "bold",
                            "flex": 0
                        },
                        {
                            "type": "text",
                            "text": reservation_time,
                            "size": "md",
                            "align": "end",
                            "weight": "bold",
                            "color": "#009688"
                        }
                        ],
                        "margin": "lg"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                        {
                            "type": "text",
                            "text": "預約服務",
                            "size": "md",
                            "weight": "bold",
                            "flex": 0
                        },
                        {
                            "type": "text",
                            "text": service,
                            "size": "md",
                            "align": "end",
                            "weight": "bold"
                        }
                        ],
                        "margin": "lg"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                        {
                            "type": "text",
                            "text": "加購",
                            "size": "md",
                            "weight": "bold",
                            "flex": 0
                        },
                        {
                            "type": "text",
                            "text": add_service,
                            "size": "md",
                            "align": "end",
                            "weight": "bold"
                        }
                        ],
                        "margin": "lg"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                        {
                            "type": "text",
                            "text": "設計師",
                            "size": "md",
                            "flex": 0,
                            "weight": "bold"
                        },
                        {
                            "type": "text",
                            "text": designer,
                            "size": "md",
                            "align": "end",
                            "weight": "bold"
                        }
                        ],
                        "margin": "lg"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                        {
                            "type": "text",
                            "text": "取消預約",
                            "align": "center",
                            "color": "#d32f2f",
                            "weight": "bold"
                        }
                        ],
                        "paddingAll": "xl",
                        "cornerRadius": "md",
                        "margin": "xxl",
                        "action": {
                            "type": "postback",
                            "label": "取消預約",
                            "data": action,
                            "displayText": "取消預約"
                        },
                        "borderColor": "#d32f2f",
                        "borderWidth": "normal"
                    }
                    ]
                }
                ],
                "backgroundColor": brown,
                "paddingTop": "lg"
            }
            }
        
        bubbles.append(bubble)

    if reservations.count() == 1:
        flex_message = FlexSendMessage(
            alt_text='我的預約',
            contents=bubbles[0]
        )
    else:
        flex_message = FlexSendMessage(
            alt_text='我的預約',
            contents={
                "type": "carousel",
                "contents": bubbles
            }
        )
    
    line_bot_api.reply_message(event.reply_token, flex_message)




