from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("api/", include("manager.urls")),
    path(r"admin/", admin.site.urls)
]
