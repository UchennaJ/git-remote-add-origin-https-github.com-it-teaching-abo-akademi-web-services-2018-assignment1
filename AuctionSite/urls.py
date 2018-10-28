"""AuctionSite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import path, re_path
from django.conf.urls import *
from yaasApp.views import *
from yaasApp.restframework_api import *
from django.contrib.auth.views import LoginView, LogoutView
from rest_framework.urlpatterns import format_suffix_patterns


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


# RESTful API URLs
urlpatterns = [
    path('YAAS/api/auctions/', api_list_auctions),
    re_path(r'^YAAS/api/auctions/(?P<id>\d+)/$', api_auction),
    re_path(r'^YAAS/api/auctions/(?P<id>\d+)/bid/$', api_bid),
    re_path(r'^YAAS/api/auctions/search/(?P<criteria>(\w\s*)+)/$', api_search_auctions)
]



urlpatterns = [
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]


urlpatterns = [
    path('admin/', admin.site.urls),
    path('YAAS/', home),
    path('YAAS/auction/create/', create_auction),
    path('YAAS/auction/create/confirmation/', confirmation),
    path('YAAS/auction/search/', search),
    path('YAAS/language/<slug:lang_code>/', change_language),
    re_path(r'^YAAS/auction/(?P<id>\d+)/$', view_auction),
    re_path(r'^YAAS/auction/(?P<id>\d+)/edit/$', edit_auction),
    re_path(r'^YAAS/auction/(?P<id>\d+)/bid/$', bid_auction),
    re_path(r'^YAAS/auction/(?P<id>\d+)/ban/$', ban_auction),
    path('YAAS/user/register/', register_user),
    path('YAAS/user/', edit_user),
    path('YAAS/login/', LoginUser.as_view(), name="login"),
    path('YAAS/logout/', logout_view, name="logout"),
    path('YAAS/email/', email_view, name="email"),


    # Comment the line below to disable database fixture
    path('AuctionSite/generatedata/', generatedata),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #url(r'^admin/', include(admin.site.urls)),


    # Django currency url
    #url(r'^currency/', include('django_easy_currencies.urls')),
]

