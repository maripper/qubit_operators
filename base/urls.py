"""qubit_operators URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path
import base.views as views
urlpatterns = [
    path('compare/', views.compare,name='compare'),
    path('restart/', views.restart,name='restart'),
    path('receiver/', views.receiver,name='receiver'),
    path('sender/', views.sender,name='sender'),
    path('encrypt/', views.encrypt,name='encrypt'),
    path('coding_decoding/', views.coding_decoding,name='coding_decoding'),
    path('decrypt/', views.decrypt,name='decrypt'),
    path('safe_poc/', views.safe_poc,name='safe_poc'),
    path('factors/', views.factors,name='factors'),
    path('eve_poc/', views.eve_poc,name='eve_poc')


]
