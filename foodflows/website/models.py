from django.db import models
from markdown import markdown
from django.utils.safestring import mark_safe
from mdeditor.fields import MDTextField
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
User = get_user_model()

class City(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="cities/", max_length=255, null=True, blank=True)
    description = MDTextField(null=True, blank=True)
    dashboard_link = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(db_index=True, default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        db_table = "cities"
        verbose_name_plural = "Cities"

    @property
    def get_description(self):
        if self.description:
            return mark_safe(markdown(self.description))
        else:
            return None

    def get_file(self):
        file = DataFile.objects.filter(status="imported", city=self)
        if file:
            return file[0]
        else:
            return None

class Population(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    year = models.PositiveSmallIntegerField()
    population = models.IntegerField()
    source = models.TextField()

    class Meta:
        db_table = "population"

class FoodGroup(models.Model):
    name = models.CharField(max_length=255)
    description = MDTextField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        db_table = "foodgroups"

class Activity(models.Model):
    name = models.CharField(max_length=255)
    description = MDTextField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        db_table = "activities"
        verbose_name_plural = "Activities"

class DataFile(models.Model):
    file = models.FileField(upload_to="files/", max_length=255)
    original_name = models.CharField(max_length=255)
    description = MDTextField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    STATUS = (
        ("pending", "Pending"),
        ("imported", "Imported"),
        ("superseded", "Superseded"),
        ("deleted", "Deleted"),
    )
    status = models.CharField(max_length=20, choices=STATUS, default="pending")

    def __str__(self):
        return self.file.name

    class Meta:
        db_table = "files"
        ordering = ["date"]

class Data(models.Model):
    source = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="data_from")
    target = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name="data_to")
    food = models.CharField(max_length=255)
    food_group = models.ForeignKey(FoodGroup, on_delete=models.CASCADE)
    year = models.PositiveSmallIntegerField()
    quantity = models.PositiveBigIntegerField()
    location = models.CharField(max_length=255, null=True, blank=True)
    segment = models.CharField(max_length=255, null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    sankey = models.BooleanField(db_index=True)
    file = models.ForeignKey(DataFile, on_delete=models.CASCADE, null=True, blank=True, related_name="data")

    class Meta:
        db_table = "foodflows"
        verbose_name_plural = "Data"

class Page(models.Model):
    title = models.CharField(max_length=255)
    content = MDTextField(null=True, blank=True)
    slug = models.SlugField(max_length=100, null=True, blank=True, unique=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["title"]
        db_table = "pages"

class DataDescription(models.Model):
    description = MDTextField(null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)

    def __str__(self):
        return self.activity.name

    @property
    def get_description(self):
        if self.description:
            return mark_safe(markdown(self.description))
        else:
            return None

    class Meta:
        ordering = ["activity__name"]
        db_table = "data_descriptions"

class Indicator(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["id"]
        db_table = "indicators"

class IndicatorDescription(models.Model):
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE, related_name="ratings")
    rating = models.PositiveSmallIntegerField()
    description = models.TextField()

    def __str__(self):
        return f"{self.indicator} - {self.rating}"

    @property
    def color(self):
        colors = {
            1: "#3e940e",
            2: "#d6c521",
            3: "#eab31d",
            4: "#f0790d",
            5: "#e23a3a",
        }
        return colors[self.rating]

    class Meta:
        ordering = ["indicator", "rating"]
        db_table = "indicator_descriptions"

class DataQualityIndicator(models.Model):
    indicator = models.ForeignKey(IndicatorDescription, on_delete=models.CASCADE)
    data = models.ForeignKey(DataDescription, on_delete=models.CASCADE, related_name="ratings")
    description = models.TextField(null=True)

    def __str__(self):
        return f"{self.indicator} for {self.data}"

    class Meta:
        ordering = ["indicator_id", "indicator__rating"]
        db_table = "data_quality_indicators"
