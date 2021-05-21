from django.conf.urls import url, include

from rest.manager import views
from rest.brave_rest_framework.routers import CustomRouter

router = CustomRouter()
router.register_all(views)
urlpatterns = [url(r"^", include(router.urls))]
