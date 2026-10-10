from django.shortcuts import render

from .forms import AcademicContextForm


def academic_context(request):
    if request.method == "POST":
        form = AcademicContextForm(request.POST)

        if form.is_valid():
            org_unit = form.cleaned_data["org_unit"]
            calendar_period = form.cleaned_data["calendar_period"]

            # Continue with your application logic.
            #
            # For example:
            # request.session["org_unit_id"] = str(org_unit.pk)
            # request.session["calendar_period_id"] = str(calendar_period.pk)

            return render(
                request,
                "calendar/context_success.html",
                {
                    "org_unit": org_unit,
                    "calendar_period": calendar_period,
                },
            )
    else:
        form = AcademicContextForm()

    return render(
        request,
        "calendar/context_form.html",
        {
            "form": form,
        },
    )