from django.shortcuts import render
from .models import *
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
import pandas as pd
import numpy as np

# Quick debugging, sometimes it's tricky to locate the PRINT in all the Django
# output in the console, so just using a simply function to highlight it better
def p(text):
    print("----------------------")
    print(text)
    print("----------------------")

@login_required
def index(request):
    context = {
        "menu": "index",
    }

    return render(request, "index.html", context)

@login_required
def city(request, id):
    context = {
        "info": City.objects.get(pk=id),
        "descriptions": DataDescription.objects.filter(city_id=id),
    }

    return render(request, "city.html", context)

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

    if request.method == "POST":
        if not info:
            info = DataDescription()
        info.description = request.POST.get("description")
        info.activity_id = request.POST.get("activity")
        info.city_id = city
        info.save()
        messages.success(request, "Your data description has been saved.")
        return redirect("controlpanel_city", id=city)

    context = {
        "city": City.objects.get(pk=city),
        "info": info,
        "activities": Activity.objects.all(),
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
