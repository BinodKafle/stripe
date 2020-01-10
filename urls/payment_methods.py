from rest_framework.routers import DefaultRouter

from ..views import PaymentMethodsViewSet

router = DefaultRouter()
router.register(r'payment-methods', PaymentMethodsViewSet, basename='payment_methods')

urlpatterns = router.urls
