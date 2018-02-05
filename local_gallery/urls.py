"""local_gallery URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from rest_framework.urlpatterns import format_suffix_patterns

from archive_manager import views

urlpatterns = [
    path('', views.home, name="home"),
    path('admin/', admin.site.urls),
    path('post/new/', views.post_new, name='post_new'),
    path('add-location/', views.create_location, name="create_location"),

    path('<slug:slug>/image/new/', views.PhotoCreateView.as_view(), name='post_new_image'),
    path('<slug:slug>/<int:pk>/', views.LocationDetailView.as_view(), name='location'),
]

# REST API urls:
urlpatterns += [
    path('api/<int:pj_id>/locations/', views.LocationList.as_view()),
    path('api/<int:pj_id>/locations/<int:pk>/', views.LocationDetail.as_view()),
    path('api/<int:pj_id>/locations/<int:pk>/photos/', views.LocationPhotoList.as_view()),
    path('api/<int:pj_id>/photos/', views.PhotoList.as_view()),
    path('api/<int:pj_id>/photos/<int:pk>/', views.PhotoDetail.as_view()),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

urlpatterns = format_suffix_patterns(urlpatterns)
