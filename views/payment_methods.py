from rest_framework import viewsets

from ..serializers import CardPaymentMethodReadSerializer, CardPaymentMethodsWriteSerializer
from ..models import Card


class PaymentMethodsViewSet(viewsets.ModelViewSet):
    serializer_class = CardPaymentMethodsWriteSerializer

    def get_queryset(self):
        return Card.objects.filter(customer=self.request.user.stripe_customer)

    def get_serializer_class(self):
        if self.action == 'create':
            return CardPaymentMethodsWriteSerializer
        if self.action in ['retrieve', 'list']:
            return CardPaymentMethodReadSerializer
