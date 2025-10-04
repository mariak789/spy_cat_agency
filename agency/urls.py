from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SpyCatViewSet, MissionViewSet, TargetViewSet

router = DefaultRouter()
router.register(r"cats", SpyCatViewSet, basename="cats")
router.register(r"missions", MissionViewSet, basename="missions")
router.register(r"targets", TargetViewSet, basename="targets")

urlpatterns = [path("", include(router.urls))]