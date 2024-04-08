from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("cities/<int:id>/", views.city, name="city"),
    path("data/diet/", views.ideal_diet, name="ideal_diet"),
    path("data/diet/chart/", views.ideal_diet, {"page": "chart"}, name="ideal_diet_chart"),
    path("data/diet/diffchart/", views.ideal_diet, {"page": "diffchart"}, name="ideal_diet_diffchart"),
    path("data/diet/individualchart/", views.ideal_diet, {"page": "individualchart"}, name="ideal_diet_individualchart"),
    path("data/diet/foodgroups/", views.ideal_diet, {"page": "foodgroups"}, name="ideal_diet_foodgroups"),
    path("controlpanel/", views.controlpanel, name="controlpanel"),
    path("controlpanel/city/<int:id>/", views.controlpanel_city, name="controlpanel_city"),
    path("controlpanel/city/<int:city>/datadescriptions/", views.controlpanel_datadescription, name="controlpanel_datadescription"),
    path("controlpanel/city/<int:city>/datadescriptions/<int:id>/", views.controlpanel_datadescription, name="controlpanel_datadescription"),
    path("controlpanel/file/<int:id>/", views.controlpanel_file, name="controlpanel_file"),
    path("controlpanel/activities/", views.controlpanel_activities, name="controlpanel_activities"),
    path("controlpanel/foodgroups/", views.controlpanel_foodgroups, name="controlpanel_foodgroups"),

    path("chart/", views.chart, name="chart"),
]
