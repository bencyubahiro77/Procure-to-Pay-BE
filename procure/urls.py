from rest_framework.routers import DefaultRouter
from procure.views import PurchaseRequestViewSet
from django.urls import path

router = DefaultRouter()
router.register('requests', PurchaseRequestViewSet, basename='requests')

urlpatterns = router.urls
