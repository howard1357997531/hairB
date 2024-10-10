from django.shortcuts import render
from django.db.models import Q
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import *

from .models import *
from line.models import Product, Order, Reservation
from line.serializers import ProductSerializer, OrderSerializer
from line.tool import get_year_month_of_next_month
import time
from datetime import datetime, timedelta
import pytz 

desired_timezone = pytz.timezone('Asia/Taipei')
time_sleep = 0

def index(request):
    return render(request, 'index.html', locals()) 

# 取得個別 lineUser 的資料
@api_view(['POST'])
def get_lineUser_data(request):
    try:
        print(request.data)
        line_id = request.data.get('userId')
        line_user = LineUser.objects.filter(line_id=line_id).first()
        serializer = LineUserSerializer(line_user, many=False)
        return Response(serializer.data, status=200)
    except:
        return Response(status=400)

# 取得所有沒被設定成 admin 或 staff 的 lineUser
@api_view(['GET', 'POST'])
def lineUser_list(request):
    time.sleep(time_sleep)
    try:
        if request.method =='GET':
            state = request.GET.get('state')
            if state == 'admin':
                line_user = LineUser.objects.filter(is_admin=False).order_by('-id')
            elif state == 'staff':
                line_user = LineUser.objects.filter(is_staff=False).order_by('-id')
            serializer = LineUserSerializer(line_user, many=True)
            return Response(serializer.data, status=200)
        
        elif request.method == 'POST':
            id = request.data.get('id')
            state = request.data.get('state')
            line_user = LineUser.objects.filter(id=int(id)).first()
            if state == 'admin':
                # 成為'管理員'會默認也成為'員工'
                line_user.is_admin = True
                line_user.is_staff = True
                line_user.become_admin_time = datetime.now(desired_timezone)
                line_user.become_staff_time = datetime.now(desired_timezone)
                line_user.save()
            elif state == 'staff':
                line_user.is_staff = True
                line_user.become_staff_time = datetime.now(desired_timezone)
                line_user.save()

                staff = Staff.objects.filter(line_user=line_user).first()
                # 檢查 staff 是否已經創建過
                if staff:
                    staff.is_delete = False
                    staff.save()
                else:
                    Staff.objects.create(line_user=line_user)

            serializer = LineUserSerializer(line_user, many=False)
            return Response(serializer.data, status=200)
            
    except:
        return Response(status=404)

@api_view(['GET', 'POST'])
def admin_list(request):
    time.sleep(time_sleep)
    try:
        if request.method == "GET":
            line_user = LineUser.objects.filter(is_admin=True).order_by('-become_admin_time')
            serializer = LineUserSerializer(line_user, many=True)
            return Response(serializer.data, status=200)
        
        elif request.method == 'POST':
            id = request.data.get('id')
            line_user = LineUser.objects.filter(id=int(id)).first()
            # 刪除'管理者'權限不會同時也刪除其'員工'權限
            line_user.is_admin = False
            line_user.save()
            serializer = LineUserSerializer(line_user, many=False)
            return Response(serializer.data, status=200)
    except:
        return Response(status=404)
    
@api_view(['GET', 'POST'])
def staff_list(request):
    time.sleep(time_sleep)
    try:
        if request.method == "GET":
            line_user = LineUser.objects.filter(is_staff=True).order_by('-become_staff_time')
            serializer = LineUserSerializer(line_user, many=True)
            return Response(serializer.data, status=200)
        elif request.method == 'POST':
            id = request.data.get('id')
            line_user = LineUser.objects.filter(id=int(id)).first()
            # 刪除'員工'權限也會一併刪除其'管理者'權限
            line_user.is_admin = False
            line_user.is_staff = False
            line_user.save()
            serializer = LineUserSerializer(line_user, many=False)

            staff = Staff.objects.filter(line_user=line_user).first()
            staff.is_delete = True
            staff.save()

            return Response(serializer.data, status=200)
    except:
        return Response(status=404)

