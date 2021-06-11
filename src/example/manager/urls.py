from django.conf.urls import url, include

from manager import views
from snatch.routers import SnatchRouter

router = SnatchRouter()
router.register_all(views)
urlpatterns = [url(r"^", include(router.urls))]
