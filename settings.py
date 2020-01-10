import stripe

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from .checks import validate_stripe_api_version

DEFAULT_STRIPE_API_VERSION = "2019-09-09"


def get_callback_function(setting_name, default=None):
    """
    Resolve a callback function based on a setting name.

    If the setting value isn't set, default is returned.  If the setting value
    is already a callable function, that value is used - If the setting value
    is a string, an attempt is made to import it.  Anything else will result in
    a failed import causing ImportError to be raised.

    :param setting_name: The name of the setting to resolve a callback from.
    :type setting_name: string (``str``/``unicode``)
    :param default: The default to return if setting isn't populated.
    :type default: ``bool``
    :returns: The resolved callback function (if any).
    :type: ``callable``
    """
    func = getattr(settings, setting_name, None)
    if not func:
        return default

    if callable(func):
        return func

    if isinstance(func, str):
        func = import_string(func)

    if not callable(func):
        raise ImproperlyConfigured(f"{setting_name} must be callable.")

    return func


def _get_idempotency_key(object_type, action, livemode):
    from .models import IdempotencyKey

    action = f"{object_type}:{action}"
    idempotency_key, _created = IdempotencyKey.objects.get_or_create(
        action=action, livemode=livemode
    )
    return str(idempotency_key.uuid)


get_idempotency_key = get_callback_function(
    "STRIPE_IDEMPOTENCY_KEY_CALLBACK", _get_idempotency_key
)

SUBSCRIBER_CUSTOMER_KEY = getattr(
    settings, "STRIPE_SUBSCRIBER_CUSTOMER_KEY", "stripe_subscriber"
)

TEST_API_KEY = getattr(settings, "STRIPE_TEST_SECRET_KEY", "")
LIVE_API_KEY = getattr(settings, "STRIPE_LIVE_SECRET_KEY", "")

# Determines whether we are in live mode or test mode
STRIPE_LIVE_MODE = getattr(settings, "STRIPE_LIVE_MODE", False)

# Default secret key
if hasattr(settings, "STRIPE_SECRET_KEY"):
    STRIPE_SECRET_KEY = settings.STRIPE_SECRET_KEY
else:
    STRIPE_SECRET_KEY = LIVE_API_KEY if STRIPE_LIVE_MODE else TEST_API_KEY

# Default public key
if hasattr(settings, "STRIPE_PUBLIC_KEY"):
    STRIPE_PUBLIC_KEY = settings.STRIPE_PUBLIC_KEY
elif STRIPE_LIVE_MODE:
    STRIPE_PUBLIC_KEY = getattr(settings, "STRIPE_LIVE_PUBLIC_KEY", "")
else:
    STRIPE_PUBLIC_KEY = getattr(settings, "STRIPE_TEST_PUBLIC_KEY", "")


def get_default_api_key():
    """
    Returns the default API key for a value of `livemode`.
    """
    if STRIPE_LIVE_MODE:
        # Livemode is unknown. Use the default secret key.
        return LIVE_API_KEY or STRIPE_SECRET_KEY
    else:
        # Livemode is false, use the test secret key
        return TEST_API_KEY or STRIPE_SECRET_KEY


def get_stripe_api_version():
    """Get the desired API version to use for Stripe requests."""
    version = getattr(settings, "STRIPE_API_VERSION", stripe.api_version)
    return version or DEFAULT_STRIPE_API_VERSION


def set_stripe_api_version(version=None, validate=True):
    """
    Set the desired API version to use for Stripe requests.

    :param version: The version to set for the Stripe API.
    :type version: ``str``
    :param validate: If True validate the value for the specified version).
    :type validate: ``bool``
    """
    version = version or get_stripe_api_version()

    if validate:
        valid = validate_stripe_api_version(version)
        if not valid:
            raise ValueError("Bad stripe API version: {}".format(version))

    stripe.api_version = version


def get_subscriber_model_string():
    """Get the configured subscriber model as a module path string."""
    return getattr(settings, "STRIPE_SUBSCRIBER_MODEL", settings.AUTH_USER_MODEL)