@api_view(['GET', 'POST'])
def product_list(request):
    time.sleep(time_sleep)
    try:
        if request.method == 'GET':
            product = Product.objects.all().order_by('-id')
            serializer = ProductSerializer(product, many=True)
        elif request.method == 'POST':
            data = request.data
            name = data.get('name')
            name_exist = Product.objects.filter(name=name)

            if name_exist:
                return Response('name_exist', status=200)
            
            product = Product.objects.create(**data)
            serializer = ProductSerializer(product, many=False)
        return Response(serializer.data, status=200)
    except:
        return Response('error', status=404)
    
@api_view(['PUT', 'DELETE'])
def product_detail(request, id):
    time.sleep(time_sleep)
    try:
        product = Product.objects.filter(id=int(id)).first()
        if request.method == 'PUT':
            data = request.data
            name = data.get('name')
            name_exist = Product.objects.filter(name=name).exclude(id=int(id))
            
            if name_exist:
                return Response('name_exist', status=200)
        
            serializer = ProductSerializer(product, data=data)

            if serializer.is_valid():
                serializer.save()
            return Response(serializer.data, status=200)
        
        elif request.method == 'DELETE':
            product.delete()
            return Response('ok', status=200)
    except:
        return Response('error', status=404)

@api_view(['GET', 'POST'])
def admin_setting_list(request):
    time.sleep(time_sleep)
    try:
        admin_setting = AdminSetting.objects.all().first()
    except:
        return Response(status=404)
    
    if request.method == 'GET':
        if admin_setting:
            serializer = AdminSettingSerializer(admin_setting, many=False)
            data = serializer.data
        else:
            # 初次設定沒有資料，此為預設值
            # None 到 js 前端會變 null
            data = {
                "company_name": "",
                "company_phone": "",
                "company_address": "",
                "latitude": 0,
                "longitude": 0,
                "work_time" :"09,00,21,00",
                "break_time" : "02,00",
                "can_reservation_time": "10,00,20,00",
                "can_reservation_period": 20,
                "rest_day_for_week": "不設定",
                "rest_day_for_day": None,
                "today_reservation_limit": 2
            }
        return Response(data, status=200)
        
    elif request.method == 'POST':
        data = request.data.get('adminData')
        print(data)
        if admin_setting:
            serializer = AdminSettingSerializer(admin_setting, data=data)
            if serializer.is_valid():
                serializer.save()
            return Response('ok', status=200)
        else:
            AdminSetting.objects.create(**data)
            return Response('ok', status=201)

@api_view(['POST'])
def schedule_list(request):
    try:
        line_id = request.data.get('line_id')
        data = request.data.get('scheduleData')
        date = data.get('date').split(' ')[0].split('/')
        year = int(date[0]); month = int(date[1]); day = int(date[2])
        line_user = LineUser.objects.filter(line_id=line_id).first()
        staff = Staff.objects.filter(line_user=line_user).first()
        schedule = StaffSchedule.objects.filter(staff=staff, date=datetime(year, month, day)).first()
        # print(schedule)
        # print(data)
        if not schedule:
            del data['reservation']
            data['staff'] = staff
            data['date'] = datetime(year, month, day)
            schedule_data = StaffSchedule.objects.create(**data)
            serializer = StaffScheduleSerializer(schedule_data, many=False)
        else:
            # 若要修改，serializer 資料儲存格式不能有 foreign Key 的項目(應該是不能被修改)
            # 資料多或少都不行，除了預設資料 id, createdAt, modifiedAt
            # date 是 datetime 格式，所以必須使用 datetime 格式修改，不能用 str '2024/05/20 00:00'
            del data['staff']
            del data['reservation']
            data['date'] = datetime(year, month, day)
            
            serializer = StaffScheduleSerializer(schedule, data=data)
            if serializer.is_valid():
                serializer.save()
            
            # 若修改後的'預約時段'不包含'已被預約時段'，會刪除那些'已被預約時段'
            reserveNotInNewSchedule = request.data.get('reserveNotInNewSchedule')
            print(reserveNotInNewSchedule)
            if reserveNotInNewSchedule:
                for i in reserveNotInNewSchedule:
                    hour = int(i.split(":")[0])
                    minute = int(i.split(":")[1])
                    reservation = Reservation.objects.filter(designer=line_user,
                date=datetime(year, month, day, hour, minute)).first()
                    reservation.delete()

            # 檢查排班是否 is_full
            schedule_count = request.data.get('scheduleCount')
            reservation_count = Reservation.objects.filter(date__year=year, date__month=month,
                date__day=day).count()
            
            if schedule.is_full:
                if schedule_count > reservation_count:
                    schedule.is_full = False
                    schedule.save()
            else:
                if schedule_count == reservation_count:
                    schedule.is_full = True
                    schedule.save()
            print(schedule_count, reservation_count)

        return Response(serializer.data, status=200)   
    except:
        return Response(status=404)        

