import stripe

from django.contrib.postgres.fields import JSONField
from django.db import models

from .. import settings as stripe_settings
from .. import enums
from ..fields import (
    StripeCurrencyCodeField,
    StripeEnumField,
)
from .base import StripeModel


class Customer(StripeModel):
    """
       Customer objects allow you to perform recurring charges and track multiple
       charges that are associated with the same customer.

       Stripe documentation: https://stripe.com/docs/api/python#customers
       """

    stripe_class = stripe.Customer
    expand_fields = ["default_source"]

    address = JSONField(null=True, blank=True, help_text="The customer's address.")
    balance = models.IntegerField(
        help_text=(
            "Current balance, if any, being stored on the customer's account. "
            "If negative, the customer has credit to apply to the next invoice. "
            "If positive, the customer has an amount owed that will be added to the "
            "next invoice. The balance does not refer to any unpaid invoices; it "
            "solely takes into account amounts that have yet to be successfully "
            "applied to any invoice. This balance is only taken into account for "
            "recurring billing purposes (i.e., subscriptions, invoices, invoice items)."
        )
    )
    currency = StripeCurrencyCodeField(
        default="",
        help_text="The currency the customer can be charged in for "
                  "recurring billing purposes",
    )
    default_source = models.CharField(max_length=12, null=True, blank=True)
    delinquent = models.BooleanField(
        help_text="Whether or not the latest charge for the customer's "
                  "latest invoice has failed."
    )
    discount = JSONField(
        null=True,
        blank=True,
        help_text="current discount active on the customer, if there is one"
    )
    email = models.TextField(max_length=5000, default="", blank=True)
    invoice_prefix = models.CharField(
        default="",
        blank=True,
        max_length=255,
        help_text=(
            "The prefix for the customer used to generate unique invoice numbers."
        ),
    )
    invoice_settings = JSONField(
        null=True, blank=True, help_text="The customer's default invoice settings."
    )
    name = models.TextField(
        max_length=5000,
        default="",
        blank=True,
        help_text="The customer's full name or business name.",
    )
    phone = models.TextField(
        max_length=5000,
        default="",
        blank=True,
        help_text="The customer's phone number.",
    )
    preferred_locales = JSONField(
        null=True,
        blank=True,
        help_text=(
            "The customer's preferred locales (languages), ordered by preference."
        ),
    )
    shipping = JSONField(
        null=True,
        blank=True,
        help_text="Shipping information associated with the customer.",
    )
    tax_exempt = StripeEnumField(
        enum=enums.CustomerTaxExempt,
        default="",
        help_text="Describes the customer's tax exemption status. When set to reverse, "
                  'invoice and receipt PDFs include the text "Reverse charge".',
    )
    user = models.OneToOneField(
        stripe_settings.get_subscriber_model_string(),
        null=True,
        on_delete=models.SET_NULL,
        related_name="stripe_customer",
    )

    date_purged = models.DateTimeField(null=True, editable=False)

    class Meta:
        unique_together = ("user", "livemode")

    def __str__(self):
        if not self.user:
            return "{id} (deleted)".format(id=self.id)
        elif self.user:
            return self.phone
        else:
            return self.id

    @classmethod
    def get_or_create_customer_in_stripe(cls, user, livemode=stripe_settings.STRIPE_LIVE_MODE):
        """
        Get or create a stripe customer.

        :param user: The user model instance for which to get or
            create a customer.
        :type user: User

        :param livemode: Whether to get the user in live or test mode.
        :type livemode: bool
        """

        try:
            return Customer.objects.get(user=user, livemode=livemode), False
        except Customer.DoesNotExist:
            action = f'create : {user.pk}'
            idempotency_key = stripe_settings.get_idempotency_key(
                "customer", action, livemode
            )
            return cls.create(user, idempotency_key=idempotency_key), True

    @classmethod
    def create(cls, user, idempotency_key=None):
        metadata = {}
        user_key = stripe_settings.SUBSCRIBER_CUSTOMER_KEY
        if user_key not in ("", None):
            metadata[user_key] = user.pk

        stripe_customer = cls._api_create(
            phone=user.phone_number,
            description=f'Customer for {user.phone_number}',
            idempotency_key=idempotency_key,
            metadata=metadata
        )
        return cls._stripe_object_to_record(stripe_customer)

    def add_card(self, source):
        """
        Adds a card to this customer's account.

        :param source: Either a token, like the ones returned by our Stripe.js, or a
            dictionary containing a user's credit card details.
            Stripe will automatically validate the card.
        :type source: string, dict
        """

        stripe_customer = self.api_retrieve()
        return stripe_customer.sources.create(source=source)
