from website.models import City

def site(request):
    
    context = {
        "CITIES": City.objects.all(),
    }
    
    return context
