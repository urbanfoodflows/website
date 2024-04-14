from django.shortcuts import render
from .models import *
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
import pandas as pd
import numpy as np
from django.db.models import Sum, OuterRef, Subquery, FloatField, ExpressionWrapper, F
from django.db.models.expressions import RawSQL
import math
from collections import defaultdict

#########################################################
# START OF CENTRAL FUNTIONS        
# These functions are called on from different places
#########################################################

# Used in a number of places to do a subquery in order to get the relevant population for a data point
POPULATION = Population.objects.filter(city_id=OuterRef("city_id"), year=OuterRef("year"))[:1]

# Quick debugging, sometimes it's tricky to locate the PRINT in all the Django
# output in the console, so just using a simply function to highlight it better
def p(text):
    print("----------------------")
    print(text)
    print("----------------------")

# We use this function to get the per-capita total, which requires a subquery to query the population table
# and conversion to a float as not to have an integer being returned. We can use this on any query and it 
# will return the figure
def per_capita_total(query):
    query = query.aggregate(
        per_capita=ExpressionWrapper(
            Sum(F("quantity") * 1000.0 / Subquery(POPULATION.values("population")[:1])),
            output_field=FloatField()
        )
    )
    return query["per_capita"]

# Similar to before, but now for the environmental impact
def per_capita_impact(query, field):
    field = "food_group__" + field
    query = query.aggregate(
        per_capita=ExpressionWrapper(
            Sum(F("quantity") * 1000.0 * F(field) / Subquery(POPULATION.values("population")[:1])),
            output_field=FloatField()
        )
    )
    return query["per_capita"]

# For creation of pie charts, bar charts, etc we need to get the food group, its color, and its 
# total quantity PER CAPITA. This requires a population subquery. We do this in a central query to not repeat.
def per_capita_breakdown(query, params={}):
    # First let's select the values we need, and add the total quantity
    fields_to_include = ["food_group__name","food_group__color"]
    if "include_city" in params:
        fields_to_include.append("city_id")
    query = query.values(*fields_to_include).annotate(total=Sum("quantity"))

    # Define a FloatField for the per_capita annotation, otherwise these figures are integers
    per_capita_field = FloatField() 

    query = query.annotate(population=Subquery(POPULATION.values("population")[:1]))

    # If we need the impact factors, then we check which field and we multiply it by that field
    if "impact" in params:
        field = "food_group__" + params["impact"]
        query = query.annotate(per_capita=ExpressionWrapper(
            F("total") * 1000.0 / F("population") * F(field),
            output_field=per_capita_field
        ))
        # And we also want not just the total quantity, but the total quantity of that impact
        query = query.annotate(total_impact=Sum("quantity")*F(field))
    else:
        # Otherwise we multiply the total quantity by population and that's it.
        query = query.annotate(per_capita=ExpressionWrapper(
            F("total") * 1000.0 / F("population"),
            output_field=per_capita_field
        ))

    if "top_ten" in params and query:
        query = query.order_by("-per_capita")[:10]

    return query

# We figure out what the list of cities is. Either based on GET parameters if they are set, 
# or otherwise all the active cities.
def get_cities(request, include_sample_city=False):
    if "cities" in request.GET:
        cities = City.objects.filter(is_active=True, pk__in=request.GET.getlist("cities"))
    else:
        cities = City.objects.filter(is_active=True)
    if include_sample_city:
        cities = cities | City.objects.filter(pk=5) # This is the sample city ID
    return cities

#################################### 
#   END OF CENTRAL FUNTIONS        
####################################


@login_required
def index(request):

    context = {
        "menu": "index",
    }

    return render(request, "index.html", context)

@login_required
def dqi(request):

    context = {
        "menu": "dqi",
        "page": Page.objects.get(slug="dqi"),
        "remove_full_width": True,
        "dqi": Indicator.objects.all(),
    }

    return render(request, "dqi.html", context)

