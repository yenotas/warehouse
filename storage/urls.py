from rest_framework.routers import DefaultRouter
from .views import PivotTableViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'complex-table', PivotTableViewSet, basename='complex-table')

urlpatterns = [
    path('', include(router.urls)),  # Подключение маршрутов ViewSet
]
