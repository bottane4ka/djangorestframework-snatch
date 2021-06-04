from django.conf.urls import url, include

from manager import views
from snatch.routers import CustomRouter

router = CustomRouter()
router.register_all(views)
urlpatterns = [url(r"^", include(router.urls))]
