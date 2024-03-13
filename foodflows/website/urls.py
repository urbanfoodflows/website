from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("cities/<int:id>/", views.city, name="city"),
    path("controlpanel/", views.controlpanel, name="controlpanel"),
    path("controlpanel/city/<int:id>/", views.controlpanel_city, name="controlpanel_city"),
    path("controlpanel/file/<int:id>/", views.controlpanel_file, name="controlpanel_file"),
    path("controlpanel/activities/", views.controlpanel_activities, name="controlpanel_activities"),
    path("controlpanel/foodgroups/", views.controlpanel_foodgroups, name="controlpanel_foodgroups"),
]