@login_required
def city(request, id):

    if "cities" in request.GET:
        return redirect("city", request.GET["cities"])
    elif not id:
        id = 1
    city = City.objects.get(is_active=True, pk=id)

    ratings = {}
    for each in DataQualityIndicator.objects.filter(data__city=id):
        if not each.indicator.indicator.name in ratings:
            ratings[each.indicator.indicator.name] = {}
        ratings[each.indicator.indicator.name][each.data.activity.name] = each.indicator

    context = {
        "city": city,
        "descriptions": DataDescription.objects.filter(city_id=id),
        "activities": Activity.objects.all(),
        "indicators": Indicator.objects.all(),
        "ratings": ratings,
        "submenu": "description",
    }

    return render(request, "city.html", context)

#################################### 
#   DATA PORTAL VIEWS
####################################

@login_required
def data(request):

    cities = get_cities(request)
    consumption_data = {}
    consumption_total = {}
    emissions_data = {}
    emissions_total = {}
    production = {}
    productiondetails = {}
    imports = {}
    for city in cities:

        # Get the consumption details as well as total to calculate OTHER category
        consumption_data[city.id] = per_capita_breakdown(Data.objects.filter(city=city, sankey=True, target__name="Consumption"), {"topten": True})
        consumption_total[city.id] = per_capita_total(Data.objects.filter(city=city, sankey=True, target__name="Consumption"))

        # Get total imports
        imports[city.id] = per_capita_total(Data.objects.filter(city=city, sankey=True, source__name="Imports"))

        # For production get the total figure, but also get the top 10 items
        production[city.id] = per_capita_total(Data.objects.filter(city=city, sankey=True, source__name="Production"))
        production_data = Data.objects.filter(city=city, sankey=True, source__name="Production")
        if production_data:
            production_data = production_data.order_by("-quantity")[:10]
        productiondetails[city.id] = production_data

        emissions_data[city.id] = per_capita_breakdown(Data.objects.filter(city=city, sankey=True, target__name="Consumption"), {"topten": True, "impact": "emissions"})
        emissions_total[city.id] = per_capita_impact(Data.objects.filter(city=city, sankey=True, target__name="Consumption"), "emissions")

    context = {
        "cities": cities,
        "menu": "data",
        "submenu": "homepage",
        "consumption_data": consumption_data,
        "consumption_total": consumption_total,
        "emissions_data": emissions_data,
        "emissions_total": emissions_total,
        "production": production,
        "productiondetails": productiondetails,
        "imports": imports,
        "echarts": True,
        "columns": math.floor(12/cities.count()),
        "table_bars": True,
    }

    return render(request, "data/index.html", context)

@login_required
def data_city(request, id=None):

    if "cities" in request.GET:
        return redirect("data_city", request.GET["cities"])
    elif not id:
        id = 1
    city = City.objects.get(is_active=True, pk=id)

    foodsupply = per_capita_breakdown(Data.objects.filter(city=city, sankey=True, target__name="Food supply"), {"topten": True})
    foodsupply_exit = per_capita_breakdown(Data.objects.filter(city=city, sankey=True, source__name="Food supply"), {"topten": True})
    consumption = per_capita_breakdown(Data.objects.filter(city=city, sankey=True, target__name="Consumption"), {"topten": True})

    context = {
        "city": city,
        "menu": "data",
        "submenu": "city",
        "production": Data.objects.filter(sankey=True, city=city, source__name="Production").order_by("-quantity"),
        "imports": Data.objects.filter(sankey=True, city=city, source__name="Imports").order_by("-quantity"),
        "table_bars": True,
        "echarts": True,
        "foodsupply": foodsupply,
        "foodsupply_exit": foodsupply_exit,
        "foodsupply_total": per_capita_total(Data.objects.filter(city=city, sankey=True, target__name="Food supply")),
        "foodsupply_exit_total": per_capita_total(Data.objects.filter(city=city, sankey=True, source__name="Food supply")),
        "consumption": consumption,
        "consumption_total": per_capita_total(Data.objects.filter(city=city, sankey=True, target__name="Consumption")),
    }

    return render(request, "data/city.html", context)

