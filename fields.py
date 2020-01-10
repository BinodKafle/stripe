from django.db import models

from .utils import convert_tstamp


class StripeEnumField(models.CharField):
    def __init__(self, enum, *args, **kwargs):
        self.enum = enum
        choices = enum.choices
        defaults = {"choices": choices, "max_length": max(len(k) for k, v in choices)}
        defaults.update(kwargs)
        super().__init__(*args, **defaults)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["enum"] = self.enum
        del kwargs["choices"]
        return name, path, args, kwargs


class StripeCurrencyCodeField(models.CharField):
    """
    A field used to store a three-letter currency code (eg. usd, eur, ...)
    """

    def __init__(self, *args, **kwargs):
        defaults = {"max_length": 3, "help_text": "Three-letter ISO currency code"}
        defaults.update(kwargs)
        super().__init__(*args, **defaults)


class StripeDateTimeField(models.DateTimeField):
    """A field used to define a DateTimeField value according to stripe logic."""

    def stripe_to_db(self, data):
        """Convert the raw timestamp value to a DateTime representation."""
        val = data.get(self.name)

        # Note: 0 is a possible return value, which is 'falseish'
        if val is not None:
            return convert_tstamp(val)
