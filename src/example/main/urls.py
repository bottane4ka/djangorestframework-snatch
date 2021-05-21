from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("rest/", include("rest.manager.urls")),
    path("admin/", admin.site.urls)
]