@api_view(['GET'])
def schedule_detail(request, line_id, year, month, day):
    if month == 9:
        time.sleep(1)
    try:
        admin_setting = AdminSetting.objects.all().first()
        line_user = LineUser.objects.filter(line_id=line_id).first()
        staff = Staff.objects.filter(line_user=line_user).first()
        select_year, select_month, select_day = (int(year), int(month), int(day))
        next_month_year, next_month = get_year_month_of_next_month(select_year, select_month)
        
        # day != 0 代表精確取得某天資訊 ex: 2024/5/2
        # day == 0 代表取得某年某月全部資訊 ex: 2024/5
        if select_day != 0:
            staff_schedule = StaffSchedule.objects.filter(staff=staff,
                date=datetime(select_year, select_month, select_day))
        else: 
            # 如要只要查詢 2024/5月有無資料，不能使用 date=datetime(2024, 5)，datetime 裡面至少要3個
            # 所以可以用 date__year=2024, date__month=5 或
            # from datetime import date
            # start_date = date(2024, 5, 1)
            # end_date = date(2024, 5, 31)
            # date__range=(start_date, end_date)
            staff_schedule = StaffSchedule.objects.filter(staff=staff)\
                .filter(Q(date__year=select_year, date__month=select_month) | Q(date__year=next_month_year, date__month=next_month))
        staff_common_setting = StaffCommonSetting.objects.filter(staff=staff)
        # 获取当前时区对象
        desired_timezone = timezone.get_current_timezone()
        # 获取当前时间并转换为当前时区的时间
        today = timezone.now().astimezone(desired_timezone).replace(hour=0, minute=0, second=0, microsecond=0)
        has_schedule_day_after_today = StaffSchedule.objects.filter(staff=staff, date__gte=today)
    except: 
        return Response(status=404)

    if request.method == 'GET':
        # print(select_year, select_month, select_day)
        # print(staff_schedule)
        serializer = AdminSettingSerializer(admin_setting, many=False)
        serializer2 = StaffCommonSettingSerializer(staff_common_setting, many=True)
        serializer3 = StaffScheduleSerializer(staff_schedule, many=True)
        highlightedDays = [timezone.localtime(schedule.date).strftime('%Y/%m/%d') \
                           for schedule in has_schedule_day_after_today]
        # print(highlightedDays)

        data = { 
            "adminSetting": serializer.data, 
            "staffCommonSetting": serializer2.data, 
            "staffSchedule": serializer3.data,
            "highlightedDays": highlightedDays
            }
        return Response(data, status=200)

@api_view(['DELETE'])
def schedule_delete(request, id):
    time.sleep(time_sleep)
    try:
        if request.method == 'DELETE':
            # 因 Reservation 的 foreign key 是 StaffSchedule，但同時也其他foreign key
            # 不知道是不是因為這樣導致有 Reservation 存在並且對到 schedule 的情況下，會不能刪除
            staff_schedule = StaffSchedule.objects.filter(id=int(id)).first()
            reservations = Reservation.objects.filter(staff_schedule=staff_schedule)
            if reservations:
                for reservation in reservations:
                    reservation.delete()

            staff_schedule.delete()
            return Response('ok', status=200)
    except:
        return Response('error', status=404)
    