@login_required
def consumption(request, page="index"):

    cities = get_cities(request)
    data = per_capita_breakdown(Data.objects.filter(city__in=cities, sankey=True, target__name="Consumption"), {"include_city": True})

    # We create defaultdicts so we don't have to manually create all the dictionaries
    totals = defaultdict(dict)
    per_capita = defaultdict(dict)

    for each in data:
        totals[each["city_id"]][each["food_group__name"]] = each["total"]
        per_capita[each["city_id"]][each["food_group__name"]] = each["per_capita"]

    context = {
        "cities": cities,
        "menu": "data",
        "submenu": "consumption",
        "page": page,
        "table_bars": True,
        "foodgroups": FoodGroup.objects.filter(is_human_food=True),
        "totals": totals,
        "per_capita": per_capita,
        "echarts": True,
    }

    return render(request, f"data/consumption.{page}.html", context)

@login_required
def impact(request, page="index", impact_type="emissions"):

    if page == "table" and request.GET.get("impact_type"):
        impact_type = request.GET.get("impact_type")

    get_sample_city = False
    if "sample_city" in request.GET and request.GET.get("sample_city"):
        get_sample_city = True
    cities = get_cities(request, get_sample_city)

    emissions_data = per_capita_breakdown(Data.objects.filter(city__in=cities, sankey=True, target__name="Consumption"), {"impact": impact_type, "include_city": True})

    # We create defaultdicts so we don't have to manually create all the dictionaries
    totals = defaultdict(dict)
    per_capita = defaultdict(dict)
    totals_impact = defaultdict(dict)

    for each in emissions_data:
        totals[each["city_id"]][each["food_group__name"]] = each["total"]
        totals_impact[each["city_id"]][each["food_group__name"]] = each["total_impact"]
        per_capita[each["city_id"]][each["food_group__name"]] = each["per_capita"]

    impact_types = {
        "emissions": {"title": "GHG emissions", "unit": "kg CO2eq", "unit_10k": "t CO2eq"},
        "land_use": {"title": "Land use", "unit": "m3", "unit_10k": "ha"},
        "water_use": {"title": "Freshwater withdrawals", "unit": "l", "unit_10k": "kl"},
    }

    context = {
        "cities": cities,
        "menu": "data",
        "submenu": "impact",
        "page": impact_type if page == "chart" else page,
        "table_bars": True,
        "foodgroups": FoodGroup.objects.filter(is_human_food=True),
        "totals": totals,
        "totals_impact": totals_impact,
        "per_capita": per_capita,
        "echarts": True,
        "impact_types": impact_types,
        "impact_type": impact_types[impact_type],
    }

    return render(request, f"data/impact.{page}.html", context)

@login_required
def data_table(request):

    cities = get_cities(request)
    data = Data.objects.filter(city__in=cities)

    if request.GET.get("sankey"):
        data = data.filter(sankey=True)

    if request.GET.get("foodgroups"):
        data = data.filter(food_group__in=request.GET.getlist("foodgroups"))

    if request.GET.get("activity"):
        activity = Activity.objects.get(name=request.GET["activity"])
        if request.GET["type"] == "target":
            data = data.filter(target=activity)
        elif request.GET["type"] == "source":
            data = data.filter(source=activity)
        else:
            messages.warning("You did not specify source/target filter, please add this filter.")

    if "food_name" in request.GET and request.GET["food_name"]:
        data = data.filter(food=request.GET.get("food_name"))

    data = data.annotate(population=Subquery(POPULATION.values("population")[:1]))
    data = data.annotate(per_capita=ExpressionWrapper(
        F("quantity") * 1000.0 / F("population"),
        output_field=FloatField()
    ))

    context = {
        "cities": cities,
        "foodgroups": FoodGroup.objects.all(),
        "activities": Activity.objects.all(),
        "data": data,
        "disable_city_picker": True,
        "menu": "data",
        "submenu": "data_table",
    }

    return render(request, "data/table.html", context)

