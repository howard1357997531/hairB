from rest_framework.serializers import ModelSerializer
from line.serializers import ReservationSerializer
from .models import *

class LineUserSerializer(ModelSerializer):
    class Meta:
        model = LineUser
        fields = ('id', 'line_id', 'display_name', 'picture_url', 'is_admin', 'is_staff', 
                  'become_admin_time', 'become_staff_time', 'created_at')

class AdminSettingSerializer(ModelSerializer):
    class Meta:
        model =  AdminSetting
        fields = ('id', 'company_name', 'company_phone', 'company_address', 'latitude', 'longitude',
        'work_time', 'break_time', 'can_reservation_time', 'can_reservation_period', 'rest_day_for_week', 
        'rest_day_for_day', 'today_reservation_limit', 'created_at')
        # fields = '__all__'

class StaffScheduleSerializer(ModelSerializer):
    # read_only 代只能看，不能做修改(在 views.py 使用 serilaizer.save() 時，data裡面沒有此資訊不會跑error)
    reservation = ReservationSerializer(many=True, required=False, read_only=True)
    class Meta:
        model = StaffSchedule
        fields = ('id', 'staff', 'date', 'fix_time', 'fix_time_delete', 'fix_time_cancel',
            'flex_time', 'common_setting_id', 'is_full', 'created_at', 'reservation')

class StaffCommonSettingSerializer(ModelSerializer):
    class Meta:
        model = StaffCommonSetting
        fields = ('id', 'staff', 'name', 'fix_time', 'fix_time_delete', 'fix_time_cancel',
                   'flex_time', 'created_at')

class StaffSerializer(ModelSerializer):
    # 與 lineUser 設置 OneToOneField 情況下可以這樣取得他的資訊
    # source="line_user" 不能跟前面變數一樣，會 error
    lineUser = LineUserSerializer(source="line_user", read_only=True)
    staffSchedule = StaffScheduleSerializer(many=True, required=False)
    staffCommonSetting = StaffCommonSettingSerializer(many=True, required=False)
    
    class Meta:
        model = Staff
        fields = ('id', 'is_delete', 'created_at', 'lineUser', 'staffSchedule', 'staffCommonSetting')

    # 也可以這樣新增
    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     data['user'] = LineUserSerializer(instance.user_id).data
    #     return data

class TakeLeaveStaffSerializer(ModelSerializer):
    lineUser = LineUserSerializer(source="line_user", read_only=True)
    
    class Meta:
        model = Staff
        fields = ('id', 'lineUser')

class TakeLeaveSerializer(ModelSerializer):
    staff = TakeLeaveStaffSerializer(required=True)
    class Meta:
        model = TakeLeave
        fields = ('id', 'staff', 'date', 'start_hour', 'start_minute', 'end_hour', 'end_minute',
                  'total_hour', 'total_minute', 'category', 'remark', 'is_approved')
        
class PunchInorOutSerializer(ModelSerializer):

    class Meta:
        model = PunchInorOut
        fields = ('id', 'staff', 'date', 'punch_in_time', 'punch_out_time', 
            'is_punch_in', 'is_punch_out', 'is_take_leave', 'is_take_leave_approve')