@api_view(['POST'])
def common_setting_list(request):
    time.sleep(time_sleep)
    try:
        id = request.data.get('id')
        line_id = request.data.get('line_id')
        data = request.data.get('commonData')
        name = data.get('name')
        line_user = LineUser.objects.filter(line_id=line_id).first()
        staff = Staff.objects.filter(line_user=line_user).first()
        name_exist = StaffCommonSetting.objects.filter(staff=staff, name=name).exclude(id=int(id))
        print(request.data)
        print(staff)
        if name_exist:
            return Response({'state': 'same name'}, status=200)

        common_setting = StaffCommonSetting.objects.filter(id=int(id)).first()
        
        if common_setting:
            serializer = StaffCommonSettingSerializer(common_setting, data=data)
            if serializer.is_valid():
                serializer.save()
            return Response({'state': 'edit', 'data': serializer.data}, status=200)
        else:
            data['staff'] = staff
            common_setting_data = StaffCommonSetting.objects.create(**data)
            serializer = StaffCommonSettingSerializer(common_setting_data, many=False)
            return Response({'state': 'create', 'data': serializer.data}, status=201)
    except:
        return Response(status=404)

# 建立請假
@api_view(['POST'])
def take_leave_list(request):
    time.sleep(time_sleep)
    try:
        if request.method == 'POST':
            data = request.data
            line_id = data.get('line_id')
            date = data.get('date')
            year = int(date.split('/')[0]); month = int(date.split('/')[1]); day = int(date.split('/')[2])
            line_user = LineUser.objects.filter(line_id=line_id).first()
            staff = Staff.objects.filter(line_user=line_user).first()
            print(data)
            # 檢查此請假時段是否已經存在
            take_leave_check = TakeLeave.objects.filter(staff=staff, date__year=year,
                date__month=month, date__day=day)

            # 同一天可以重複請假，但時段不能重複包含
            if take_leave_check.exists():
                apply_start_time = int(data.get('start_hour')) * 60 + int(data.get('start_minute'))
                apply_end_time = int(data.get('end_hour')) * 60 + int(data.get('end_minute'))

                for take_leave in take_leave_check:
                    start_time = int(take_leave.start_hour) * 60 + int(take_leave.start_minute)
                    end_time = int(take_leave.end_hour) * 60 + int(take_leave.end_minute)
                    print(apply_start_time, apply_end_time, start_time, end_time)
                    # 只要此請假的 apply_start_time 和 apply_end_time 有在範圍內，代表重複時間

                    # 但若這樣寫繪有問題: start_time <= apply_start_time <= end_time or \
                    #                   start_time <= apply_end_time <= end_time:
                    # 因為可能發生: 已有時間 9:00 ~ 12:00，然後要申請 12:00 ~ 15:00，這樣會跑這邊表示重複
                    # 所以要改 start_time <= apply_start_time < end_time
                    if start_time <= apply_start_time < end_time or \
                       start_time < apply_end_time <= end_time:
                        return Response('date exist', status=200)
            
            del data['line_id']
            data['staff'] = staff
            data['date'] = datetime(year, month, day)
            TakeLeave.objects.create(**data)

            # 檢查是否有當天打卡紀錄(沒有的話代表是向未來請假)
            punch = PunchInorOut.objects.filter(staff=staff, date__year=year,
                date__month=month, date__day=day).first()

            if punch:
                punch.is_take_leave = True
                punch.save()
            else:
                # 沒打卡紀錄會建立未來打卡資料，is_take_leave = True
                PunchInorOut.objects.create(
                    staff=staff, 
                    date=datetime(year, month, day),
                    punch_in_time = datetime(year, month, day),
                    punch_out_time = datetime(year, month, day),
                    is_take_leave = True)
        return Response('ok', status=200)
    except:
        return Response('error', status=404)

@api_view(['GET'])
def take_leave_detail(request, line_id, date):
    time.sleep(time_sleep)
    try:
        line_user = LineUser.objects.filter(line_id=line_id).first()
        staff = Staff.objects.filter(line_user=line_user).first()

        if date == "all_data":
            take_leave = TakeLeave.objects.filter(staff=staff).order_by('-date')
        else:
            print(date)
            date = date.split('-')
            year = int(date[0]); month = int(date[1]); day = int(date[2])
            take_leave = TakeLeave.objects.filter(staff=staff, 
                date=datetime(year, month, day)).order_by('-id')
    except:
        return Response('error', status=404)
    
    if request.method == 'GET':
        serilaizer = TakeLeaveSerializer(take_leave, many=True)
        return Response(serilaizer.data, status=200)

