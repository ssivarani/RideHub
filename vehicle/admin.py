from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Owner, Renter, Vehicle, Booking


@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):

    list_display=["user","orders_received","view_bookings"]

    readonly_fields=["orders_received","view_bookings"]

    def view_bookings(self,obj):

        url=reverse("admin:vehicle_booking_changelist")

        return format_html(
            '<a class="button" href="{}?vehicle__owner__id__exact={}">View Bookings</a>',
            url,
            obj.user.id
        )

    view_bookings.short_description="Bookings"


@admin.register(Renter)
class RenterAdmin(admin.ModelAdmin):

    list_display=["user","orders_placed","view_bookings"]

    readonly_fields=["orders_placed","view_bookings"]

    def view_bookings(self,obj):

        url=reverse("admin:vehicle_booking_changelist")

        return format_html(
            '<a class="button" href="{}?user__id__exact={}">View Bookings</a>',
            url,
            obj.user.id
        )

    view_bookings.short_description="Bookings"


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):

    list_display=[
        "user",
        "vehicle",
        "from_date",
        "to_date",
        "status",
        "payment_status",
        "total_price"
    ]

    list_filter=[
        "status",
        "payment_status"
    ]

    search_fields=[
        "user__username",
        "vehicle__company",
        "vehicle__model"
    ]

    def lookup_allowed(self, lookup, value, request):

        if lookup in [
            "vehicle__owner__id__exact",
            "user__id__exact"
        ]:
            return True

        return super().lookup_allowed(lookup, value, request)

admin.site.register(Vehicle)
from .models import Contact
admin.site.register(Contact)