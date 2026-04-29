from django.urls import path  # type: ignore
from . import views

urlpatterns = [
    path("", views.homePage_view, name="home"),
    path("dashboard", views.dashboard_view, name="dashboard"),
    path("announcements", views.announcements_view, name="announcements"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="Logout"),
    path("addTree/<str:locationID2>/<str:areaID2>", views.addTree_view, name="addTree"),

    # ---- Irrigation ----------
    path('irrigation/dashboard', views.irrigation_dashboard, name='irrigation_dashboard'),
    path('irrigation/dashboard/valve-statuses/', views.get_all_valve_statuses, name='valve_statuses'),
    path('irrigation/dashboard/toggle-valve/', views.toggle_valve, name='toggle_valve'),
    path('irrigation/add-schedule/', views.irrigation_timer, name="irrigation_timer"),
    path('irrigation/add-valve/', views.add_valve, name="add_valve"),
    path('irrigation/emergency-shutoff/', views.emergency_shutoff, name='emergency_shutoff'),
    path('irrigation/schedules/', views.get_schedule_overview, name='schedule_overview'),

    # ---- Tree Grid -----------
    path('treespace/locations/', views.location_list_view, name='location_list'),
    path('treespace/area/<int:location_id>/', views.area_list_view, name='area_list'),
    path('treespace/tree-grid/<int:area_id>/', views.area_tree_grid_view, name='tree_grid'),
    path("treespace/tree-data/<str:locationID>/<str:areaID>/<str:treeID>", views.treeData_view, name="treeData"),
    path("treespace/tree-data/add-log/<str:locationID>/<str:areaID>/<str:treeID>", views.addLog_view, name="addLog"),
    path("treespace/tree-data/logs/<str:locationID>/<str:areaID>/<str:treeID>/<str:selector>", views.treeLog_view, name="treeLog"),
    path("treespace/locations/add", views.addLocation_view, name="add_location"),
    path("treespace/areas/add/<int:location_id>", views.addArea_view, name="add_area"),

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
]