@api_view(['DELETE'])
def take_leave_delete(request, id):
    time.sleep(time_sleep)
    try:
        take_leave = TakeLeave.objects.filter(id=int(id)).first()
        staff = take_leave.staff
        date = timezone.localtime(take_leave.date)
        year = date.year; month=date.month; day=date.day
        take_leave.delete()
        
        # 因為同一天可以請超過一次假，先檢查同一天還有沒有其他假
        take_leave_check = TakeLeave.objects.filter(staff=staff, date__year=year,
            date__month=month, date__day=day)
        
        if not take_leave_check:
            punch = PunchInorOut.objects.filter(staff=staff, date__year=year,
            date__month=month, date__day=day).first()

            if not punch.is_take_leave_approve:
                punch.is_take_leave = False
                punch.save()

        return Response("ok", status=200)
    except:
        return Response('error', status=400)

@api_view(['GET', 'POST'])
def take_leave_approve_list(request):
    time.sleep(time_sleep)
    try:
        if request.method == 'GET':
            state = request.GET.get('state')
            print(state)
            if state == 'five_day':
                # 取得近五日 is_approved=True 資料(包括今日，所以 days=4)
                five_day_before_today = (datetime.now(desired_timezone) - timedelta(days=4)).replace(hour=0, minute=0, second=0, microsecond=0)
                
                take_leave = TakeLeave.objects.filter(is_approved=True, 
                    approve_date__gte=five_day_before_today).order_by("-approve_date")
            else:
                take_leave = TakeLeave.objects.filter(is_approved=False).order_by("-date")

            serializer = TakeLeaveSerializer(take_leave, many=True)
        elif request.method == 'POST':
            id = request.data.get('id')
            line_id = request.data.get('line_id')
            date = request.data.get('date').split("/")
            is_approved = request.data.get('is_approved')
            take_leave = TakeLeave.objects.filter(id=id).first()
            take_leave.is_approved = is_approved
            if is_approved:
                take_leave.approve_date = timezone.now()
            take_leave.save()
            serializer = TakeLeaveSerializer(take_leave, many=False)

            # 當那天所有的請假都 is_approved = True 才會讓那天 punch 的 is_take_leave_approve = True
            # 因為那天可能會有兩個不同時段請假
            year = int(date[0]); month = int(date[1]); day = int(date[2])
            line_user = LineUser.objects.filter(line_id=line_id).first()
            staff = Staff.objects.filter(line_user=line_user).first()
            take_leave = TakeLeave.objects.filter(staff=staff, date__year=year,
                date__month=month, date__day=day, is_approved=False)
            punch = PunchInorOut.objects.filter(staff=staff, date__year=year,
                    date__month=month, date__day=day).first()
            
            # 有可能事先請假但還沒打卡，要先創建 punch
            # 因為不是用 signal 寫的，直接用admin設定不會創建打卡紀錄
            if not punch:
                PunchInorOut.objects.create(
                    staff=staff,
                    date=datetime(year, month, day),
                    is_take_leave=True
                )
            
            if not take_leave:
                punch.is_take_leave_approve = True
            else:
                punch.is_take_leave_approve = False
            punch.save()
        
        return Response(serializer.data, status=200)
    except:
        return Response('error', status=404)

@api_view(['GET', 'POST'])
def punch_in_or_out_list(request):
    time.sleep(time_sleep)
    try:
        line_id = request.data.get('line_id')
        state = request.data.get('state')
        today = datetime.now(desired_timezone)
        punch_time = request.data.get('punchTime').split(":")
        year = today.year; month = today.month; day = today.day
        hour = int(punch_time[0]); minute = int(punch_time[1]); second = int(punch_time[2])
        
        line_user = LineUser.objects.filter(line_id=line_id).first()
        staff = Staff.objects.filter(line_user=line_user).first()
        punch = PunchInorOut.objects.filter(staff=staff, date__year=year,
            date__month=month, date__day=day).first()
        
        if request.method == 'GET':
            admin = AdminSetting.objects.first()
            serializer = AdminSettingSerializer(admin, many=False)
            serializer2 = PunchInorOutSerializer(punch, many=False)
            return Response({
                "admin_data": serializer.data,
                "punch": serializer2.data
            }, status=200)
        
        elif request.method == 'POST':
            if state == "punch_in":
                if punch:
                    # 如果存在代表有透過請假建立 punch
                    punch.punch_in_time = datetime(year, month, day, hour, minute, second)
                    punch.is_punch_in=True
                    punch.save()
                else:
                    PunchInorOut.objects.create(staff=staff, is_punch_in=True)

            elif state == "punch_out":
                if punch:
                    punch.punch_out_time = datetime(year, month, day, hour, minute, second)
                    punch.is_punch_out = True
                    punch.save()

        return Response('ok', status=200)
    except:
        return Response('error', status=404)
      
