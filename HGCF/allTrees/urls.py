from django.urls import path # type: ignore
from . import views

urlpatterns = [
    path("", views.homePage_view, name="home"),
    path("dashboard", views.dashboard_view, name="dashboard"),
    path("announcements", views.announcements_view, name="announcements"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="Logout"),
    path("addTree/<str:locationID2>/<str:areaID2>", views.addTree_view, name="addTree"),
    # path('valve-status/', views.get_valve_status, name='valve_status'),

    #---- Irrigation ----------
    path('irrigation/dashboard', views.irrigation_dashboard, name='irrigation_dashboard'),
    path('irrigation/dashboard/valve-statuses/', views.get_all_valve_statuses, name='valve_statuses'),
    path('irrigation/dashboard/toggle-valve/', views.toggle_valve, name='toggle_valve'),
    path('irrigation/add-schedule/', views.irrigation_timer, name="irrigation_timer"),
    path('irrigation/add-valve/', views.add_valve, name="add_valve"),
    path('irrigation/emergency-shutoff/', views.emergency_shutoff, name='emergency_shutoff'),
    path('irrigation/schedules/', views.get_schedule_overview, name='schedule_overview'),


    #---- Tree Grid -----------
    path('treespace/locations/', views.location_list_view, name='location_list'),
    path('treespace/area/<int:location_id>/', views.area_list_view, name='area_list'),
    path('treespace/tree-grid/<int:area_id>/', views.area_tree_grid_view, name='tree_grid'),
    path("treespace/tree-data/<str:locationID>/<str:areaID>/<str:treeID>", views.treeData_view, name="treeData"),
    path("treespace/tree-data/add-log/<str:locationID>/<str:areaID>/<str:treeID>", views.addLog_view, name="addLog"),
    path("treespace/tree-data/logs/<str:locationID>/<str:areaID>/<str:treeID>/<str:selector>", views.treeLog_view, name="treeLog"),

    path("treespace/locations/add", views.addLocation_view, name="add_location"),
    path("treespace/areas/add/<int:location_id>", views.addArea_view, name="add_area"),



    
    #Joyces Kitchen URLs
    path("recipeForm", views.recipeForm_view, name="recipeForm"),
    path("recipes/<str:recipe>", views.recipeInfo_view, name="recipeInfo"),
    
    #Environmental URLs
    path("weatherDash", views.weather_dashboard_view, name="weatherDash"),
    
    #Stores
    path("addProduct", views.addProduct_view, name="addProduct"),
    path("store", views.store_view, name="store"),
]

