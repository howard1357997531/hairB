from rest_framework.serializers import ModelSerializer
from mainapp.models import LineUser
from .models import *

class LineUserSerializer(ModelSerializer):
    class Meta:
        model = LineUser
        fields = ('display_name', 'picture_url')

class ReservationSerializer(ModelSerializer):
    # 向上從 lineUser 拿資料，不能設定 many = True
    line_user = LineUserSerializer(required=True)

    class Meta:
        model = Reservation
        fields = ('id', 'line_user', 'date', 'designer', 'service', 'add_service')

class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'price', 'quantity', 'image_url', 'description', 'created_at')

class ItemSerializer(ModelSerializer):
    class Meta:
        model = Item
        fields = ('id', 'order', 'name', 'price', 'quantity', 'image_url', 'created_at')

class OrderSerializer(ModelSerializer):
    line_user = LineUserSerializer(required=False)
    items = ItemSerializer(many=True, required=False)
    class Meta:
        model = Order
        fields = ('id', 'line_user', 'transaction_id', 'transaction_time', 'shipping_state',
            'pickup_method', 'total_price', 'address', 'is_pay', 'created_at', 'items')



