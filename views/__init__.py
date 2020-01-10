from rest_framework.routers import DefaultRouter

router = DefaultRouter()

from .payment_methods import PaymentMethodsViewSet