from django.db import models
from django.utils import timezone
from datetime import datetime

class Common(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class LineUser(Common):
    line_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    display_name = models.CharField(max_length=255, null=True, blank=True)
    picture_url = models.CharField(max_length=255, null=True, blank=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    become_admin_time = models.DateTimeField(default=timezone.now)
    become_staff_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.display_name
    
class AdminSetting(Common):
    company_name = models.CharField(max_length=255, null=True, blank=True)
    company_phone = models.CharField(max_length=255, null=True, blank=True)
    company_address = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.FloatField(default=0)
    longitude = models.FloatField(default=0)
    work_time = models.CharField(max_length=255, null=True, blank=True)
    break_time = models.CharField(max_length=255, null=True, blank=True)
    can_reservation_time = models.CharField(max_length=255, null=True, blank=True)
    can_reservation_period = models.PositiveIntegerField(default=0)
    rest_day_for_week = models.CharField(max_length=255, null=True, blank=True)
    rest_day_for_day = models.CharField(max_length=255, null=True, blank=True)
    today_reservation_limit = models.PositiveIntegerField(default=0)

    def __str__(self):
        return str(self.id)

class Staff(Common):
    line_user = models.OneToOneField(LineUser, on_delete=models.CASCADE, null=True, blank=True)
    # '開始小時,開始分鐘,區間小時,區間分鐘'
    is_delete = models.BooleanField(default=False)

    def __str__(self):
        return str(self.line_user.display_name)

# common_settind_id 預設0為'不設定'
class StaffSchedule(Common):
    staff = models.ForeignKey(Staff, related_name='staffSchedule', on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)
    fix_time = models.CharField(max_length=255, null=True, blank=True)
    fix_time_delete = models.CharField(max_length=255, null=True, blank=True)
    fix_time_cancel = models.BooleanField(default=False)
    flex_time = models.CharField(max_length=255, null=True, blank=True)
    common_setting_id = models.PositiveIntegerField(default=0)
    is_full = models.BooleanField(default=False)

    def __str__(self):
        date = timezone.localtime(self.date).strftime('%Y/%m/%d')
        return f'{self.staff.line_user.display_name} {date}'

class StaffCommonSetting(Common):
    staff = models.ForeignKey(Staff, related_name='staffCommonSetting',on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    fix_time = models.CharField(max_length=255, null=True, blank=True)
    fix_time_delete = models.CharField(max_length=255, null=True, blank=True)
    fix_time_cancel = models.BooleanField(default=False)
    flex_time = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return str(self.id)

class TakeLeave(Common):
    staff = models.ForeignKey(Staff, related_name='takeLeave', on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateTimeField()
    start_hour = models.CharField(max_length=255, null=True, blank=True)
    start_minute = models.CharField(max_length=255, null=True, blank=True)
    end_hour = models.CharField(max_length=255, null=True, blank=True)
    end_minute = models.CharField(max_length=255, null=True, blank=True)
    total_hour = models.CharField(max_length=255, null=True, blank=True)
    total_minute = models.CharField(max_length=255, null=True, blank=True)
    category = models.CharField(max_length=255, null=True, blank=True)
    remark = models.TextField(null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    approve_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        date = timezone.localtime(self.date).strftime('%Y/%m/%d')
        time = f'{self.start_hour}:{self.start_minute}~{self.end_hour}:{self.end_minute} '
        return f'{self.staff.line_user.display_name} {date} {time}'
    
class PunchInorOut(Common):
    staff = models.ForeignKey(Staff, related_name='punchInorOut', on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)
    punch_in_time = models.DateTimeField(default=timezone.now)
    punch_out_time = models.DateTimeField(default=timezone.now)
    is_punch_in = models.BooleanField(default=False)
    is_punch_out = models.BooleanField(default=False)
    is_take_leave = models.BooleanField(default=False)
    is_take_leave_approve = models.BooleanField(default=False)

    def __str__(self):
        date = timezone.localtime(self.date).strftime('%Y/%m/%d')
        return f'{self.staff.line_user.display_name} {date}'