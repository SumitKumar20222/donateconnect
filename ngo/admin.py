from django.contrib import admin
from .models import Donation
from django.utils.html import format_html


class DonationAdmin(admin.ModelAdmin):
    list_display = ('name', 'item_type', 'quantity', 'assigned_to', 'show_image')

    def show_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100"/>', obj.image.url)
        return "No Image"

    show_image.short_description = "Image"


admin.site.register(Donation, DonationAdmin)