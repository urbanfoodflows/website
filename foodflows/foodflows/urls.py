from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from website.admin import admin_site  

urlpatterns = [
    path("", include("website.urls")),
    path("admin/", admin_site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
