from django.http import HttpResponse
from cachelib import SimpleCache
from linebot import WebhookHandler, LineBotApi
from django.conf import settings
from django.utils import timezone
from linebot.models import *
from mainapp.models import AdminSetting
from .models import *
from .cart import *
from .linepay import *
from .tool import text_bubble, check_flex_message_count
import uuid
from urllib.parse import parse_qsl, quote
from datetime import datetime
import pytz


line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
'''
SimpleCache 的默认配置是不持久化缓存数据，意味着在程序结束或缓存被重置时，
数据会被清除。不过，SimpleCache 提供了一个可选参数 default_timeout，
可以用来设置缓存数据的过期时间（以秒为单位）。如果没有指定 default_timeout，
缓存数据将会一直存在，直到程序结束或缓存被手动删除。
# 初始化缓存，并设置默认的超时时间为10秒
# cache = SimpleCache(default_timeout=10)
'''
cache = SimpleCache()
desired_timezone = pytz.timezone('Asia/Taipei')
brown = "#d7ccc8"

class Cart(object):
    def __init__(self, user_id):
        self.user_id = user_id
        self.cache = cache

    def bucket(self):
        return cache.get(key=self.user_id) or {}

    def add(self, product, num):
        bucket = self.bucket()
        if bucket == None:
            cache.add(key=self.user_id, value={product: int(num)})
        else:
            bucket.update({product: int(num)})
            cache.set(key=self.user_id, value=bucket)
            
    def delete(self, product):
        bucket = self.bucket()

        if bucket == None:
            return
        else:
            new_dict = bucket
            del new_dict[product]
            cache.set(key=self.user_id, value=new_dict)

    def reset(self): #清空購物車
        cache.set(key=self.user_id, value={})

    def shopping_cart(self):
        # 放置產品明細
        # print(self.bucket())         # 洗髮精
        # print(self.bucket().items()) # {'洗髮精': 6, '護髮油': 7}
        total_price = 0 #總金額
        product_box_component = [
          {
            "type": "text",
            "wrap": True,
            "text": "購物車",
            "size": "lg",
            "align": "center",
            "color": "#000000"
          },
          {
            "type": "separator",
            "color": "#b3b3b3",
            "margin": "xl"
          }
        ]  
        
        for name, quantity in self.bucket().items():
            product = Product.objects.filter(name=name).first()
            amount = product.price * int(quantity)
            total_price += amount
            product_box_component.extend([
            {
              "type": "box",
              "layout": "horizontal",
              "contents": [
                {
                  "type": "text",
                  "margin": "none",
                  "wrap": True,
                  "text": f"{name} (${product.price} x {quantity})",
                  "size": "sm",
                  "color": "#000000"
                },
                {
                  "type": "text",
                  "margin": "none",
                  "wrap": True,
                  "text": f"$ {amount}",
                  "align": "end",
                  "size": "sm",
                  "color": "#000000"
                }
              ],
              "paddingTop": "lg",
              "paddingBottom": "lg",
              "action": {
                "type": "message",
                "label": f"<刪除> {name}",
                "text": f"<刪除> {name}"
              }
            },
            {
              "type": "separator",
              "color": "#b3b3b3"
            }
          ])
        
        product_box_component.extend([
            {
          "type": "box",
          "layout": "horizontal",
          "contents": [
            {
              "type": "text",
              "margin": "none",
              "wrap": True,
              "text": "總價",
              "color": "#009688",
              "size": "sm",
              "weight": "bold"
            },
            {
              "type": "text",
              "margin": "none",
              "wrap": True,
              "text": f"NT$ {total_price}",
              "align": "end",
              "color": "#009688",
              "size": "sm",
              "weight": "bold"
            }
          ],
          "paddingTop": "lg",
          "paddingBottom": "lg"
          },
          {
            "type": "separator",
            "color": "#b3b3b3"
          },
          {
            "type": "text",
            "text": "<刪除> 點擊上方(商品格)即可刪除商品",
            "size": "sm",
            "margin": "lg",
            "color": "#000000",
            "wrap": True
          },
          {
            "type": "text",
            "text": "<修改數量> 在商品列表中，選擇要修改數量的商品，按(加入購物車)輸入數量即可修改",
            "size": "sm",
            "margin": "md",
            "color": "#000000",
            "wrap": True
          },
          {
            "type": "text",
            "text": "<備註> 確定商品種類、數量無誤後，請點擊(選擇取貨方式)",
            "size": "sm",
            "margin": "md",
            "color": "#000000",
            "wrap": True
          }
        ])

        bubble = {
  "type": "bubble",
  "body": {
    "type": "box",
    "layout": "vertical",
    "spacing": "sm",
    "contents": product_box_component
  },
  "footer": {
    "type": "box",
    "layout": "vertical",
    "spacing": "md",
    "contents": [
      {
        "type": "box",
        "layout": "horizontal",
        "contents": [
          {
            "type": "button",
            "action": {
              "type": "message",
              "label": "清空購物車",
              "text": "清空購物車"
            },
            "style": "secondary",
            "color": "#9e9e9e"
          },
          {
            "type": "button",
            "action": {
              "type": "message",
              "label": "繼續買",
              "text": "繼續買"
            },
            "color": "#78909c",
            "style": "secondary"
          }
        ],
        "spacing": "md"
      },
      {
        "type": "button",
        "action":  {
          "type": "postback",
          "label": "選擇取貨方式",
          "data": "action=select_pickup_method",
          "displayText": "選擇取貨方式"
        },
        "style": "secondary",
        "color": "#a1887f"
      }
    ],
    "paddingTop": "none"
  },
  "styles": {
    "body": {
      "backgroundColor": "#d1ccca"
    },
    "footer": {
      "backgroundColor": "#d1ccca"
    }
  }
}

        message = FlexSendMessage(
            alt_text='請確認購物清單',
            contents=bubble
        )

        #會回傳到app.py message = cart.display()
        return message
    
    def order_confirm(self, pickup_method, address):
        total_price = 0 #總金額
        product_box_component = [
          {
            "type": "text",
            "wrap": True,
            "text": "訂單確認",
            "size": "lg",
            "align": "center",
            "color": "#000000"
          },
          {
            "type": "separator",
            "color": "#b3b3b3",
            "margin": "xl"
          }
        ]  
        
        for name, quantity in self.bucket().items():
            product = Product.objects.filter(name=name).first()
            amount = product.price * int(quantity)
            total_price += amount
            product_box_component.extend([
            {
              "type": "box",
              "layout": "horizontal",
              "contents": [
                {
                  "type": "text",
                  "margin": "none",
                  "wrap": True,
                  "text": f"{name} (${product.price} x {quantity})",
                  "size": "sm",
                  "color": "#000000"
                },
                {
                  "type": "text",
                  "margin": "none",
                  "wrap": True,
                  "text": f"$ {amount}",
                  "align": "end",
                  "size": "sm",
                  "color": "#000000"
                }
              ],
              "paddingTop": "lg",
              "paddingBottom": "lg",
              "action": {
                "type": "message",
                "label": f"<刪除> {name}",
                "text": f"<刪除> {name}"
              }
            },
            {
              "type": "separator",
              "color": "#b3b3b3"
            }
          ])
        
        product_box_component.extend([
            {
          "type": "box",
          "layout": "horizontal",
          "contents": [
            {
              "type": "text",
              "margin": "none",
              "wrap": True,
              "text": "總價",
              "color": "#009688",
              "size": "sm",
              "weight": "bold"
            },
            {
              "type": "text",
              "margin": "none",
              "wrap": True,
              "text": f"NT$ {total_price}",
              "align": "end",
              "color": "#009688",
              "size": "sm",
              "weight": "bold"
            }
          ],
          "paddingTop": "lg",
          "paddingBottom": "lg"
          },
          {
            "type": "separator",
            "color": "#b3b3b3"
          },
          {
            "type": "text",
            "text": f"取貨方式: {pickup_method}",
            "size": "sm",
            "margin": "lg",
            "color": "#000000",
            "wrap": True
          },
          {
            "type": "text",
            "text": f"取貨地址: {address}",
            "size": "sm",
            "margin": "md",
            "color": "#000000",
            "wrap": True
          },
          {
            "type": "text",
            "text": "<備註> 確定商品種類、數量、取貨方式、取貨地址無誤後，請點擊(建立訂單)",
            "size": "sm",
            "margin": "md",
            "color": "#000000",
            "wrap": True
          }
        ])

        bubble = {
  "type": "bubble",
  "body": {
    "type": "box",
    "layout": "vertical",
    "spacing": "sm",
    "contents": product_box_component
  },
  "footer": {
    "type": "box",
    "layout": "vertical",
    "spacing": "md",
    "contents": [
      {
        "type": "box",
        "layout": "horizontal",
        "contents": [
          {
            "type": "button",
            "action": {
              "type": "postback",
              "label": "修改取貨方式",
              "data": "action=select_pickup_method",
              "displayText": "修改取貨方式"
            },
            "style": "secondary",
            "color": "#9e9e9e"
          },
          {
            "type": "button",
            "action": {
              "type": "postback",
              "label": "建立訂單",
              "data": f"action=order_create&pickup_method={pickup_method}&address={address}",
              "displayText": "建立訂單"
            },
            "color": "#a1887f",
            "style": "secondary"
          }
        ],
        "spacing": "md"
      }
    ],
    "paddingTop": "none"
  },
  "styles": {
    "body": {
      "backgroundColor": "#d1ccca"
    },
    "footer": {
      "backgroundColor": "#d1ccca"
    }
  }
}

        message = FlexSendMessage(
            alt_text='請確認購物清單',
            contents=bubble
        )

        #會回傳到app.py message = cart.display()
        return message

