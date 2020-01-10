import logging
import uuid
from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import JSONField

from ..fields import StripeDateTimeField
from .. import settings as stripe_settings

logger = logging.getLogger(__name__)


class StripeModel(models.Model):

    stripe_class = None
    expand_fields = []

    stripe_id = models.CharField(max_length=255, blank=False, unique=True)
    created = StripeDateTimeField(
        null=True,
        blank=True,
        help_text="The datetime this object was created in stripe.",
    )
    livemode = models.NullBooleanField(
        default=None,
        null=True,
        blank=True,
        help_text="Null here indicates that the livemode status is unknown or was "
                  "previously unrecorded. Otherwise, this field indicates whether this record "
                  "comes from Stripe test mode or live mode operation.",
    )
    metadata = JSONField(
        null=True,
        blank=True,
        help_text="A set of key/value pairs that you can attach to an object. "
                  "It can be useful for storing additional information about an object in "
                  "a structured format.",
    )
    description = models.TextField(
        null=True, blank=True, help_text="A description of this object."
    )

    class Meta:
        abstract = True

    @property
    def default_api_key(self):
        return stripe_settings.get_default_api_key()

    @classmethod
    def api_retrieve_card_from_token(cls, token_id, api_key=stripe_settings.STRIPE_SECRET_KEY):
        import stripe
        card_data = stripe.Token.retrieve(token_id, api_key=api_key)['card']
        return cls._stripe_object_to_record(card_data)

    @classmethod
    def _api_create(cls, api_key=stripe_settings.STRIPE_SECRET_KEY, **kwargs):
        """
        Call the stripe API's create operation for this model.

        :param api_key: The api key to use for this request. \
            Defaults to stripe_settings.STRIPE_SECRET_KEY.
        :type api_key: string
        """

        return cls.stripe_class.create(api_key=api_key, **kwargs)

    def api_retrieve(self, api_key=None):
        """
        Call the stripe API's retrieve operation for this model.

        :param api_key: The api key to use for this request. \
            Defaults to settings.STRIPE_SECRET_KEY.
        :type api_key: string
        """
        api_key = api_key or self.default_api_key

        return self.stripe_class.retrieve(
            id=self.stripe_id, api_key=api_key, expand=self.expand_fields
        )

    @classmethod
    def _id_from_data(cls, data):
        """
        Extract stripe id from stripe field data
        :param data:
        :return:
        """

        if isinstance(data, str):
            # data like "sub_6lsC8pt7IcFpjA"
            id_ = data
        elif data:
            # data like {"id": sub_6lsC8pt7IcFpjA", ...}
            id_ = data.get("id")
        else:
            id_ = None

        return id_

    @classmethod
    def is_valid_object(cls, data):
        """
        Returns whether the data is a valid object for the class
        """
        return data["object"] == cls.stripe_class.OBJECT_NAME

    @classmethod
    def _manipulate_stripe_object_hook(cls, data):
        """
        Gets called by this object's stripe object conversion method just before
        conversion.
        Use this to populate custom fields in a StripeModel from stripe data.
        """
        if data.get('id', None):
            data['stripe_id'] = data['id']
            del data['id']
        return data

    @classmethod
    def _stripe_object_to_record(cls, data):
        """
        This takes an object, as it is formatted in Stripe's current API for our object
        type. In return, it provides a dict. The dict can be used to create a record or
        to update a record

        This function takes care of mapping from one field name to another, converting
        from cents to dollars, converting timestamps, and eliminating unused fields
        (so that an objects.create() call would not fail).

        :param data: the object, as sent by Stripe. Parsed from JSON, into a dict
        :type data: dict

        :return: All the members from the input, translated, mutated, etc
        :rtype: dict
        """

        manipulated_data = cls._manipulate_stripe_object_hook(data)

        if "object" not in data:
            raise ValueError("Stripe data has no `object` value. Aborting. %r" % data)

        if not cls.is_valid_object(data):
            raise ValueError(
                "Trying to fit a %r into %r. Aborting." % (data["object"], cls.__name__)
            )

        result = {}

        # Iterate over all the fields that we know are related to Stripe,
        # let each field work its own magic
        ignore_fields = ["id", "date_purged"]  # XXX: Customer hack
        for field in cls._meta.fields:
            if field.name in ignore_fields:
                continue

            if isinstance(field, models.ForeignKey):
                continue

            if hasattr(field, "stripe_to_db"):
                field_data = field.stripe_to_db(manipulated_data)
            else:
                field_data = manipulated_data.get(field.name)

            if (
                    isinstance(field, (models.CharField, models.TextField))
                    and field_data is None
            ):
                # TODO - this applies to StripeEnumField as well, since it
                #  sub-classes CharField, is that intentional?
                field_data = ""

            result[field.name] = field_data

        return result


class IdempotencyKey(models.Model):
    uuid = models.UUIDField(
        max_length=36, primary_key=True, editable=False, default=uuid.uuid4
    )
    action = models.CharField(max_length=100)
    livemode = models.BooleanField(
        help_text="Whether the key was used in live or test mode."
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("action", "livemode")

    def __str__(self):
        return str(self.uuid)

    @property
    def is_expired(self):
        """
        :rtype: bool
        """
        return timezone.now() > self.created + timedelta(hours=24)
