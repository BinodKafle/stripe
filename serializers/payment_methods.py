from rest_framework import serializers, status

from ..utils import CustomValidation
from ..models import Card, Account, Customer


class CardPaymentMethodReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = "__all__"


class CardPaymentMethodsWriteSerializer(serializers.ModelSerializer):
    last4 = serializers.CharField(read_only=True)
    brand = serializers.CharField(read_only=True)

    class Meta:
        model = Card
        fields = ["stripe_id", "last4", "brand"]

    def create(self, validated_data):
        try:
            user = self.context['request'].user
            card, card_does_not_exist = Card.get_card_detail_from_token(validated_data['stripe_id'])

            customer, customer_does_not_exist = Customer.get_or_create_customer_in_stripe(user=user)

            account, account_does_not_exist = Account.get_or_create_account_in_stripe(user,
                                                                                      type='custom',
                                                                                      country='US',
                                                                                      requested_capabilities=[
                                                                                          "transfers"],
                                                                                      business_type="individual",
                                                                                      )
            if customer_does_not_exist:
                customer = Customer.objects.create(user=user, **customer)
                customer.add_card(validated_data['stripe_id'])

            if card_does_not_exist:
                Card.objects.create(customer=customer, **card)
                if not customer_does_not_exist:
                    customer.add_card(validated_data['stripe_id'])

            if account_does_not_exist:
                Account.objects.create(user=user, **account)
            return card
        except Exception as e:
            raise CustomValidation(str(e), 'error', status_code=status.HTTP_400_BAD_REQUEST)
