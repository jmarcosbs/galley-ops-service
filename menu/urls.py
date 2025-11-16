from django.urls import path

from .views import MenuViewSet

urlpatterns = [
    path("menu/", MenuViewSet.as_view(), name="menu"),
]