@login_required
def production(request, page="table"):

    cities = get_cities(request)
    production = Data.objects.filter(city__in=cities, sankey=True, source__name="Production") \
        .values("food_group", "year", "city").annotate(Sum("quantity")).annotate(population=Subquery(POPULATION.values("population")[:1])).order_by()

    totals = {}
    per_capita = {}
    for city in cities:
        per_capita[city.id] = {}
        totals[city.id] = {}

    errors = []

    for each in production:
        quantity = each["quantity__sum"]
        foodgroup = each["food_group"]
        population = each["population"]
        city = each["city"]
        if population:
            totals[city][foodgroup] = quantity
            per_capita[city][foodgroup] = quantity/population*1000 #kg instead of t
        else:
            totals[city][foodgroup] = 0
            per_capita[city][foodgroup] = 0
            e = f"Not all population data is available - incomplete data for city #{city}. Removing this city from the list..."
            if e not in errors:
                errors.append(e)
            cities = cities.exclude(pk=city)

    if errors:
        for each in errors:
            messages.warning(request, each)

    context = {
        "totals": totals,
        "per_capita": per_capita,
        "cities": cities,
        "menu": "data",
        "submenu": "production",
        "page": page,
        "foodgroups": FoodGroup.objects.all(),
        "google_charts": False if page == "table" else True,
    }

    return render(request, f"data/production.{page}.html", context)

@login_required
def production_overview(request):

    cities = get_cities(request)

    production = Data.objects.filter(sankey=True, city__in=cities, source__name="Production") \
        .filter(quantity__gt=0) \
        .annotate(population=Subquery(POPULATION.values("population")[:1]))

    totals = {}
    per_capita = {}
    colors = {}
    for city in cities:
        per_capita[city.id] = {}
        totals[city.id] = {}

    errors = []

    for each in production:
        quantity = each.quantity
        foodgroup = each.food_group.name
        food = each.food
        population = each.population
        city = each.city.id
        if foodgroup not in totals[city]:
            totals[city][foodgroup] = {}
            per_capita[city][foodgroup] = {}
            colors[foodgroup] = each.food_group.color
        if population:
            totals[city][foodgroup][food] = quantity
            per_capita[city][foodgroup][food] = quantity/population*1000 #kg instead of t
        else:
            totals[city][foodgroup] = 0
            per_capita[city][foodgroup] = 0
            e = f"Not all population data is available - incomplete data for city #{city}. Removing this city from the list..."
            if e not in errors:
                errors.append(e)
            cities = cities.exclude(pk=city)

    if errors:
        for each in errors:
            messages.warning(request, each)

    context = {
        "totals": totals,
        "per_capita": per_capita,
        "cities": cities,
        "menu": "data",
        "submenu": "production",
        "page": "overview",
        "foodgroups": FoodGroup.objects.all(),
        "colors": colors,
        "echarts": True,
    }

    return render(request, f"data/production.overview.html", context)

@login_required
def data_dqi(request):

    cities = get_cities(request)
    ratings = defaultdict(dict)

    for each in cities:
        ratings[each.id] = defaultdict(dict)

    for each in DataQualityIndicator.objects.filter(data__city__in=cities):
        ratings[each.data.city.id][each.indicator.indicator.name][each.data.activity.name] = each.indicator

    context = {
        "cities": cities,
        "menu": "data",
        "submenu": "dqi",
        "indicators": Indicator.objects.all(),
        "ratings": ratings,
        "activities": Activity.objects.all(),
    }

    return render(request, f"data/dqi.html", context)


