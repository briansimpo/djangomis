from functools import wraps
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect
from djangospice.routing import safe_reverse


def _require_access(view_func, *, allow_authenticated: bool, allow_staff: bool = False, allow_client: bool = False, allow_guest: bool = False, json_only: bool = False):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        user = request.user

        # Guest (anonymous)
        if not user.is_authenticated:
            if allow_authenticated:
                return view_func(request, *args, **kwargs)

            if json_only:
                return JsonResponse({"detail": "Authentication required"}, status=401)
            return redirect(safe_reverse("account_login"))

        # Staff
        if allow_staff and getattr(user, "is_staff", False):
            return view_func(request, *args, **kwargs)

        # Student
        if allow_client and (
            getattr(user, "is_client", False)
            or getattr(user, "role", None) == "client"
        ):
            return view_func(request, *args, **kwargs)

        # Applicant
        if allow_guest and (
            getattr(user, "is_guest", False)
            or getattr(user, "role", None) == "guest"
        ):
            return view_func(request, *args, **kwargs)

        # Authenticated but not allowed
        if json_only:
            return JsonResponse({"detail": "Forbidden"}, status=403)
        return HttpResponseForbidden()

    return _wrapped


def staff_required(view_func, *, json_only=False):
    return _require_access(
        view_func,
        allow_authenticated=False,
        allow_staff=True,
        json_only=json_only,
    )


def client_required(view_func, *, json_only=False):
    return _require_access(
        view_func,
        allow_authenticated=False,
        allow_client=True,
        json_only=json_only,
    )


def guest_required(view_func, *, json_only=False):
    return _require_access(
        view_func,
        allow_authenticated=False,
        allow_guest=True,
        json_only=json_only,
    )


def authenticated_required(view_func, *, json_only=False):
    return _require_access(
        view_func,
        allow_authenticated=False,
        allow_staff=True,
        allow_client=True,
        json_only=json_only,
    )


