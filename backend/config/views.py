from django.http import JsonResponse

def test_api(request):
    return JsonResponse({
        "success": True,
        "message": "Resume Screening System API is working!",
        "project": "Growth For Impact",
    })