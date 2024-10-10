from django.db import models
from django.utils import timezone
from mainapp.models import LineUser, StaffSchedule
from linebot.models import *
from urllib.parse import quote
from datetime import datetime

class Common(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Reservation(Common):
    line_user = models.ForeignKey(LineUser, on_delete=models.CASCADE, related_name='line_user', null=True, blank=True)
    staff_schedule = models.ForeignKey(StaffSchedule, on_delete=models.CASCADE, related_name='reservation', null=True, blank=True)
    designer = models.ForeignKey(LineUser, on_delete=models.CASCADE, related_name='designer', null=True, blank=True)
    date = models.DateTimeField(default=datetime.now())
    service = models.CharField(max_length=255, null=True, blank=True)
    add_service = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return str(self.staff_schedule.date)

class Product(Common):
    name = models.CharField(max_length=255, unique=True, null=True, blank=True)
    price = models.PositiveIntegerField(default=0)
    quantity = models.PositiveIntegerField(default=0)
    image_url = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)

    @staticmethod
    def list_all():
        products = Product.objects.all()

        bubbles = []

        for product in products:
            bubble = BubbleContainer(
                hero=ImageComponent(
                    size='full',
                    aspect_ratio='20:13',
                    aspect_mode='cover',
                    url=product.image_url
                ),
                body=BoxComponent(
                    layout='vertical',
                    contents=[
                        TextComponent(text=product.name,#產品名稱
                                      wrap=True,
                                      weight='bold',
                                      size='xl'),
                        BoxComponent(#產品價格
                            layout='baseline',
                            contents=[#利用format的方法把product.price轉換成字串
                                TextComponent(text='NT${price}'.format(price=product.price),
                                              wrap=True,
                                              weight='bold',
                                              size='xl')
                            ]
                        ),
                        TextComponent(margin='md',#產品敘述 如果product.description or ''是空值的話就直接回傳空字串
                                      text='{des}'.format(des=product.description or ''),
                                      wrap=True,
                                      size='xs',
                                      color='#aaaaaa')
                    ],
                ),
                footer=BoxComponent(#購物車按鈕
                    layout='vertical',
                    spacing='sm',
                    contents=[
                        ButtonComponent(
                            style='primary',
                            color='#a1887f',
                            action=URIAction(label='加入購物車',
                                             uri='line://oaMessage/{base_id}/?{message}'.format(base_id='@244cbsrk', # 請用自己的
                                                                                                message=quote("{product}, 購買數量:".format(product=product.name)))),
                        )
                    ]
                )
            )

            bubbles.append(bubble)

        carousel_container = CarouselContainer(contents=bubbles)

        message = FlexSendMessage(alt_text='請選購商品', contents=carousel_container)

        return message

    def __str__(self):
        return str(self.name)

SHIPPING_STATE_CHOICES = (
    ('運送中', '運送中'),
    ('已送達', '已送達'),
)

PICKUP_METHOD_CHOICES = (
    ('來店取', '來店取'),
    ('寄送指定地點', '寄送指定地點'),
)
class Order(Common):
    line_user = models.ForeignKey(LineUser, on_delete=models.CASCADE, null=True, blank=True)
    transaction_id = models.CharField(max_length=255, null=True, blank=True)
    transaction_time = models.DateTimeField(default=timezone.now)
    shipping_state = models.CharField(max_length=255, default='運送中', choices=SHIPPING_STATE_CHOICES)
    pickup_method = models.CharField(max_length=255, default='來店取', choices=PICKUP_METHOD_CHOICES)
    total_price = models.IntegerField(default=0)
    address = models.CharField(max_length=255, null=True, blank=True)
    is_pay = models.BooleanField(default=False)
    

    # 新增收據
    @staticmethod
    def display_receipt(transaction_id):
        total_price = 0
        item_box_component = []
        order = Order.objects.filter(transaction_id=transaction_id).first()
        # items = order.item_set.all()
        items = Item.objects.filter(order=order)

        for item in items:#透過self.items取得訂單明細項目
            total_price += item.quantity * item.price
            item_box_component.append(BoxComponent(
                layout='horizontal',
                contents=[
                    TextComponent(text='{quantity} x {product_name}'.
                                  format(quantity=item.quantity,
                                         product_name=item.product.name),
                                  size='sm',
                                  color='#555555',
                                  flex=0), 
                    TextComponent(text='NT${amount}'.
                                  format(amount=(item.quantity * item.price)),
                                  size='sm',
                                  color='#111111',
                                  align='end')]
            ))

        #產生資料後就append到item_box_component等等會用到
        #透過BubbleContainer產生收據格式
        bubble = BubbleContainer(
            direction='ltr',
            body=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(text='收據',
                                  weight='bold',
                                  color='#1DB446',
                                  size='sm'),
                    TextComponent(text='Fashion Salon',
                                  weight='bold',
                                  size='xxl',
                                  margin='md'),
                    TextComponent(text='線上商城',
                                  size='xs',
                                  color='#aaaaaa',
                                  wrap=True),
                    SeparatorComponent(margin='xxl'),
                    BoxComponent(
                        layout='vertical',
                        margin='xxl',
                        spacing='sm',
                        contents=item_box_component#透過for迴圈產生的訂單明細
                    ),
                    SeparatorComponent(margin='xxl'),#分隔線
                    BoxComponent(
                        layout='vertical',
                        margin='xxl',
                        spacing='sm',
                        contents=[
                            BoxComponent(
                                layout='horizontal',
                                contents=[#顯示總金額
                                    TextComponent(text='總價:',
                                                  size='sm',
                                                  color='#555555',
                                                  flex=0),
                                    TextComponent(text=f'NT${total_price}',
                                                  size='sm',
                                                  color='#111111',
                                                  align='end')]
                            )

                        ]
                    )
                ],
            )
        )
        message = FlexSendMessage(alt_text='請確認收據~', contents=bubble)

        return message

    def __str__(self):
        return f'{self.line_user} {self.transaction_id}'

# 不建議跟 product 設為 ForeignKey 因為要是刪除 product
# 到時候查詢 order 的 item 資訊會不見
class Item(Common):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    price = models.PositiveIntegerField(default=0)
    quantity = models.PositiveIntegerField(default=0)
    image_url = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f'{self.order.line_user.display_name} - {self.order.transaction_id}' 