# 顯示所有商品
def display_all_product():
    products = Product.objects.all().order_by('-id')

    flex_message_count = check_flex_message_count(products.count())
    flex_message_total = []
    message = []
    
    for product in products:
        image_url = product.image_url
        name = product.name
        price = f"${product.price}"
        quantity = f'( 庫存: {product.quantity} )'
        description = product.description 
        description = description if len(description) < 43 else description[:44] + "..."

        bubble = {
  "type": "bubble",
  "hero": {
    "type": "image",
    "size": "full",
    "aspectRatio": "20:13",
    "aspectMode": "cover",
    "url": image_url
  },
  "body": {
    "type": "box",
    "layout": "vertical",
    "spacing": "sm",
    "contents": [
      {
        "type": "text",
        "text": name,
        "wrap": True,
        "weight": "bold",
        "size": "xl",
        "align": "center",
        "color": "#000000"
      },
      {
        "type": "text",
        "text": description,
        "margin": "lg",
        "wrap": True,
        "color": "#000000"
      },
      {
        "type": "text",
        "text": price,
        "align": "center",
        "size": "xxl",
        "margin": "xl",
        "color": "#000000"
      },
      {
        "type": "text",
        "text": quantity,
        "align": "center",
      }
    ]
  },
  "footer": {
    "type": "box",
    "layout": "horizontal",
    "spacing": "md",
    "contents": [
      {
        "type": "button",
        "action": {
          "type": "message",
          "label": f"詳細資訊",
          "text": f"{name} 詳細資訊"
        },
        "color": "#78909c",
        "style": "secondary"
      },
      {
        "type": "button",
        "action": {
          "type": "uri",
          "label": "加入購物車",
          "uri": 'line://oaMessage/{base_id}/?{message}'.format(base_id='@244cbsrk', # 請用自己的
            message=quote('請勿新增或刪除任何文字，\n只能輸入(大於 0 的整數)\n({product})，購買數量:'.format(product=name)))
        },
        "color": "#a1887f",
        "style": "secondary"
      }
    ]
  },
  "styles": {
    "body": {
      "backgroundColor": "#d1ccca"
    },
    "footer": {
      "backgroundColor": "#d1ccca"
    }
  }
}
        
        # 如果商品售罄
        if product.quantity <= 0:
            bubble["footer"]["contents"][1] = {
              "type": "button",
              "action": {
                "type": "message",
                "label": "已售罄",
                "text": f"{name} 已售罄"
              },
              "color": "#d32f2f",
              "style": "secondary"
            }

        # bubbles.append(bubble)
        flex_message_total.append(bubble)
    
    for count in range(flex_message_count):
      start = count * 10
      end = (count + 1) * 10

      flex_message = FlexSendMessage(
          alt_text="本月預約",
          contents={
            "type": "carousel",
            "contents": flex_message_total[start: end]
          }
        )
      message.append(flex_message)

    return message