@login_required
def ideal_diet(request, page="table"):

    cities = get_cities(request)

    consumption = Data.objects.filter(city__in=cities, sankey=True, target__name="Consumption") \
        .values("food_group", "year", "city").annotate(Sum("quantity")).annotate(population=Subquery(POPULATION.values("population")[:1])).order_by()

    ideal = IdealConsumption.objects.all()

    grouptotals = {}
    percentage = {}  
    totals = {}
    for city in cities:
        grouptotals[city.id] = {}
        percentage[city.id] = {}
        totals[city.id] = {}

    errors = []

    for each in consumption:
        quantity = each["quantity__sum"]
        foodgroup = each["food_group"]
        population = each["population"]
        city = each["city"]
        if population:
            totals[city][foodgroup] = quantity/population*1000*1000/365 # from t per year to g per day
        else:
            totals[city][foodgroup] = 0
            e = f"Not all population data is available - incomplete data for city #{city}. Removing this city from the list..."
            if e not in errors:
                errors.append(e)
            cities = cities.exclude(pk=city)

    if errors:
        for each in errors:
            messages.warning(request, each)

    ideals = {} # A dictionary with all the ideal values (ID + quantity)
    for each in ideal:
        ideals[each.id] = each.quantity
        for city in cities:
            grouptotals[city.id][each.id] = 0
            for group in each.foodgroups.all():
                if group.id in totals[city.id]:
                    grouptotals[city.id][each.id] += totals[city.id][group.id]
            if each.quantity:
                if page == "barchart" or page == "barchartgrouped":
                    # For the bar charts we want to know consumption as a % of ideal consumption
                    percentage[city.id][each.id] = ((grouptotals[city.id][each.id]/each.quantity)*100)
                else:
                    # For the table etc we just want to know how many % this is higher or lower
                    percentage[city.id][each.id] = ((grouptotals[city.id][each.id]/each.quantity)*100)-100

    if page == "barchart" or page == "barchartgrouped":
        # We calculate the value as a % of the target value. That doesn't work if the target value is 0 so we remove them.
        ideal = ideal.filter(quantity__gt=0)

    context = {
        "ideal": ideal,
        "totals": grouptotals,
        "percentage": percentage,
        "cities": cities,
        "menu": "data",
        "submenu": "idealdiet",
        "page": page,
        "google_charts": False if page == "table" else True,
        "ideals": ideals,
        "echarts": True if page == "barchart" or page == "barchartgrouped" else False,
    }

    return render(request, f"data/diet.{page}.html", context)

@login_required
def chart(request):

    context = {
        "menu": "index",
        "google_charts": True,
    }

    return render(request, "chart.html", context)


# 
#
#  CONTROL PANEL
#
#

@login_required
def controlpanel(request):
    context = {
        "controlpanel": True,
        "cities": City.objects.all(),
    }

    return render(request, "controlpanel/index.html", context)

@login_required
def controlpanel_city(request, id):
    city = City.objects.get(pk=id)

    if request.method == "POST":

        if request.FILES.get("file"):
            file = DataFile.objects.create(
                file = request.FILES.get("file"),
                original_name = request.FILES['file'].name,
                description = request.POST.get("description"),
                city = city,
                user = request.user,
            )
            messages.success(request, "Your spreadsheet has been uploaded. Please see below the data review of this file.")
            return redirect("controlpanel_file", id=file.id)

        elif request.POST.get("population"):
            Population.objects.create(
                population = request.POST.get("population"),
                year = request.POST.get("year"),
                city = city,
                source = request.POST.get("source"),
            )
            messages.success(request, "Population data was saved.")
            return redirect(request.get_full_path())

    if "delete_population" in request.GET:
        Population.objects.get(pk=request.GET["delete_population"]).delete()
        messages.success(request, "Population data was deleted.")
        return redirect("controlpanel_city", id=city.id)

    context = {
        "controlpanel": True,
        "city": city,
        "files": DataFile.objects.filter(city_id=id).order_by("status"),
        "population": Population.objects.filter(city_id=id),
        "descriptions": DataDescription.objects.filter(city_id=id),
    }

    return render(request, "controlpanel/city.html", context)

