from django.contrib import admin

# Register your models here.
from . import models


@admin.register(models.IdempotencyKey)
class IdempotencyKeyAdmin(admin.ModelAdmin):
    list_display = ("uuid", "action", "created", "is_expired", "livemode")
    list_filter = ("livemode",)
    search_fields = ("uuid", "action")

    def has_add_permission(self, request):
        return False
