# Generated by Django 2.2.4 on 2019-09-26 08:24
import uuid

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion

from fields import StripeDateTimeField, StripeCurrencyCodeField, StripeEnumField
from enums import CustomerTaxExempt, CardCheckResult, CardBrand, CardFundingType, CardTokenizationMethod, BusinessType, \
    AccountType


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='IdempotencyKey',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('action', models.CharField(max_length=100)),
                ('livemode', models.BooleanField(help_text='Whether the key was used in live or test mode.')),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'unique_together': {('action', 'livemode')},
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_id', models.CharField(max_length=255, unique=True)),
                ('created', StripeDateTimeField(blank=True, help_text='The datetime this object was created in stripe.',
                                                null=True)),
                ('livemode', models.NullBooleanField(default=None,
                                                     help_text='Null here indicates that the livemode status is unknown or was previously unrecorded. Otherwise, this field indicates whether this record comes from Stripe test mode or live mode operation.')),
                ('metadata', django.contrib.postgres.fields.jsonb.JSONField(blank=True,
                                                                            help_text='A set of key/value pairs that you can attach to an object. It can be useful for storing additional information about an object in a structured format.',
                                                                            null=True)),
                ('description', models.TextField(blank=True, help_text='A description of this object.', null=True)),
                ('address',
                 django.contrib.postgres.fields.jsonb.JSONField(blank=True, help_text="The customer's address.",
                                                                null=True)),
                ('balance', models.IntegerField(
                    help_text="Current balance, if any, being stored on the customer's account. If negative, the customer has credit to apply to the next invoice. If positive, the customer has an amount owed that will be added to the next invoice. The balance does not refer to any unpaid invoices; it solely takes into account amounts that have yet to be successfully applied to any invoice. This balance is only taken into account for recurring billing purposes (i.e., subscriptions, invoices, invoice items).")),
                ('currency', StripeCurrencyCodeField(default='',
                                                     help_text='The currency the customer can be charged in for recurring billing purposes',
                                                     max_length=3)),
                ('default_source', models.CharField(blank=True, max_length=12, null=True)),
                ('delinquent', models.BooleanField(
                    help_text="Whether or not the latest charge for the customer's latest invoice has failed.")),
                ('discount', django.contrib.postgres.fields.jsonb.JSONField(blank=True,
                                                                            help_text='current discount active on the customer, if there is one',
                                                                            null=True)),
                ('email', models.TextField(blank=True, default='', max_length=5000)),
                ('invoice_prefix', models.CharField(blank=True, default='',
                                                    help_text='The prefix for the customer used to generate unique invoice numbers.',
                                                    max_length=255)),
                ('invoice_settings', django.contrib.postgres.fields.jsonb.JSONField(blank=True,
                                                                                    help_text="The customer's default invoice settings.",
                                                                                    null=True)),
                ('name',
                 models.TextField(blank=True, default='', help_text="The customer's full name or business name.",
                                  max_length=5000)),
                ('phone',
                 models.TextField(blank=True, default='', help_text="The customer's phone number.", max_length=5000)),
                ('preferred_locales', django.contrib.postgres.fields.jsonb.JSONField(blank=True,
                                                                                     help_text="The customer's preferred locales (languages), ordered by preference.",
                                                                                     null=True)),
                ('shipping', django.contrib.postgres.fields.jsonb.JSONField(blank=True,
                                                                            help_text='Shipping information associated with the customer.',
                                                                            null=True)),
                ('tax_exempt', StripeEnumField(default='', enum=CustomerTaxExempt,
                                               help_text='Describes the customer\'s tax exemption status. When set to reverse, invoice and receipt PDFs include the text "Reverse charge".',
                                               max_length=7)),
                ('date_purged', models.DateTimeField(editable=False, null=True)),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL,
                                              related_name='stripe_customer', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'livemode')},
            },
        ),
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_id', models.CharField(max_length=255, unique=True)),
                ('created', StripeDateTimeField(blank=True, help_text='The datetime this object was created in stripe.',
                                                null=True)),
                ('livemode', models.NullBooleanField(default=None,
                                                     help_text='Null here indicates that the livemode status is unknown or was previously unrecorded. Otherwise, this field indicates whether this record comes from Stripe test mode or live mode operation.')),
                ('metadata', django.contrib.postgres.fields.jsonb.JSONField(blank=True,
                                                                            help_text='A set of key/value pairs that you can attach to an object. It can be useful for storing additional information about an object in a structured format.',
                                                                            null=True)),
                ('description', models.TextField(blank=True, help_text='A description of this object.', null=True)),
                ('address_city',
                 models.TextField(blank=True, default='', help_text='City/District/Suburb/Town/Village.',
                                  max_length=5000)),
                ('address_country',
                 models.TextField(blank=True, default='', help_text='Billing address country.', max_length=5000)),
                ('address_line1',
                 models.TextField(blank=True, default='', help_text='Street address/PO Box/Company name.',
                                  max_length=5000)),
                ('address_line1_check', StripeEnumField(blank=True, default='', enum=CardCheckResult,
                                                        help_text='If `address_line1` was provided, results of the check.',
                                                        max_length=11)),
                ('address_line2',
                 models.TextField(blank=True, default='', help_text='Apartment/Suite/Unit/Building.', max_length=5000)),
                ('address_state',
                 models.TextField(blank=True, default='', help_text='State/County/Province/Region.', max_length=5000)),
                ('address_zip',
                 models.TextField(blank=True, default='', help_text='ZIP or postal code.', max_length=5000)),
                ('address_zip_check', StripeEnumField(blank=True, default='', enum=CardCheckResult,
                                                      help_text='If `address_zip` was provided, results of the check.',
                                                      max_length=11)),
                ('brand', StripeEnumField(enum=CardBrand, help_text='Card brand.', max_length=16)),
                ('country', models.CharField(blank=True, default='',
                                             help_text='Two-letter ISO code representing the country of the card.',
                                             max_length=2)),
                ('cvc_check', StripeEnumField(blank=True, default='', enum=CardCheckResult,
                                              help_text='If a CVC was provided, results of the check.', max_length=11)),
                ('dynamic_last4', models.CharField(blank=True, default='',
                                                   help_text='(For tokenized numbers only.) The last four digits of the device account number.',
                                                   max_length=4)),
                ('exp_month', models.IntegerField(help_text='Card expiration month.')),
                ('exp_year', models.IntegerField(help_text='Card expiration year.')),
                ('fingerprint',
                 models.CharField(blank=True, default='', help_text='Uniquely identifies this particular card number.',
                                  max_length=16)),
                ('funding', StripeEnumField(enum=CardFundingType, help_text='Card funding type.', max_length=7)),
                ('last4', models.CharField(help_text='Last four digits of Card number.', max_length=4)),
                ('name', models.TextField(blank=True, default='', help_text='Cardholder name.', max_length=5000)),
                ('tokenization_method', StripeEnumField(blank=True, default='', enum=CardTokenizationMethod,
                                                        help_text='If the card number is tokenized, this is the method that was used.',
                                                        max_length=11)),
                ('customer',
                 models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='legacy_cards',
                                   to='stripe.Customer')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_id', models.CharField(max_length=255, unique=True)),
                ('created', StripeDateTimeField(blank=True, help_text='The datetime this object was created in stripe.',
                                                null=True)),
                ('livemode', models.NullBooleanField(default=None,
                                                     help_text='Null here indicates that the livemode status is unknown or was previously unrecorded. Otherwise, this field indicates whether this record comes from Stripe test mode or live mode operation.')),
                ('metadata', django.contrib.postgres.fields.jsonb.JSONField(blank=True,
                                                                            help_text='A set of key/value pairs that you can attach to an object. It can be useful for storing additional information about an object in a structured format.',
                                                                            null=True)),
                ('description', models.TextField(blank=True, help_text='A description of this object.', null=True)),
                ('business_profile', django.contrib.postgres.fields.jsonb.JSONField(blank=True,
                                                                                    help_text='Optional information related to the business.',
                                                                                    null=True)),
                ('business_type',
                 StripeEnumField(blank=True, default='', enum=BusinessType, help_text='The business type.',
                                 max_length=10)),
                ('capabilities', django.contrib.postgres.fields.jsonb.JSONField(blank=True,
                                                                                help_text='Capabilities that was requested for this account and their associated states',
                                                                                null=True)),
                ('charges_enabled', models.BooleanField(help_text='Whether the account can create live charges')),
                ('company', django.contrib.postgres.fields.jsonb.JSONField(blank=True,
                                                                           help_text='Information about the company or business. This field is null unless business_type is set to company.',
                                                                           null=True)),
                ('country', models.CharField(help_text='The country of the account', max_length=2)),
                ('default_currency',
                 StripeCurrencyCodeField(help_text='The currency this account has chosen to use as the default',
                                         max_length=3)),
                ('details_submitted', models.BooleanField(
                    help_text='Whether account details have been submitted. Standard accounts cannot receive payouts before this is true.')),
                ('email', models.CharField(help_text='The primary user’s email address.', max_length=255)),
                ('individual', django.contrib.postgres.fields.jsonb.JSONField(blank=True,
                                                                              help_text='Information about the person represented by the account. This field is null unless business_type is set to individual.',
                                                                              null=True)),
                ('payouts_enabled', models.BooleanField(help_text='Whether Stripe can send payouts to this account')),
                ('requirements', django.contrib.postgres.fields.jsonb.JSONField(blank=True,
                                                                                help_text='Information about the requirements for the account, including what information needs to be collected, and by when.',
                                                                                null=True)),
                ('settings', django.contrib.postgres.fields.jsonb.JSONField(blank=True,
                                                                            help_text='Account options for customizing how the account functions within Stripe.',
                                                                            null=True)),
                ('tos_acceptance', django.contrib.postgres.fields.jsonb.JSONField(blank=True,
                                                                                  help_text='Details on the acceptance of the Stripe Services Agreement',
                                                                                  null=True)),
                ('type', StripeEnumField(enum=AccountType, help_text='The Stripe account type.', max_length=8)),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL,
                                              related_name='stripe_account', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]