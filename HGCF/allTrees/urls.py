from django.urls import path # type: ignore
from . import views

urlpatterns = [
    path("", views.homePage_view, name="home"),
    path("dashboard", views.dashboard_view, name="dashboard"),
    path("announcements", views.announcements_view, name="announcements"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="Logout"),
    path("addTree/<str:locationID2>/<str:areaID2>", views.addTree_view, name="addTree"),
    path("addLocation", views.addLocation_view, name="addLocation"),
    path("addArea/<str:locationID2>", views.addArea_view, name="addArea"),
    path("treeData/<str:locationID2>/<str:areaID2>/<str:treeID2>", views.treeData2_view, name="treeData"),
    path("treeLog/<str:locationID2>/<str:areaID2>/<str:treeID2>/<str:selector>", views.treeLog_view, name="treeLog"),
    path("addLog/<str:locationID2>/<str:areaID2>/<str:treeID2>", views.addLog2_view, name="addLog"),
    path('toggle-valve/', views.toggle_valve, name='toggle_valve'),
    path('irrigation_timer/', views.irrigation_timer, name="irrigation_timer"),
    # path('valve-status/', views.get_valve_status, name='valve_status'),
    path('dashboard/irrigation/valve-statuses/', views.get_all_valve_statuses, name='valve_statuses'),
    path('dashboard/irrigation/', views.irrigation_dashboard, name='irrigation_dashboard'),
    path('dashboard/schedules/', views.get_schedule_overview, name='schedule_overview'),
    path('dashboard/emergency-shutoff/', views.emergency_shutoff, name='emergency_shutoff'),



    
    #Joyces Kitchen URLs
    path("recipeForm", views.recipeForm_view, name="recipeForm"),
    path("recipes/<str:recipe>", views.recipeInfo_view, name="recipeInfo"),
    
    #Environmental URLs
    path("weatherDash", views.weather_dashboard_view, name="weatherDash"),
    
    #Stores
    path("addProduct", views.addProduct_view, name="addProduct"),
    path("store", views.store_view, name="store"),
]

