from django.urls import path  # type: ignore
from . import views

urlpatterns = [
    path("", views.homePage_view, name="home"),
    path("dashboard", views.dashboard_view, name="dashboard"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="Logout"),
    path("addTree/<str:locationID2>/<str:areaID2>", views.addTree_view, name="addTree"),

    # ---- Our Story -----------
    path("our-story/", views.our_story_view, name="our_story"),
    path("our-story/subscribe/", views.our_story_subscribe_view, name="our_story_subscribe"),
    path("subscribe/", views.farm_subscribe_view, name="farm_subscribe"),

    # ---- Announcements ------------
    path("announcements/", views.announcements_view, name="announcements"),
    path("announcements/<slug:slug>/", views.announcement_detail_view, name="announcement_detail"),
    path("treespace/announcements/", views.treespace_announcement_setup_view, name="treespace_announcement_setup"),
    path("treespace/email-update/", views.treespace_email_update_view, name="treespace_email_update"),

    # ---- Irrigation ----------
    path('irrigation/dashboard', views.irrigation_dashboard, name='irrigation_dashboard'),
    path('irrigation/dashboard/valve-statuses/', views.get_all_valve_statuses, name='valve_statuses'),
    path('irrigation/dashboard/toggle-valve/', views.toggle_valve, name='toggle_valve'),
    path('irrigation/add-schedule/', views.irrigation_timer, name="irrigation_timer"),
    path('irrigation/add-valve/', views.add_valve, name="add_valve"),
    path('irrigation/emergency-shutoff/', views.emergency_shutoff, name='emergency_shutoff'),
    path('irrigation/schedules/', views.get_schedule_overview, name='schedule_overview'),
    path('irrigation/schedule/<int:schedule_id>/edit/', views.irrigation_schedule_edit, name='irrigation_schedule_edit'),
    path('irrigation/schedule/<int:schedule_id>/delete/', views.irrigation_schedule_delete, name='irrigation_schedule_delete'),

    # ---- Tree / Farm Map -----------

    # New main Farm Map routes
    path('treespace/farm-map/', views.farm_map_view, name='farm_map'),
    path('treespace/farm-map/location/<int:location_id>/', views.farm_map_view, name='farm_map_location'),
    path('treespace/farm-map/location/<int:location_id>/area/<int:area_id>/', views.farm_map_view, name='farm_map_area'),

    # Quick View API
    path('treespace/api/tree-quick-view/<int:tree_pk>/', views.tree_quick_view_api, name='tree_quick_view_api'),

    # Add pages
    path("treespace/locations/add/", views.addLocation_view, name="add_location"),
    path("treespace/areas/add/<int:location_id>/", views.addArea_view, name="add_area"),

    # Full Tree Pages
    path("treespace/tree-data/<str:locationID>/<str:areaID>/<str:treeID>/", views.treeData_view, name="treeData"),
    path("treespace/tree-data/<str:locationID>/<str:areaID>/<str:treeID>/add-log/", views.addLog_view, name="addLog"),
    path("treespace/tree-data/<str:locationID>/<str:areaID>/<str:treeID>/logs/<str:selector>/", views.treeLog_view, name="treeLog"),
    path("treespace/tree-data/<str:locationID>/<str:areaID>/<str:treeID>/edit/", views.editTree_view, name="editTree"),

    # Legacy redirects
    path('treespace/locations/', views.legacy_location_list_redirect, name='location_list'),
    path('treespace/area/<int:location_id>/', views.legacy_area_list_redirect, name='area_list'),
    path('treespace/tree-grid/<int:area_id>/', views.legacy_tree_grid_redirect, name='tree_grid'),




    # Joyce's Kitchen URLs
    path("recipeForm", views.recipeForm_view, name="recipeForm"),
    path("recipes/<str:recipe>", views.recipeInfo_view, name="recipeInfo"),

    # Environmental URLs
    path("weatherDash", views.weather_dashboard_view, name="weatherDash"),

    # Stores
    path("addProduct", views.addProduct_view, name="addProduct"),
    path("store", views.store_view, name="store"),
    path("cart/", views.cart_view, name="cart"),
    path("cart/update/", views.update_cart_item, name="update_cart_item"),
    path("cart/remove/", views.remove_cart_item, name="remove_cart_item"),
    path("checkout/create-session/", views.create_checkout_session_view, name="create_checkout_session"),
    path("checkout/success/", views.checkout_success_view, name="checkout_success"),
    path("checkout/create-session/", views.create_checkout_session_view, name="create_checkout_session"),
    path("checkout/success/", views.checkout_success_view, name="checkout_success"),
    path("stripe/webhook/", views.stripe_webhook_view, name="stripe_webhook"),

    # UPICK
    path("upick/", views.upick_landing_view, name="upick_landing"),
    path("upick/day/<int:event_id>/", views.upick_day_view, name="upick_day"),
    path("upick/reserve/<int:slot_id>/", views.upick_reserve_view, name="upick_reserve"),
    path("upick/success/<int:reservation_id>/", views.upick_success_view, name="upick_success"),
    path("treespace/upick/", views.treespace_upick_dashboard_view, name="treespace_upick_dashboard"),
    path("treespace/upick/reservation/status/", views.treespace_upick_update_reservation_status, name="treespace_upick_update_reservation_status"),
    path("treespace/upick/setup/", views.treespace_upick_setup_view, name="treespace_upick_setup"),
    path("upick/<int:event_id>/waitlist/", views.upick_join_waitlist, name="upick_join_waitlist"),
    path("treespace/upick/waitlist/<int:entry_id>/convert/", views.treespace_upick_convert_waitlist_entry,name="treespace_upick_convert_waitlist_entry"),
    path("treespace/upick/waitlist/<int:entry_id>/remove/", views.treespace_upick_remove_waitlist_entry, name="treespace_upick_remove_waitlist_entry"),
    path("upick/waitlist/",views.upick_general_waitlist_view,name="upick_general_waitlist"),
    path("treespace/upick/waitlist/",views.treespace_upick_waitlist_view,name="treespace_upick_waitlist"),
    path("treespace/upick/reservation/<int:reservation_id>/strawberries-depleted-email/", views.treespace_send_strawberries_depleted_email, name="treespace_send_strawberries_depleted_email"),

    # ---- POS ----------
    path("pos/", views.pos_terminal_page, name="pos_terminal_page"),
    path("pos/api/products/", views.pos_products_api, name="pos_products_api"),
    path("pos/api/calculate-totals/", views.pos_calculate_totals_api, name="pos_calculate_totals_api"),
    path("pos/api/create-sale/", views.pos_create_sale_api, name="pos_create_sale_api"),
    path("pos/api/sale/<int:sale_id>/", views.pos_sale_detail_api, name="pos_sale_detail_api"),
    path("pos/api/sale/<int:sale_id>/complete-cash/", views.pos_complete_cash_sale_api, name="pos_complete_cash_sale_api"),
    path("pos/api/readers/", views.pos_terminal_readers_api, name="pos_terminal_readers_api"),
    path("pos/api/sale/<int:sale_id>/start-card-payment/", views.pos_start_card_payment_api, name="pos_start_card_payment_api"),
    path("pos/api/sale/<int:sale_id>/card-payment-status/", views.pos_card_payment_status_api, name="pos_card_payment_status_api"),
    path("pos/api/sale/<int:sale_id>/cancel-card-payment/", views.pos_cancel_card_payment_api, name="pos_cancel_card_payment_api"),
    path("pos/stripe/webhook/", views.stripe_terminal_webhook, name="stripe_terminal_webhook"),
    path("pos/api/today-reservations/", views.pos_today_reservations_api, name="pos_today_reservations_api"),
    path("pos/products/", views.pos_products_list_page, name="pos_products_list_page"),
    path("pos/products/<int:product_id>/edit/", views.pos_product_edit_page, name="pos_product_edit_page"),
    path("pos/api/sale/<int:sale_id>/manual-card-complete/", views.pos_complete_manual_card_sale_api, name="pos_complete_manual_card_sale_api"),
    path("pos/sales/", views.pos_sales_list_page, name="pos_sales_list_page"),
    path("pos/api/sale/<int:sale_id>/resend-receipt/", views.pos_resend_receipt_api, name="pos_resend_receipt_api"),
]