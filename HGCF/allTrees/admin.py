from django.contrib import admin # type: ignore
from .models import *

# Register your models here.
admin.site.register(individualTrees_model)
admin.site.register(locationTree_model)
admin.site.register(areaTree_model)
admin.site.register(logCategory_model)
admin.site.register(treeLogs_model)
admin.site.register(tree_qr)
admin.site.register(recipeModel)
admin.site.register(cart_items)
admin.site.register(valve_registration)
admin.site.register(valve_schedule)

class POSSaleItemInline(admin.TabularInline):
    model = POSSaleItem
    extra = 0
    fields = (
        'product',
        'product_name_snapshot',
        'sku_snapshot',
        'quantity',
        'unit_price',
        'line_subtotal',
        'sold_by_weight',
        'weight_amount',
    )
    readonly_fields = (
        'product_name_snapshot',
        'sku_snapshot',
        'line_subtotal',
    )


class POSPaymentEventInline(admin.TabularInline):
    model = POSPaymentEvent
    extra = 0
    fields = (
        'provider',
        'event_type',
        'external_id',
        'created_at',
    )
    readonly_fields = (
        'provider',
        'event_type',
        'external_id',
        'created_at',
    )
    show_change_link = True

class ProductVariantInline(admin.TabularInline):
    model = mainStore_product_variants
    extra = 1
    fields = (
        "variant_name",
        "size",
        "sku",
        "price_override",
        "sale_price_override",
        "inventory_total",
        "is_active",
        "is_active_online",
        "is_active_offline",
        "display_order",
    )

@admin.register(mainStore_products)
class MainStoreProductsAdmin(admin.ModelAdmin):
    list_display = (
        "product_name",
        "product_type",
        "price",
        "unit_type",
        "inventory_status",
        "show_in_store",
        "is_active_online",
        "pos_display_order",
    )

    list_filter = (
        "product_type",
        "inventory_status",
        "show_in_store",
        "is_active",
        "is_active_online",
        "is_active_offline",
        "on_sale",
    )

    search_fields = (
        "product_name",
        "sku",
        "description",
    )

    inlines = [ProductVariantInline]

class UPickTimeSlotInline(admin.TabularInline):
    model = UPickTimeSlot
    extra = 1
    fields = (
        "start_time",
        "end_time",
        "capacity",
        "is_active",
        "is_walk_in_available",
        "notes",
    )


@admin.register(UPickEvent)
class UPickEventAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "crop_name",
        "date",
        "is_active",
        "is_public",
        "default_slot_capacity",
    )

    list_filter = (
        "crop_name",
        "is_active",
        "is_public",
        "date",
    )

    search_fields = (
        "title",
        "crop_name",
        "description",
    )

    inlines = [UPickTimeSlotInline]


@admin.register(UPickTimeSlot)
class UPickTimeSlotAdmin(admin.ModelAdmin):
    list_display = (
        "event",
        "start_time",
        "end_time",
        "capacity",
        "spots_remaining",
        "is_active",
        "is_walk_in_available",
    )

    list_filter = (
        "event__date",
        "is_active",
        "is_walk_in_available",
    )

    search_fields = (
        "event__title",
        "event__crop_name",
    )


@admin.register(UPickReservation)
class UPickReservationAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "email",
        "phone",
        "party_size",
        "time_slot",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "time_slot__event__date",
        "time_slot__event__crop_name",
    )

    search_fields = (
        "first_name",
        "last_name",
        "email",
        "phone",
    )

    readonly_fields = (
        "ip_address",
        "created_at",
        "updated_at",
        "check_in_time",
        "completed_time",
    )

@admin.register(POSSession)
class POSSessionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'status',
        'opened_by',
        'opened_at',
        'closed_by',
        'closed_at',
        'opening_cash',
        'closing_cash',
        'expected_cash',
    )

    list_filter = (
        'status',
        'opened_at',
        'closed_at',
    )

    search_fields = (
        'opened_by__username',
        'closed_by__username',
        'notes',
    )

    readonly_fields = (
        'opened_at',
        'closed_at',
    )


@admin.register(POSSale)
class POSSaleAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'sale_number',
        'status',
        'payment_method',
        'subtotal',
        'tax_amount',
        'total',
        'customer_name',
        'created_by',
        'created_at',
        'completed_at',
    )

    list_filter = (
        'status',
        'payment_method',
        'created_at',
        'completed_at',
        'session',
    )

    search_fields = (
        'sale_number',
        'customer_name',
        'customer_email',
        'stripe_payment_intent_id',
        'stripe_charge_id',
        'notes',
    )

    readonly_fields = (
        'created_at',
        'completed_at',
    )

    inlines = [POSSaleItemInline, POSPaymentEventInline]


@admin.register(POSSaleItem)
class POSSaleItemAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'sale',
        'product_name_snapshot',
        'quantity',
        'unit_price',
        'line_subtotal',
        'sold_by_weight',
        'weight_amount',
        'created_at',
    )

    list_filter = (
        'sold_by_weight',
        'created_at',
    )

    search_fields = (
        'product_name_snapshot',
        'sku_snapshot',
        'sale__sale_number',
    )

    readonly_fields = (
        'created_at',
    )


@admin.register(POSPaymentEvent)
class POSPaymentEventAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'sale',
        'provider',
        'event_type',
        'external_id',
        'created_at',
    )

    list_filter = (
        'provider',
        'event_type',
        'created_at',
    )

    search_fields = (
        'sale__sale_number',
        'external_id',
        'event_type',
    )

    readonly_fields = (
        'created_at',
    )