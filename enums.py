import operator
from collections import OrderedDict

from django.utils.translation import gettext_lazy as _


class EnumMetaClass(type):
    @classmethod
    def __prepare__(self, name, bases):
        return OrderedDict()

    def __new__(mcs, name, bases, classdict):
        members = []
        keys = {}
        choices = OrderedDict()
        for key, value in classdict.items():
            if key.startswith("__"):
                continue
            members.append(key)
            if isinstance(value, tuple):
                value, alias = value
                keys[alias] = key
            else:
                alias = None
            keys[alias or key] = key
            choices[alias or key] = value

        for k, v in keys.items():
            classdict[v] = k

        classdict["__choices__"] = choices
        classdict["__members__"] = members

        # Note: Differences between Python 2.x and Python 3.x force us to
        # explicitly use unicode here, and to explicitly sort the list. In
        # Python 2.x, class members are unordered and so the ordering will
        # vary on different systems based on internal hashing. Without this
        # Django will continually require new no-op migrations.
        classdict["choices"] = tuple(
            (str(k), str(v))
            for k, v in sorted(choices.items(), key=operator.itemgetter(0))
        )

        return type.__new__(mcs, name, bases, classdict)


class Enum(metaclass=EnumMetaClass):
    pass


class CardCheckResult(Enum):
    pass_ = (_("Pass"), "pass")
    fail = _("Fail")
    unavailable = _("Unavailable")
    unchecked = _("Unchecked")


class CardBrand(Enum):
    AmericanExpress = (_("American Express"), "American Express")
    DinersClub = (_("Diners Club"), "Diners Club")
    Discover = _("Discover")
    JCB = _("JCB")
    MasterCard = _("MasterCard")
    UnionPay = _("UnionPay")
    Visa = _("Visa")
    Unknown = _("Unknown")


class CardFundingType(Enum):
    credit = _("Credit")
    debit = _("Debit")
    prepaid = _("Prepaid")
    unknown = _("Unknown")


class CardTokenizationMethod(Enum):
    apple_pay = _("Apple Pay")
    android_pay = _("Android Pay")


class BusinessType(Enum):
    individual = _("Individual")
    company = _("Company")


class AccountType(Enum):
    standard = _("Standard")
    express = _("Express")
    custom = _("Custom")


class CustomerTaxExempt(Enum):
    none = _("None")
    exempt = _("Exempt")
    reverse = _("Reverse")
