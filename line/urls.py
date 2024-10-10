from django.urls import path
from . import views
from . import cart

urlpatterns = [
    path('callback', views.callback, name='callback'),
    path('line_pay_confirm/', cart.line_pay_confirm, name='confirm'),
]