from django.urls import path
from rest_framework import routers

from . import views_api

# Namespace for the URLs
app_name = 'accounts_api'

router = routers.DefaultRouter()
router.register(r'users', views_api.CustomUserViewSet)

# Assign the router url to urlpatterns
urlpatterns = router.urls
