from website.models import City

def site(request):
    
    context = {
        "CITIES": City.objects.filter(is_active=True),
    }
    
    return context
