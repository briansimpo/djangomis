from .models import Company


def org_metadata(request):
    org = Company.objects.first()
    return {"org": org}

