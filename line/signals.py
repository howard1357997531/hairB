from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from .models import Product, Order, Item, Reservation
from mainapp.models import *
from mainapp.serializers import StaffScheduleSerializer, StaffCommonSettingSerializer
from .tool import  parse_schedule

# # 刪除訂單、重建訂單，都會刪除訂單(會把原本要購買商品的數量'加回'庫存)
# # 不能用 post_delete 因為 order 刪除後 item 也會跟這著刪除
# @receiver(pre_delete, sender=Order)
# def Order_pre_delete_signals(sender, instance, **kwargs):
#     items = Item.objects.filter(order=instance)
#     print(items)
#     for item in items:
#         name = item.product.name
#         quantity = item.quantity

#         # 商品的庫存'加回'取消訂單後的購買量
#         product = Product.objects.filter(name=name).first()
#         product.quantity += quantity
#         product.save()

# pre_save 抓到的instance是儲存後的，所以要抓儲存前要用
# sender.objects.filter(id=instance.id).first()
# 儲存前，舊設計師當天預約扣一，所以一定不會滿，要 is_full = False
@receiver(pre_save, sender=Reservation)
def Reservation_pre_save_signals(sender, instance, **kwargs):
    # 如果是建立，儲存前不會有id，要檢查
    if instance.id:
        date = instance.date
        year = date.year; month = date.month; day = date.day
        pre_designer = sender.objects.filter(id=instance.id).first()
        designer = pre_designer.designer
        staff = Staff.objects.filter(line_user=designer).first()
        staff_schedule = StaffSchedule.objects.filter(staff=staff, date__year=year, date__month=month, date__day=day).first()
        staff_schedule.is_full = False
        staff_schedule.save()

# 檢查儲存後，新設計師當天預約是否有滿約
@receiver(post_save, sender=Reservation)
def Reservation_post_save_signals(sender, instance, created, **kwargs):
    date = instance.date
    year = date.year; month = date.month; day = date.day
    designer = instance.designer
    staff = Staff.objects.filter(line_user=designer).first()
    admin_data = AdminSetting.objects.first()
    staff_schedule = StaffSchedule.objects.filter(staff=staff, date__year=year, date__month=month, date__day=day).first()
    staff_schedule_serializer = StaffScheduleSerializer(staff_schedule, many=False)
    common = StaffCommonSetting.objects.filter(staff=staff)
    common_serializer = StaffCommonSettingSerializer(common, many=True)

    # 取得此設計師'當天'所有可預約時間
    time_list = parse_schedule(admin_data, staff_schedule_serializer.data, common_serializer.data)
    print('asd',time_list)

    has_reservations_list = Reservation.objects.filter(designer=designer, date__year=year, date__month=month, date__day=day)
    print('asd', has_reservations_list.count())

    if len(time_list) == len(has_reservations_list):
        staff_schedule.is_full = True
        staff_schedule.save()

# 只要刪除預約，設計師的排班一定不會滿
@receiver(post_delete, sender=Reservation)
def Reservation_post_delete_signals(sender, instance, **kwargs):
    date = instance.date
    year = date.year; month = date.month; day = date.day
    designer = instance.designer
    staff = Staff.objects.filter(line_user=designer).first()
    staff_schedule = StaffSchedule.objects.filter(staff=staff, date__year=year, date__month=month, date__day=day).first()
    staff_schedule.is_full = False
    staff_schedule.save()
    print('asdasd')


