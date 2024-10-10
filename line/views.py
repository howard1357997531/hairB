from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from linebot import WebhookHandler, LineBotApi
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage, TextMessage
from urllib.parse import parse_qsl
from mainapp.models import LineUser
from .models import *
from .event import *
from .service import *
from .cart import *
from .linepay import *
from .staff import *
import uuid

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(settings.LINE_CHANNEL_SECRET)

# def home(request):
#     return HttpResponse('asd')

def add_staff(request):
    staffs = LineUser.objects.filter(is_admin=False)
    return render(request, 'add_staff.html', locals())

def home(request):
    return render(request, 'index.html', locals())

# line
@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
 
        try:
            handler.handle(body, signature)
            return HttpResponse()
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()
    else:
        return HttpResponseBadRequest()
    
# event.message.text 用戶輸入文字
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message_text = event.message.text
    user = LineUser.objects.filter(line_id=event.source.user_id).first()
    profile = line_bot_api.get_profile(event.source.user_id)

    if not user:    
        LineUser.objects.create(
            line_id = profile.user_id,
            display_name = profile.display_name,
            picture_url = profile.picture_url
        )
    else:
        # 若 lineUser 名稱、圖片有更新會修改 database
        if user.display_name != profile.display_name or user.picture_url != profile.picture_url:
            user.display_name = profile.display_name
            user.picture_url = profile.picture_url
            user.save()

    if message_text == '123456':
        admin_login(event)

    if message_text == '髮廊介紹':
        about_us_event(event)

    elif message_text == '營業據點':
        location_event(event)

    elif message_text == '預約注意':
        note_for_reservation(event)

    elif message_text == '預約服務':
        service_category_event(event)

    elif message_text == '我的預約':
        my_reservation(event)

    elif message_text == '最新消息':
        latest_news(event)

    elif message_text == '交易紀錄':
        more_information(event)

    elif message_text == '更多資訊':
        more_information(event)

    elif message_text == '123':
        display_receipt(event)


    # linepay
    profile = line_bot_api.get_profile(event.source.user_id)
    message = None

    if message_text in ['商品', '繼續買']:
        message = display_all_product()

    elif message_text.endswith('詳細資訊'):
        product_detail(event, message_text)
        
    elif message_text == '清空購物車':
        shopping_cart_reset(event) 

    elif message_text.startswith('請勿新增或刪除任何文字，\n只能輸入(大於 0 的整數)\n('):
        message = add_to_shopping_cart(event, message_text)

    elif message_text.startswith("<刪除>"):
        message = delete_product_in_cart(event, message_text)

    elif message_text == '購物車':
        message = shopping_cart(event)

    elif message_text.startswith('請勿新增或刪除任何文字，\n請輸入要寄送的地址\n地址:'):
        message = delivery_to_address_text(event, message_text)
    
    elif message_text == '重建訂單':
        order_rebuild(event)

    if message:
        line_bot_api.reply_message(
            event.reply_token,
            message
        )

@handler.add(PostbackEvent)
def handle_postback(event):
    data = dict(parse_qsl(event.postback.data))

    if data.get('action') == 'service':
        select_service_event(event)
    elif data.get('action') == 'service_category':
        service_category_event(event)
    elif data.get('action') == 'service_detail':
        service_detail_event(event)
    elif data.get('action') == 'select_designer':
        select_designer_event(event)
    elif data.get('action') == 'select_reservation_date':
        select_reservation_date_event(event)
    elif data.get('action') == 'can_reservation_list':
        can_reservation_list_event(event)
    elif data.get('action') == 'reservation_confirm':
        reservation_confirm_event(event)
    elif data.get('action') == 'reservation_check_and_save':
        reservation_check_and_save_event(event)
    elif data.get('action') == 'reservation_change':
        reservation_change_event(event)
    elif data.get('action') == 'reservation_cancel':
        reservation_cancel_event(event)
    
    # 商品
    elif data.get('action') == 'product_detail':
        product_detail(event)
    elif data.get('action') == 'edit_product_quantity':
        edit_cart_product_quantity(event)
    elif data.get('action') == 'select_pickup_method':
        select_pickup_method(event)
    elif data.get('action') == 'order_confirm':
        order_confirm(event)
    elif data.get('action') == 'order_create':
        order_create(event)
    elif data.get('action') == 'order_delete':
        order_delete(event)
    elif data.get('action') == 'order_no_pay':
        order_no_pay(event)

    return 'ok'

@handler.add(FollowEvent)
def handle_follow(event):
    welcome_msg = '''$ Nice Salon $
我是專業小幫手

想預約剪髮、燙髮、染髮、護髮等等服務都可以直接跟我預約喔
直接點選下方【歡迎光臨專屬您的設計】

期待您的光臨 !'''

    line_bot_api.reply_message(
        event.reply_token,
        TextMessage(text=welcome_msg)
    )

# 封鎖時call的
@handler.add(UnfollowEvent)
def handle_unfollow(event):
    print(event)
