import stripe

from django.contrib.postgres.fields import JSONField
from django.db import models

from .. import enums
from ..fields import StripeEnumField, StripeCurrencyCodeField
from .base import StripeModel
from .. import settings as stripe_settings


class Account(StripeModel):
    """
        Stripe documentation: https://stripe.com/docs/api#account
        """

    stripe_class = stripe.Account

    user = models.OneToOneField(
        stripe_settings.get_subscriber_model_string(),
        null=True,
        on_delete=models.SET_NULL,
        related_name="stripe_account",
    )
    business_profile = JSONField(
        null=True, blank=True, help_text="Optional information related to the business."
    )
    business_type = StripeEnumField(
        enum=enums.BusinessType, default="", blank=True, help_text="The business type."
    )
    capabilities = JSONField(
        null=True,
        blank=True,
        help_text="Capabilities that was requested for this account and their associated states"
    )
    charges_enabled = models.BooleanField(
        help_text="Whether the account can create live charges"
    )
    company = JSONField(
        null=True,
        blank=True,
        help_text=(
            "Information about the company or business. "
            "This field is null unless business_type is set to company."
        ),
    )
    country = models.CharField(max_length=2, help_text="The country of the account")
    default_currency = StripeCurrencyCodeField(
        help_text="The currency this account has chosen to use as the default"
    )
    details_submitted = models.BooleanField(
        help_text=(
            "Whether account details have been submitted. "
            "Standard accounts cannot receive payouts before this is true."
        )
    )
    email = models.CharField(
        max_length=255, help_text="The primary user’s email address."
    )
    # TODO external_accounts = ...
    individual = JSONField(
        null=True,
        blank=True,
        help_text=(
            "Information about the person represented by the account. "
            "This field is null unless business_type is set to individual."
        ),
    )
    payouts_enabled = models.BooleanField(
        help_text="Whether Stripe can send payouts to this account"
    )
    requirements = JSONField(
        null=True,
        blank=True,
        help_text="Information about the requirements for the account, "
                  "including what information needs to be collected, and by when.",
    )
    settings = JSONField(
        null=True,
        blank=True,
        help_text=(
            "Account options for customizing how the account functions within Stripe."
        ),
    )
    tos_acceptance = JSONField(
        null=True,
        blank=True,
        help_text="Details on the acceptance of the Stripe Services Agreement",
    )
    type = StripeEnumField(enum=enums.AccountType, help_text="The Stripe account type.")

    def __str__(self):
        return "{} - {}".format(self.email or "", self.stripe_id)

    def __repr__(self):
        return "Account(pk={!r}, email={!r}, type={!r}, stripe_id={!r})".format(
            self.pk,
            self.email or "",
            self.type,
            self.stripe_id,
        )

    @classmethod
    def get_or_create_account_in_stripe(cls, user, livemode=stripe_settings.STRIPE_LIVE_MODE, **account_data):
        """
        Get or create a stripe connect account.

        :param user: The user model instance for which to get or
            create a connect account.
        :type user: User

        :param livemode: Whether to get the user in live or test mode.
        :type livemode: bool
        """

        try:
            return Account.objects.get(user=user), False
        except Account.DoesNotExist:
            action = f'create:{user.pk}'
            idempotency_key = stripe_settings.get_idempotency_key(
                "account", action, livemode
            )
            return cls.create(user, idempotency_key=idempotency_key, **account_data), True

    @classmethod
    def create(cls, user, idempotency_key=None, **account_data, ):
        metadata = {}
        user_key = stripe_settings.SUBSCRIBER_CUSTOMER_KEY
        if user_key not in ("", None):
            metadata[user_key] = user.pk

        stripe_account = cls._api_create(
            idempotency_key=idempotency_key, metadata=metadata, **account_data
        )
        return cls._stripe_object_to_record(stripe_account)
