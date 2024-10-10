"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from mainapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('mainapp.urls')),
    path('line/', include('line.urls')),

    path('', views.index, name='index'),
    path('admin-setting/', views.index, name='index'),
    path('staff/', views.index, name='index'),
    path('product/', views.index, name='index'),
    path('order-shipping-approve/', views.index, name='index'),
    path('take-leave-approve/', views.index, name='index'),
    path('admin-setting/', views.index, name='index'),
    path('punch-in-or-out/', views.index, name='index'),
    path('schedule-detail/', views.index, name='index'),
    path('schedule/', views.index, name='index'),
    path('take-leave/', views.index, name='index'),
    path('purchase-history/', views.index, name='index'),
]
