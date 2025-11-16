from django.contrib import admin
from django.utils.text import Truncator

from .models import NCM


@admin.register(NCM)
class NCMAdmin(admin.ModelAdmin):
    list_display = ("code", "short_description")
    search_fields = ("code", "description")
    ordering = ("code",)

    @staticmethod
    def short_description(obj):
        return Truncator(obj.description).chars(80)

    short_description.short_description = "Description"