# 商品詳細資訊
def product_detail(event, message_text):
    name = message_text.split(" ")[0]
    product = Product.objects.filter(name=name).first()
    image_url = product.image_url
    name = product.name
    price = f"${product.price}"
    quantity = f'( 庫存: {product.quantity} )'
    description = product.description

    bubble = {
  "type": "bubble",
  "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "image",
        "url": image_url,
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
            "text": name,
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

    bubble2 = {
  "type": "bubble",
  "body": {
    "type": "box",
    "layout": "vertical",
    "spacing": "sm",
    "contents": [
      {
        "type": "text",
        "text": name,
        "wrap": True,
        "weight": "bold",
        "size": "xl",
        "align": "center",
        "color": "#000000"
      },
      {
        "type": "text",
        "text": description,
        "margin": "lg",
        "wrap": True,
        "color": "#000000"
      },
      {
        "type": "text",
        "text": price,
        "align": "center",
        "size": "xl",
        "margin": "xl",
        "color": "#000000"
      },
      {
        "type": "text",
        "text": quantity,
        "align": "center",
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
          "type": "uri",
          "label": "加入購物車",
          "uri": 'line://oaMessage/{base_id}/?{message}'.format(base_id='@244cbsrk', # 請用自己的
            message=quote('請勿新增或刪除任何文字，\n只能輸入(大於 0 的整數)\n({product})，購買數量:'.format(product=name)))
        },
        "color": "#a1887f",
        "style": "secondary"
      }
    ]
  },
  "styles": {
    "body": {
      "backgroundColor": "#d1ccca"
    },
    "footer": {
      "backgroundColor": "#d1ccca"
    }
  }
}   
    
    # 如果商品售罄
    if product.quantity <= 0:
            bubble2["footer"]["contents"][0] = {
              "type": "button",
              "action": {
                "type": "message",
                "label": "已售罄",
                "text": f"{name} 已售罄"
              },
              "color": "#d32f2f",
              "style": "secondary"
            }

    flex_message2 = FlexSendMessage(
        alt_text="詳細資料",
        contents=bubble2
    )

    return line_bot_api.reply_message(
        event.reply_token,
        [flex_message, flex_message2]
    )

