from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("cities/<int:id>/", views.city, name="city"),
    path("dqi/", views.dqi, name="dqi"),

    # Data section
    path("data/diet/", views.ideal_diet, name="ideal_diet"),
    path("data/diet/chart/", views.ideal_diet, {"page": "chart"}, name="ideal_diet_chart"),
    path("data/diet/diffchart/", views.ideal_diet, {"page": "diffchart"}, name="ideal_diet_diffchart"),
    path("data/diet/barchart/", views.ideal_diet, {"page": "barchart"}, name="ideal_diet_barchart"),
    path("data/diet/barchartgrouped/", views.ideal_diet, {"page": "barchartgrouped"}, name="ideal_diet_barchartgrouped"),
    path("data/diet/foodgroups/", views.ideal_diet, {"page": "foodgroups"}, name="ideal_diet_foodgroups"),
    path("data/consumption/", views.consumption, name="consumption"),
    path("data/consumption/table/", views.consumption, {"page": "table"}, name="consumption_table"),
    path("data/consumption/barchartgrouped/", views.consumption, {"page": "barchartgrouped"}, name="consumption_barchartgrouped"),
    path("data/dqi/", views.data_dqi, name="data_dqi"),
    path("data/production/", views.production_overview, name="production"),
    path("data/production/table/", views.production, {"page": "table"}, name="production_table"),
    path("data/production/comparison/", views.production, {"page": "comparison"}, name="production_comparison"),
    path("data/impact/", views.impact, name="impact"),
    path("data/impact/chart/", views.impact, {"page": "chart"}, name="impact_chart"),
    path("data/impact/chart/<slug:impact_type>/", views.impact, {"page": "chart"}, name="impact_chart"),
    path("data/impact/table/", views.impact, {"page": "table"}, name="impact_table"),
    path("data/table/", views.data_table, name="data_table"),
    path("data/", views.data, name="data"),
    path("data/city/<int:id>/", views.data_city, name="data_city"),
    path("data/city/", views.data_city, name="data_city"),

    path("controlpanel/", views.controlpanel, name="controlpanel"),
    path("controlpanel/city/<int:id>/", views.controlpanel_city, name="controlpanel_city"),
    path("controlpanel/city/<int:city>/datadescriptions/", views.controlpanel_datadescription, name="controlpanel_datadescription"),
    path("controlpanel/city/<int:city>/datadescriptions/<int:id>/", views.controlpanel_datadescription, name="controlpanel_datadescription"),
    path("controlpanel/file/<int:id>/", views.controlpanel_file, name="controlpanel_file"),
    path("controlpanel/activities/", views.controlpanel_activities, name="controlpanel_activities"),
    path("controlpanel/foodgroups/", views.controlpanel_foodgroups, name="controlpanel_foodgroups"),

    path("chart/", views.chart, name="chart"),
]
