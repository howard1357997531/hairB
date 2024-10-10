from django.contrib import admin
from .models import *

@admin.register(LineUser)
class LineUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'line_id', 'display_name', 'picture_url', 'is_admin', 'is_staff',
        'become_admin_time', 'become_staff_time', 'created_at')

@admin.register(AdminSetting)
class AdminSettingAdmin(admin.ModelAdmin):
    list_display = ('id', 'company_name', 'company_phone', 'company_address', 'latitude', 'longitude',
        'work_time', 'break_time', 'can_reservation_time', 'can_reservation_period', 'rest_day_for_week', 
        'rest_day_for_day', 'today_reservation_limit', 'created_at')

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('id', 'line_user', 'is_delete', 'created_at')

@admin.register(StaffSchedule)
class StaffScheduleAdmin(admin.ModelAdmin):
    list_display = ('id', 'staff', 'date', 'fix_time', 'fix_time_delete', 'fix_time_cancel',
        'flex_time', 'common_setting_id', 'is_full', 'created_at')
    
@admin.register(StaffCommonSetting)
class StaffCommonSettingAdmin(admin.ModelAdmin):
    list_display = ('id', 'staff', 'name', 'fix_time', 'fix_time_delete', 'fix_time_cancel',
        'flex_time', 'created_at')
    
@admin.register(TakeLeave)
class TakeLeave(admin.ModelAdmin):
    list_display = ('id', 'staff', 'date', 'approve_date', 'start_hour', 'start_minute', 'end_hour', 'end_minute',
        'total_hour', 'total_minute', 'category', 'is_approved')

@admin.register(PunchInorOut)
class PunchInorOutSettingAdmin(admin.ModelAdmin):
    list_display = ('id', 'staff', 'date', 'punch_in_time', 'punch_out_time', 
        'is_punch_in', 'is_punch_out', 'is_take_leave', 'is_take_leave_approve')
    
