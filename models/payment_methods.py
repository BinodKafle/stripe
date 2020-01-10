import stripe
from django.db import models

from .. import enums
from ..fields import StripeEnumField
from .base import StripeModel


class Card(StripeModel):

    stripe_class = stripe.Card

    address_city = models.TextField(
        max_length=5000,
        blank=True,
        default="",
        help_text="City/District/Suburb/Town/Village.",
    )
    address_country = models.TextField(
        max_length=5000, blank=True, default="", help_text="Billing address country."
    )
    address_line1 = models.TextField(
        max_length=5000,
        blank=True,
        default="",
        help_text="Street address/PO Box/Company name.",
    )
    address_line1_check = StripeEnumField(
        enum=enums.CardCheckResult,
        blank=True,
        default="",
        help_text="If `address_line1` was provided, results of the check.",
    )
    address_line2 = models.TextField(
        max_length=5000,
        blank=True,
        default="",
        help_text="Apartment/Suite/Unit/Building.",
    )
    address_state = models.TextField(
        max_length=5000,
        blank=True,
        default="",
        help_text="State/County/Province/Region.",
    )
    address_zip = models.TextField(
        max_length=5000, blank=True, default="", help_text="ZIP or postal code."
    )
    address_zip_check = StripeEnumField(
        enum=enums.CardCheckResult,
        blank=True,
        default="",
        help_text="If `address_zip` was provided, results of the check.",
    )
    brand = StripeEnumField(enum=enums.CardBrand, help_text="Card brand.")
    country = models.CharField(
        max_length=2,
        default="",
        blank=True,
        help_text="Two-letter ISO code representing the country of the card.",
    )
    customer = models.ForeignKey(
        "Customer", on_delete=models.SET_NULL, null=True, related_name="legacy_cards"
    )
    cvc_check = StripeEnumField(
        enum=enums.CardCheckResult,
        default="",
        blank=True,
        help_text="If a CVC was provided, results of the check.",
    )
    dynamic_last4 = models.CharField(
        max_length=4,
        default="",
        blank=True,
        help_text="(For tokenized numbers only.) The last four digits of the device "
                  "account number.",
    )
    exp_month = models.IntegerField(help_text="Card expiration month.")
    exp_year = models.IntegerField(help_text="Card expiration year.")
    fingerprint = models.CharField(
        default="",
        blank=True,
        max_length=16,
        help_text="Uniquely identifies this particular card number.",
    )
    funding = StripeEnumField(
        enum=enums.CardFundingType, help_text="Card funding type."
    )
    last4 = models.CharField(max_length=4, help_text="Last four digits of Card number.")
    name = models.TextField(
        max_length=5000, default="", blank=True, help_text="Cardholder name."
    )
    tokenization_method = StripeEnumField(
        enum=enums.CardTokenizationMethod,
        default="",
        blank=True,
        help_text="If the card number is tokenized, this is the method that was used.",
    )

    def __repr__(self):
        return "Card(pk={!r}, customer={!r})".format(
            self.pk,
            getattr(self, "customer", None),
        )

    @classmethod
    def get_card_detail_from_token(cls, card_token):
        card = cls.api_retrieve_card_from_token(card_token)
        exists = Card.objects.filter(fingerprint=card['fingerprint'])
        if exists:
            return exists.first(), False
        return card, True
