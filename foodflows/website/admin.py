from django.contrib import admin
from .models import *
from django.contrib.admin import AdminSite

class MyAdminSite(AdminSite):
    # Text to put at the end of each page"s <title>.
    site_title = "Urban Food Flows"

    # Text to put in each page"s <h1> (and above login form).
    site_header = "Urban Food Flows Admin"

    # Text to put at the top of the admin index page.
    index_title = "Urban Food Flows"
    enable_nav_sidebar = False

class ActivityAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name", "position", "shortname", "is_active", "is_described", "has_dqi"]

admin_site = MyAdminSite()

admin_site.register(City)
admin_site.register(Population)
admin_site.register(Page)
admin_site.register(Activity, ActivityAdmin)
admin_site.register(FoodGroup)
admin_site.register(Data)
admin_site.register(Indicator)
admin_site.register(IndicatorDescription)
admin_site.register(IdealConsumption)
