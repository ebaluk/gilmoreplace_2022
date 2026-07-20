from django.template.response import TemplateResponse

def preview404(request):
    return TemplateResponse(request, "404.html")
    
    
