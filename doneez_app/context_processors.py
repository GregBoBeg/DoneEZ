from doneez_app.models import BusinessType

def business_solutions_processor(request):
    business_solutions = BusinessType.objects.filter(b2b="SOLUTION").order_by('business_type',)
    return {'business_solutions': business_solutions}