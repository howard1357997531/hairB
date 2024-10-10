from django.urls import path
from . import views

urlpatterns = [
    path('get_lineUser_data/', views.get_lineUser_data, name='get_lineUser_data'),
    path('lineUser_list/', views.lineUser_list, name='lineUser_list'),
    path('admin_list/', views.admin_list, name='admin_list'),
    path('staff_list/', views.staff_list, name='staff_list'),
    path('product_list/', views.product_list, name='product_list'),
    path('product_detail/<int:id>/', views.product_detail, name='product_detail'),
    path('admin_setting_list/', views.admin_setting_list, name='admin_setting_list'),
    path('schedule_list/', views.schedule_list, name='schedule_list'),
    path('schedule_detail/<str:line_id>/<int:year>/<int:month>/<int:day>/', views.schedule_detail, name='schedule_detail'),
    path('schedule_delete/<int:id>/', views.schedule_delete, name='schedule_delete'),
    path('common_setting_list/', views.common_setting_list, name='common_setting_list'),
    path('take_leave_list/', views.take_leave_list, name='take_leave_list'),
    path('take_leave_detail/<str:line_id>/<str:date>/', views.take_leave_detail, name='take_leave_detail'),
    path('take_leave_delete/<int:id>/', views.take_leave_delete, name='take_leave_delete'),
    path('take_leave_approve_list/', views.take_leave_approve_list, name='take_leave_approve_list'),
    path('punch_in_or_out_list/',views.punch_in_or_out_list, name='punch_in_or_out_list'),
    path('punch_in_or_out_detail/<str:line_id>/',views.punch_in_or_out_detail, name='punch_in_or_out_detail'),
    path('punch_in_or_out_record_detail/<str:line_id>/<int:year>/<int:month>/',views.punch_in_or_out_record_detail, name='punch_in_or_out_record_detail'),
    path('purchase_history_detail/<str:state>/<str:year>/<str:month>/<str:day>/', \
          views.purchase_history_detail, name='purchase_history_detail'),
    path('purchase_history_personal_detail/<str:line_id>/<str:year>/<str:month>/', \
          views.purchase_history_personal_detail, name='purchase_history_personal_detail'),
    ]