@login_required
def controlpanel_file(request, id):
    file = DataFile.objects.get(pk=id)

    try:
        df = pd.read_excel(file.file)
        df.dropna(how="all", inplace = True)
        column_count = len(df.columns)
        errors = []
        info = {}
        info["columns"] = column_count
        info["origins"] = df["Origin"].unique()
        info["destinations"] = df["Destination"].unique()
        info["groups"] = df["Food group"].unique()

        if column_count != 9:
            errors.append("The number of columns is " + str(column_count) + ". However, we expect 9 columns. Please review.")
    except Exception as e:
        errors.append("There was a problem reading and interpreting the file. This is the error: " + str(e))

    empty_food_names = df[df["Food name"].isna()]
    if len(empty_food_names.index):
        errors.append("Not all rows have a 'food name' value. This value is required - please add it for the missing rows, shown below:")
        errors.append(mark_safe(empty_food_names.to_html(index=False, justify="left", classes="table")))

    activities = {}
    for each in Activity.objects.all():
        activities[each.name] = each.id

    groups = {}
    for each in FoodGroup.objects.all():
        groups[each.name] = each.id

    if "delete" in request.POST:
        city_id = int(file.city.id)
        file.status = "deleted"
        file.save()
        messages.success(request, "The spreadsheet has been deleted.")
        return redirect("controlpanel_city", id=city_id)

    if "delete-data" in request.POST:
        file.status = "pending"
        file.save()
        Data.objects.filter(city=file.city).delete()
        messages.success(request, "Data has removed from the database. You can re-import or remove the file below.")
        return redirect(request.get_full_path())

    if "save" in request.POST:
        a = DataFile.objects.filter(status="imported", city=file.city)
        a.update(status="superseded")

        file.status = "imported"
        file.save()

        items = []

        i = 2 # Skip the header row
        df = df.replace(np.nan, None) # We want None instead of NaN 
        for row in df.itertuples():
            i += 1
            origin = row[1]
            destination = row[2]
            food = row[3]
            foodgroup = row[4]
            year = row[5]
            quantity = row[6]
            location = row[7]
            segment = row[8]
            sankey = row[9]

            try:
                items.append(Data(
                    source_id = activities[origin],
                    target_id = activities[destination],
                    food = food,
                    food_group_id = groups[foodgroup],
                    year = year,
                    quantity = quantity,
                    location = location,
                    segment = segment,
                    sankey = True if sankey.lower() == "yes" or sankey == True else False,
                    city = file.city,
                    file = file,
                ))
            except Exception as e:
                errors.append(f"We were unable to add row {i}. This is the error that came back: {e} is invalid.")

        if not errors:
            Data.objects.filter(city=file.city).delete()
            try:
                Data.objects.bulk_create(items)
                messages.success(request, "The data have been saved in the database. Previous data was overwritten.")
                return redirect("controlpanel_city", id=file.city.id)
            except Exception as e:
                errors.append(f"We were unable to save the data. This is the error that came back: {e}")


    context = {
        "controlpanel": True,
        "file": file,
        "errors": errors,
        "info": info,
        "df": df,
        "activities": activities,
        "groups": groups,
    }

    return render(request, "controlpanel/file.html", context)

@login_required
def controlpanel_datadescription(request, city, id=None):

    info = None
    if id:
        info = DataDescription.objects.get(pk=id)

    indicators = Indicator.objects.all()
    dqi = DataQualityIndicator.objects.filter(data=info)

    ratings = []
    descriptions = {}
    for each in dqi:
        ratings.append(each.indicator_id)
        descriptions[each.indicator.indicator.id] = each.description

    if request.method == "POST":
        if not info:
            info = DataDescription()
        info.description = request.POST.get("description")
        info.activity_id = request.POST.get("activity")
        info.city_id = city
        info.save()

        dqi.delete()
        for each in indicators:
            label = "rating_" + str(each.id)
            rating = request.POST.get(label)
            if rating:
                DataQualityIndicator.objects.create(
                    indicator_id = rating,
                    data = info,
                    description = request.POST.get("description_" + str(each.id))
                )

        messages.success(request, "Your data description has been saved.")
        return redirect("controlpanel_city", id=city)

    context = {
        "controlpanel": True,
        "city": City.objects.get(pk=city),
        "info": info,
        "activities": Activity.objects.all(),
        "indicators": indicators,
        "ratings": ratings,
        "descriptions": descriptions,
    }

    return render(request, "controlpanel/datadescription.html", context)

@login_required
def controlpanel_activities(request):
    context = {
        "controlpanel": True,
        "activities": Activity.objects.all(),
    }

    return render(request, "controlpanel/activities.html", context)

@login_required
def controlpanel_foodgroups(request):
    context = {
        "controlpanel": True,
        "foodgroups": FoodGroup.objects.all(),
    }

    return render(request, "controlpanel/foodgroups.html", context)