# 加入購物車
def add_to_shopping_cart(event, message_text):
    user_id = event.source.user_id

    # 若結帳後未付款
    line_user = LineUser.objects.filter(line_id=user_id).first()
    order = Order.objects.filter(line_user=line_user, is_pay=False).first()

    if order:
        order_no_pay(event, order.id)

    # 檢查文字是否為: (洗髮精)，購買數量:1
    first_text_check = '請勿新增或刪除任何文字，\n只能輸入(大於 0 的整數)\n('
    end_text_check = ')，購買數量:'
    all_product_name = Product.objects.all().values('name')
    all_product_name_list = [name['name'] for name in all_product_name]

    one_check = "(" in message_text and ")" in message_text and "，" in message_text and ":" in message_text
    two_check = end_text_check in message_text
    warning_text = None

    if one_check and two_check:
        product_name = message_text.split(first_text_check)[1].split(end_text_check)[0]
        if product_name not in all_product_name_list:
            warning_text = f'抱歉! 我們沒有賣({product_name})這個商品'
            bubble = text_bubble(warning_text)
            flex_message = FlexSendMessage(alt_text=warning_text, contents=bubble)
            return flex_message
            
        quantity = message_text.split(end_text_check)[-1].strip()
        if quantity.isnumeric() and int(quantity) > 0:
            quantity = int(quantity)
        else:
            warning_text = '請勿新增或刪除任何文字，並且只能輸入(大於0的整數)'
    else:
        warning_text = '請勿新增或刪除任何文字，並且只能輸入(大於0的整數)'
    
    if warning_text:
      bubble = text_bubble(warning_text)
      flex_message = FlexSendMessage(alt_text=warning_text, contents=bubble)
      return flex_message

    # 如果商品售罄或庫存小於購買數量
    product = Product.objects.filter(name=product_name).first()
    product_quantity = product.quantity
    warning_text = None

    # 如果在按下商品列表時庫存還有10個，要買5個但還沒按下'送出鍵'的期間，已經有其他使用者建立訂單
    # 讓庫存歸0或剩下2個(比要得5個少)，會導致數量不夠無法加入購物車，會跑這邊
    if product_quantity <= 0:
      warning_text = '商品已售罄'
      size = None
    elif product_quantity < quantity:
      warning_text = f'{product_name} 只剩{product_quantity}個'
      size = "micro"

    if warning_text:
      bubble = text_bubble(warning_text, size)
      flex_message = FlexSendMessage(alt_text=warning_text, contents=bubble)
      return flex_message

    cart = Cart(user_id=user_id)
    previous_quantity = cart.bucket().get(product_name, None)

    # 如果舊數量和新數量相同不跑這邊(修改用)
    if previous_quantity is not None and previous_quantity != quantity:
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
        "text": f"已經購買: {product_name} x {previous_quantity}",
        "color": "#000000"
      },
      {
        "type": "text",
        "margin": "none",
        "wrap": True,
        "text": f"請問要修改成: 數量 x {quantity} 嗎?",
        "margin": "md",
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
          "type": "message",
          "label": "繼續買",
          "text": "繼續買"
        },
        "style": "link"
      },
      {
        "type": "button",
        "action": {
          "type": "postback",
          "label": "修改數量",
          "data": f"action=edit_product_quantity&product_name={product_name}&quantity={quantity}",
          "displayText": "修改數量"
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

        message = FlexSendMessage(
            alt_text='還需要購買其他商品嗎?', 
            contents=bubble
        )
        
        return message

    cart.add(product=product_name, num=quantity)
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
    "text": f"加入購物車: {product_name} x {quantity}",
    "color": "#000000"
  },
  {
    "type": "text",
    "margin": "none",
    "wrap": True,
    "text": '''還有需要其他商品嗎?
若沒有，點擊購物車可以查看目前已選購商品''',
    "margin": "md",
    "color": "#000000"
  }
  ,
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
      "type": "message",
      "label": "繼續買",
      "text": "繼續買"
    },
    "style": "link"
  },
  {
    "type": "button",
    "action": {
      "type": "message",
      "label": "購物車",
      "text": "購物車"
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

    message = FlexSendMessage(
        alt_text='還需要購買其他商品嗎?', 
        contents=bubble
    )

    return message

# 修改購物車裡的商品數量
def edit_cart_product_quantity(event):
    data = dict(parse_qsl(event.postback.data))
    print('edit_product_quantity', data)

    product_name = data.get('product_name')
    quantity = data.get('quantity')

    cart = Cart(user_id=event.source.user_id)
    cart.add(product=product_name, num=quantity)

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
    "text": f"已修改成: {product_name} x {quantity}",
    "color": "#000000"
  },
  {
    "type": "text",
    "margin": "none",
    "wrap": True,
    "text": '''還有需要其他商品嗎?
若沒有，點擊購物車可以查看目前已選購商品''',
    "margin": "md",
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
      "type": "message",
      "label": "繼續買",
      "text": "繼續買"
    },
    "style": "link"
  },
  {
    "type": "button",
    "action": {
      "type": "message",
      "label": "購物車",
      "text": "購物車"
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

    message = FlexSendMessage(
        alt_text='還需要購買其他商品嗎?', 
        contents=bubble
    )

    return line_bot_api.reply_message(
        event.reply_token,
        message
    )

# 刪除購物車裡的商品
def delete_product_in_cart(event, message_text):
    name = message_text.split(" ")[1]
    cart = Cart(user_id=event.source.user_id)
    cart.delete(name)
    message = shopping_cart(event)
    bubble = text_bubble(f'已刪除 {name}')
    text_message = FlexSendMessage(alt_text=f'已刪除 {name}', contents=bubble)
    return [text_message, message]

# 購物車
def shopping_cart(event):
    user_id = event.source.user_id

    # 若結帳後未付款
    line_user = LineUser.objects.filter(line_id=user_id).first()
    order = Order.objects.filter(line_user=line_user, is_pay=False).first()

    if order:
        order_no_pay(event, order.id)

    cart = Cart(user_id=user_id)

    if cart.bucket():#當購物車裡面有東西時
      message = cart.shopping_cart() #就會使用 display()顯示購物車內容
    else:
      bubble = text_bubble('您的購物車是空的')
      message = FlexSendMessage(alt_text="您的購物車是空的", contents=bubble)

    return message

# 重置購物車
def shopping_cart_reset(event):
    cart = Cart(user_id=event.source.user_id)
    cart.reset()

    bubble = text_bubble('已清空購物車')
    text_message = FlexSendMessage(alt_text='已清空購物車', contents=bubble)

    return line_bot_api.reply_message(
        event.reply_token,
        text_message
    )

# 選擇取貨方式
def select_pickup_method(event):
  bubble = {
  "type": "bubble",
  "body": {
    "type": "box",
    "layout": "vertical",
    "spacing": "sm",
    "contents": [
      {
        "type": "text",
        "wrap": True,
        "text": "選擇取貨方式",
        "size": "lg",
        "align": "center",
        "color": "#000000"
      },
      {
        "type": "separator",
        "color": "#b3b3b3",
        "margin": "lg"
      }
    ]
  },
  "footer": {
    "type": "box",
    "layout": "vertical",
    "spacing": "md",
    "contents": [
      {
        "type": "box",
        "layout": "horizontal",
        "contents": [
          {
            "type": "button",
            "action": {
              "type": "postback",
              "label": "來店取",
              "data": "action=order_confirm",
              "displayText": "來店取"
            },
            "style": "secondary",
            "color": "#9e9e9e",
            "flex": 2
          },
          {
            "type": "button",
            "action": {
              "type": "uri",
              "label": "寄至指定地點",
              "uri": "http://linecorp.com/"
            },
            "action": {
              "type": "uri",
              "label": "寄送至指定地點",
              "uri": 'line://oaMessage/{base_id}/?{message}'.format(base_id='@244cbsrk', # 請用自己的
                message=quote('請勿新增或刪除任何文字，\n請輸入要寄送的地址\n地址:'))
            },
            "color": "#9e9e9e",
            "style": "secondary",
            "flex": 3
          }
        ],
        "spacing": "md"
      }
    ],
    "paddingTop": "none"
  },
  "styles": {
    "body": {
      "backgroundColor": "#d1ccca"
    },
    "footer": {
      "backgroundColor": "#d1ccca"
    }
  }
}

  flex_message = FlexSendMessage(alt_text="選擇取貨方式", contents=bubble)
  line_bot_api.reply_message(event.reply_token, flex_message)

# 寄送指定地點文字輸入
def delivery_to_address_text(event, message_text):
    # 檢查文字
    first_text_check = '請勿新增或刪除任何文字，\n請輸入要寄送的地址\n地址:'
    address = message_text.split(first_text_check)[1].strip()
    order_confirm(event, address)
    
# 訂單確認
def order_confirm(event, address=None):
    admin_setting = AdminSetting.objects.first()
    company_name = admin_setting.company_name
    company_address = admin_setting.company_address
    if address:
      pickup_method = '寄送指定地點'
    else:
      pickup_method = '來店取'
      address = f'({company_name}) {company_address}'

    print(pickup_method, address)
    user_id = event.source.user_id

    # 若結帳後未付款
    line_user = LineUser.objects.filter(line_id=user_id).first()
    order = Order.objects.filter(line_user=line_user, is_pay=False).first()

    if order:
        order_no_pay(event, order.id)

    cart = Cart(user_id=user_id)

    if cart.bucket():# 當購物車裡面有東西時
      message = cart.order_confirm(pickup_method, address)
    else:
      bubble = text_bubble('您的購物車是空的')
      message = FlexSendMessage(alt_text="您的購物車是空的", contents=bubble)

    line_bot_api.reply_message(event.reply_token, message)

# 建立訂單
def order_create(event):
    user_id = event.source.user_id
    cart = Cart(user_id=user_id)
    line_user = LineUser.objects.filter(line_id=user_id).first()
    order = Order.objects.filter(line_user=line_user, is_pay=False).first()

    # 若已建立訂單後未付款
    warning_text = None
    if order:
        warning_text = '訂單已經建立過了'

    # 若重複按建立訂單會檢查購物車裡面有沒有資料(因建立訂單會清空購物車)，會 return
    if not cart.bucket():
        warning_text = '訂單已經建立過了'

    if warning_text:   
        bubble = text_bubble(warning_text)
        text_message = FlexSendMessage(alt_text=warning_text, contents=bubble)
        return line_bot_api.reply_message(event.reply_token, text_message)

    total_price = 0 # 總金額
    items = [] # 暫存訂單項目
    warning_text_list = []

    for name, quantity in cart.bucket().items():
        product = Product.objects.filter(name=name).first()
        product_quantity = int(product.quantity)
        
        # 如果商品售罄
        if product_quantity <= 0:
          warning_text_list.append(f'{name} 已售罄')
          
        elif product_quantity < quantity :
          warning_text_list.append(f'{name} 只剩{product_quantity}個')
            
        total_price += product.price * int(quantity)
        item = Item()
        item.name = name
        item.price = product.price
        item.quantity = int(quantity)
        item.image_url = product.image_url
        items.append(item)

    if len(warning_text_list) != 0:
        warning_text = '\n'.join(warning_text_list)
        if '只剩' in warning_text:
            warning_text += '\n請修改(購買數量)，再建立訂單'
            size = None
        else:
            size = "micro"

        bubble = text_bubble(warning_text, size)
        text_message = FlexSendMessage(alt_text='請修改數量再建立訂單', contents=bubble)
        return line_bot_api.reply_message(event.reply_token, text_message)

    #建立LinePay的物件
    line_pay = LinePay()
    order_id = uuid.uuid4().hex

    #再使用line_pay.pay的方法，最後就會回覆像postman的格式
    info = line_pay.pay(
        product_name='消費金額',
        amount=total_price,
        order_id=order_id,
        product_image_url=settings.STORE_IMAGE_URL
    )
    # print('info: ', info)
    # info:  {'paymentUrl': {'web': 'https://sandbox-web-pay.line.me/web/payment/wait?transactionReserveId=c1U4d1dvaDlndEg0V3FWR1VORTFFbWN2amkwTXRJaXR4ay9mTGRuNysxVXphZ1JaaXBlMlY5M0MwbEpPVHRIeg', 
    #         'app': 'line://pay/payment/c1U4d1dvaDlndEg0V3FWR1VORTFFbWN2amkwTXRJaXR4ay9mTGRuNysxVXphZ1JaaXBlMlY5M0MwbEpPVHRIeg'}, 
    #         'transactionId': 2023101602024262310, 'paymentAccessToken': '256146199953'}
    #取得付款連結和transactionId後(linepay.py  def _check_response(self, response))
    pay_web_url = info['paymentUrl']['web'] # 真正會付錢的 url
    transaction_id = info['transactionId']
    data = dict(parse_qsl(event.postback.data))
    pickup_method = data.get('pickup_method')
    address = data.get('address')

    order = Order.objects.create(
        line_user = line_user,
        transaction_id = transaction_id,
        pickup_method = pickup_method,
        total_price = total_price, 
        address = address,
        is_pay = False,
    )

    for item in items:
        item.order = order
        item.save()

    #訂單項目物件都建立後就會清空購物車
    cart.reset()

    #最後告知用戶並提醒付款
    bubble = {
  "type": "bubble",
  "size": "kilo",
  "body": {
    "type": "box",
    "layout": "horizontal",
    "spacing": "sm",
    "contents": [
      {
        "type": "text",
        "margin": "none",
        "wrap": True,
        "text": "訂單建立成功!",
        "color": "#000000"
      },
      {
        "type": "text",
        "margin": "none",
        "wrap": True,
        "text": f"總價: ${total_price}",
        "align": "end",
        "color": "#000000"
      }
    ],
    "paddingBottom": "lg"
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
          "label": "刪除訂單",
          "data": f"action=order_delete&id={order.id}"
        },
        "style": "link"
      },
      {
        "type": "button",
        "action": {
          "type": "uri",
          "label": "點擊付款",
          "uri": pay_web_url
        },
        "style": "link"
      }
    ]
  },
  "styles": {
    "body": {
      "backgroundColor": "#d1ccca"
    },
    "footer": {
      "backgroundColor": "#d1ccca",
      "separator": True,
      "separatorColor": "#bdbdbd"
    }
  }
}
    
    flex_message = FlexSendMessage(
        alt_text="訂單建立成功!!",
        contents=bubble
    )

    line_bot_api.reply_message(event.reply_token, flex_message)