@api_view(['GET', 'POST'])
def punch_in_or_out_detail(request, line_id):
    time.sleep(time_sleep)
    try:
        today = datetime.now(desired_timezone)
        year = today.year; month = today.month; day = today.day
        
        line_user = LineUser.objects.filter(line_id=line_id).first()
        staff = Staff.objects.filter(line_user=line_user).first()
        punch = PunchInorOut.objects.filter(staff=staff, date__year=year,
            date__month=month, date__day=day).first()
        
        if request.method == 'GET':
            admin = AdminSetting.objects.first()
            serializer = AdminSettingSerializer(admin, many=False)
            serializer2 = PunchInorOutSerializer(punch, many=False)
            return Response({
                "admin_data": serializer.data,
                "punch": serializer2.data
            }, status=200)
        
        elif request.method == 'POST':
            pass

        return Response('ok', status=200)
    except:
        return Response('error', status=404)
    
@api_view(['GET', 'POST'])
def punch_in_or_out_record_detail(request, line_id, year, month):
    time.sleep(time_sleep)
    try:
        line_user = LineUser.objects.filter(line_id=line_id).first()
        staff = Staff.objects.filter(line_user=line_user).first()
        punch = PunchInorOut.objects.filter(staff=staff, date__year=year,
            date__month=month)
        
        if request.method == 'GET':
            admin = AdminSetting.objects.first()
            serializer = AdminSettingSerializer(admin, many=False)
            serializer2 = PunchInorOutSerializer(punch, many=True)
            return Response({
                "admin_data": serializer.data,
                "punch": serializer2.data
            }, status=200)
        
        elif request.method == 'POST':
            pass

        return Response('ok', status=200)
    except:
        return Response('error', status=404)

# 貨物送達批准
@api_view(['GET', 'PUT'])
def purchase_history_detail(request, state, year, month, day):
    time.sleep(time_sleep)
    try:
        shipping_state = '運送中' if state == 'is_shipping' else '已送達'
        if request.method == 'GET':
            select_year = int(year); select_month = int(month); select_day = int(day)
        
            if select_day == 0:
                order = Order.objects.filter(shipping_state=shipping_state, is_pay=True, 
                    transaction_time__year=select_year, transaction_time__month=select_month).order_by('-id')
            else:
                order = Order.objects.filter(shipping_state=shipping_state, is_pay=True, transaction_time__year=select_year,
                    transaction_time__month=select_month, transaction_time__day=select_day).order_by('-id')
            serializer = OrderSerializer(order, many=True)
            
        if request.method == 'PUT':
            id = request.data.get('id')
            order = Order.objects.filter(id=int(id)).first()
            order.shipping_state = shipping_state
            order.save()
            serializer = OrderSerializer(order, many=False)

        return Response(serializer.data, status=200)
    except:
        return Response('error', status=404)

# 購買紀錄(個人)  
@api_view(['GET'])
def purchase_history_personal_detail(request, line_id, year, month):
    time.sleep(time_sleep)
    try:
        if request.method == 'GET':
            select_year = int(year); select_month = int(month)
            line_user = LineUser.objects.filter(line_id=line_id).first()
            if select_year == 0 and select_month == 0:
                order = Order.objects.filter(line_user=line_user, is_pay=True).order_by('-id')
            else:
                order = Order.objects.filter(line_user=line_user, is_pay=True, created_at__year=select_year,\
                    created_at__month=select_month).order_by('-id')

            serializer = OrderSerializer(order, many=True)
            return Response(serializer.data, status=200)
    except:
        return Response('error', status=404) 

    