# 刪除訂單
def order_delete(event):
    data = dict(parse_qsl(event.postback.data))
    print('order_delete', data)
    id = data.get('id')
    # 只能刪除 is_pay = False(有可能之後再按)
    order = Order.objects.filter(id=int(id), is_pay=False).first()
    
    if order:
      order.delete()

    bubble = text_bubble('訂單已經刪除')
    text_message = FlexSendMessage(alt_text='訂單已經刪除',contents=bubble)

    line_bot_api.reply_message(
        event.reply_token,
        text_message
    )

# 建立訂單後未付款，按'加入購物車'或'購物車'會跑這
# 因為 pay_web_url 不知道有沒有時效限制，所以會取得之前的購買資訊
# 然後重建訂單，取得新的 pay_web_url
def order_no_pay(event, check_id=None):
    if check_id: 
      id = check_id
    else:
      data = dict(parse_qsl(event.postback.data))
      print('order_no_pay', data)
      id = data.get('id')
      
    order = Order.objects.filter(id=int(id)).first()
    items = Item.objects.filter(order=order)
    total_price = sum([item.price * item.quantity for item in items])
    created_at = timezone.localtime(order.created_at).strftime("%Y-%m-%d %H:%M:%S")

    product_box_component = [
      {
        "type": "text",
        "wrap": True,
        "text": "有訂單未付款",
        "size": "lg",
        "align": "center",
        "color": "#d32f2f"
      },
      {
        "type": "text",
        "text": f"({created_at})",
        "size": "sm",
        "align": "center",
        "offsetBottom": "xs",
        "color": "#000000"
      },
      {
        "type": "separator",
        "color": "#b3b3b3",
        "margin": "md"
      }
    ]  
    
    for item in items:
        name = item.name
        price = item.price
        quantity = item.quantity
        product_box_component.extend([
        {
          "type": "box",
          "layout": "horizontal",
          "contents": [
            {
              "type": "text",
              "wrap": True,
              "text": f"{name} (${price} x {quantity})",
              "size": "sm",
              "color": "#000000"
            },
            {
              "type": "text",
              "wrap": True,
              "text": f"$ {price * int(quantity)}",
              "align": "end",
              "size": "sm",
              "color": "#000000"
            }
          ],
          "paddingTop": "lg",
          "paddingBottom": "lg"
        },
        {
          "type": "separator",
          "color": "#b3b3b3"
        }
      ])
    
    product_box_component.extend([
      {
      "type": "box",
      "layout": "horizontal",
      "contents": [
        {
          "type": "text",
          "margin": "none",
          "wrap": True,
          "text": "總價",
          "color": "#009688",
          "size": "sm",
          "weight": "bold"
        },
        {
          "type": "text",
          "margin": "none",
          "wrap": True,
          "text": f"NT$ {total_price}",
          "align": "end",
          "color": "#009688",
          "size": "sm",
          "weight": "bold"
        }
      ],
      "paddingTop": "lg",
      "paddingBottom": "lg"
      },
      {
        "type": "separator",
        "color": "#b3b3b3"
      },
      {
        "type": "text",
        "text": "<備註> (重建訂單)後會來到購物車，並且加入您上次未付款的商品，您可以再追加或刪除商品，確定之後請按(選擇取貨方式)，最後在建立訂單",
        "size": "sm",
        "margin": "lg",
        "color": "#000000",
        "wrap": True
      }
    ])

    bubble = {
"type": "bubble",
"body": {
"type": "box",
"layout": "vertical",
"spacing": "sm",
"contents": product_box_component
},
  "footer": {
    "type": "box",
    "layout": "vertical",
    "spacing": "md",
    "contents": [
      {
        "type": "box",
        "layout": "horizontal",
        "contents": [
          {
            "type": "button",
            "action": {
              "type": "postback",
              "label": "刪除訂單",
              "data": f"action=order_delete&id={id}"
            },
            "style": "link"
          },
          {
            "type": "button",
            "action": {
              "type": "message",
              "label": "重建訂單",
              "text": "重建訂單"
            },
            "style": "link"
          }
        ],
        "spacing": "md"
      }
    ]
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
    
    text_bubble = {
  "type": "bubble",
  "size": "kilo",
  "body": {
    "type": "box",
    "layout": "vertical",
    "spacing": "sm",
    "contents": [
      {
        "type": "text",
        "text": "⚠️",
        "align": "center"
      },
      {
        "type": "text",
        "wrap": True,
        "text": "已偵測到之前有建立訂單但尚未付款，必須先(刪除)或(重建)訂單才能進行其他操作",
        "margin": "md",
        "color": "#000000"
      }
    ],
    "paddingBottom": "xl"
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
    
    text_message = FlexSendMessage(
        alt_text="重建訂單",
        contents=text_bubble
    )

    flex_message = FlexSendMessage(
        alt_text='重建訂單',
        contents=bubble
    )

    return line_bot_api.reply_message(
        event.reply_token,
        [text_message, flex_message]
    )

# 重建訂單
def order_rebuild(event):
    user_id = event.source.user_id
    line_user = LineUser.objects.filter(line_id=user_id).first()
    order = Order.objects.filter(line_user=line_user, is_pay=False).first()

    if not order:
        bubble = bubble = text_bubble('訂單已經刪除')
        text_message = FlexSendMessage(alt_text="訂單已經刪除", contents=bubble)
        return line_bot_api.reply_message(event.reply_token, text_message)

    items = Item.objects.filter(order=order)
    cart = Cart(user_id=user_id)

    # 將舊訂單的商品加入購物車
    for item in items:
        product_name = item.name
        product_quantity = item.quantity
        cart.add(product=product_name, num=product_quantity)

    order.delete()

    bubble = text_bubble('已將上次未付款的所有商品加入到購物車')
    text_message = FlexSendMessage(alt_text="重建訂單", contents=bubble)
    flex_message = cart.shopping_cart()

    return line_bot_api.reply_message(
        event.reply_token,
        [text_message, flex_message]
    )

# line_pay 確認
def line_pay_confirm(request):
    print(request)
    transaction_id = request.GET.get('transactionId')
    order = Order.objects.filter(transaction_id=transaction_id).first()
    items = Item.objects.filter(order=order)
    total_price = sum([int(item.price) * item.quantity for item in items])

    if order:
        line_pay = LinePay()
        line_pay.confirm(transaction_id=transaction_id, amount=total_price)

        order.transaction_time = datetime.now(desired_timezone)
        order.is_pay = True
        order.save()

        # 成功付錢之後會'減去'該商品購買量的庫存
        # 目前無法使用 signals 就算 post_save Order 還是無法抓到 item 資料(空直)
        # instance 抓不到剛剛建立的 Itme 資訊(可能因為 order 建立比較早，然後
        # 直接抓資料，但 Item 還沒建立)
        for item in items:
          name = item.name
          quantity = item.quantity
          product = Product.objects.filter(name=name).first()
          product.quantity -= quantity
          product.save()
        
        #傳收據給用戶
        # message = display_receipt(transaction_id)
        # line_bot_api.push_message(to=order.line_user.line_id, messages=message)

        return HttpResponse('<h1>您的支付成功! ! 感謝您的購買</h1>')

# 收據
def display_receipt(transaction_id="2024061702142419610"):
    company_name = AdminSetting.objects.first().company_name
    order = Order.objects.filter(transaction_id=transaction_id).first()
    items = Item.objects.filter(order=order)
    line_user_name = order.line_user.display_name
    total_price = sum([item.price * item.quantity for item in items])
    pickup_method = order.pickup_method
    address = order.address
    transaction_date = timezone.localtime(order.transaction_time).strftime("%Y-%m-%d %H:%M:%S")
 
    contents = [
       {
        "type": "box",
        "layout": "horizontal",
        "contents": [
          {
            "type": "box",
            "layout": "horizontal",
            "contents": [
              {
                "type": "text",
                "text": "LINE",
                "size": "md",
                "flex": 1,
                "weight": "bold"
              },
              {
                "type": "box",
                "layout": "vertical",
                "contents": [
                  {
                    "type": "text",
                    "text": "Pay",
                    "color": "#ffffff",
                    "size": "sm"
                  }
                ],
                "backgroundColor": "#1DB446",
                "width": "34px",
                "paddingStart": "5px"
              }
            ],
            "width": "74px"
          },
          {
            "type": "text",
            "text": "收據",
            "weight": "bold",
            "size": "md",
            "align": "end"
          }
        ]
      },
      {
        "type": "text",
        "wrap": True,
        "text": company_name,
        "size": "3xl",
        "weight": "bold",
        "margin": "md"
      },
      {
        "type": "text",
        "text": "商品:",
        "size": "sm",
        "margin": "lg",
        "color": "#000000"
      },
      {
        "type": "separator",
        "color": "#b3b3b3",
        "margin": "md"
      },
    ]
    
    for item in items:
      name = item.name
      price = item.price
      quantity = item.quantity

      contents.extend([
        {
        "type": "box",
        "layout": "horizontal",
        "contents": [
          {
            "type": "text",
            "wrap": True,
            "text": f"{name} (${price} x {quantity})",
            "size": "sm",
            "flex": 3,
            "color": "#000000"
          },
          {
            "type": "text",
            "wrap": True,
            "text": f"$ {price * quantity}",
            "align": "end",
            "size": "sm",
            "flex": 1,
            "color": "#000000"
          }
        ],
        "paddingTop": "lg",
        "paddingBottom": "lg"
        },
        {
          "type": "separator",
          "color": "#b3b3b3"
        }
      ])

    contents.append({
        "type": "box",
        "layout": "horizontal",
        "contents": [
          {
            "type": "text",
            "wrap": True,
            "text": "總價",
            "color": "#009688",
            "size": "xs",
            "weight": "bold"
          },
          {
            "type": "text",
            "wrap": True,
            "text": f"$ {total_price}",
            "align": "end",
            "color": "#009688",
            "size": "sm",
            "weight": "bold"
          }
        ],
        "paddingTop": "lg"
      })
    
    bubble = {
  "type": "bubble",
  "body": {
    "type": "box",
    "layout": "vertical",
    "contents": contents,
    "spacing": "sm",
    "paddingBottom": "xl"
  },
  "footer": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "box",
        "layout": "horizontal",
        "contents": [
          {
            "type": "text",
            "text": "交易編號:",
            "position": "absolute",
            "size": "sm",
            "color": "#000000"
          },
          {
            "type": "text",
            "text": transaction_id,
            "align": "end",
            "size": "sm",
            "color": "#000000"
          }
        ]
      },
      {
        "type": "box",
        "layout": "horizontal",
        "contents": [
          {
            "type": "text",
            "text": "交易日期:",
            "position": "absolute",
            "size": "sm",
            "color": "#000000"
          },
          {
            "type": "text",
            "text": transaction_date,
            "align": "end",
            "size": "sm",
            "color": "#000000"
          }
        ]
      },
      {
        "type": "box",
        "layout": "horizontal",
        "contents": [
          {
            "type": "text",
            "text": "取貨人:",
            "position": "absolute",
            "size": "sm",
            "color": "#000000"
          },
          {
            "type": "text",
            "text": line_user_name,
            "align": "end",
            "size": "sm",
            "color": "#000000"
          }
        ]
      },
      {
        "type": "box",
        "layout": "horizontal",
        "contents": [
          {
            "type": "text",
            "text": "取貨方式:",
            "position": "absolute",
            "size": "sm",
            "color": "#000000"
          },
          {
            "type": "text",
            "text": pickup_method,
            "align": "end",
            "size": "sm",
            "color": "#000000"
          }
        ]
      },
      {
        "type": "box",
        "layout": "horizontal",
        "contents": [
          {
            "type": "text",
            "text": "取貨地址:",
            "size": "sm",
            "color": "#000000",
            "flex": 1,
            "wrap": True
          },
          {
            "type": "text",
            "text": address,
            "size": "sm",
            "color": "#000000",
            "flex": 3,
            "wrap": True,
            "align": "end"
          }
        ]
      }
    ],
    "paddingStart": "xxl",
    "paddingEnd": "xxl",
    "paddingTop": "lg",
    "paddingBottom": "lg",
    "spacing": "sm"
  },
  "styles": {
    "body": {
      "backgroundColor": "#d1ccca"
    },
    "footer": {
      "backgroundColor": "#d1ccca",
      "separatorColor": "#b3b3b3",
      "separator": True
    }
  }
}

    flex_message = FlexSendMessage(
        alt_text='請確認收據~',
        contents=bubble
    )
    
    return flex_message

    # line_bot_api.reply_message(
    #     event.reply_token,
    #     flex_message
    # )
