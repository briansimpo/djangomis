from django.core.exceptions import ValidationError
from django.http import HttpRequest

from apps.calendar.models import CalendarPeriod
from apps.organization.models import OrgUnit
from apps.workforce.helpers import get_user_org_unit


class WorkspaceContextService:
    """
    Manage a user's active organization unit and calendar period.

    Responsibilities:
    - Resolve accessible organization units.
    - Validate organization-unit access.
    - Resolve calendar periods within an organization unit.
    - Read requested and session selections.
    - Persist, resolve, and clear the active context.
    """

    ORG_UNIT_ID_KEY = "org_unit_id"
    CALENDAR_PERIOD_ID_KEY = "calendar_period_id"

    # ------------------------------------------------------------------
    # Organization Unit
    # ------------------------------------------------------------------

    @classmethod
    def get_org_unit(cls, org_unit_id):
        """Return an organization unit by ID, or None."""
        if not org_unit_id:
            return None

        try:
            return OrgUnit.objects.filter(pk=org_unit_id).first()
        except (ValidationError, ValueError, TypeError):
            return None

    @classmethod
    def get_user_org_units(cls, user):
        """Return the organization units accessible to a user."""
        if not user.is_authenticated:
            return []

        if user.is_superuser:
            return list(OrgUnit.objects.all().order_by("level"))

        org_units = get_user_org_unit(user)

        if org_units is None:
            return []

        if isinstance(org_units, OrgUnit):
            return [org_units]

        return list(org_units)

    @classmethod
    def user_belongs_to_org_unit(cls, user, org_unit_id):
        """Check whether a user belongs to an organization unit."""
        if not user.is_authenticated or not org_unit_id:
            return False

        return any(
            str(org_unit.pk) == str(org_unit_id)
            for org_unit in cls.get_user_org_units(user)
        )

    @classmethod
    def can_access_org_unit(cls, user, org_unit):
        """Check whether a user can access an organization unit."""
        if not user.is_authenticated or org_unit is None:
            return False

        return (
            user.is_superuser
            or cls.user_belongs_to_org_unit(user, org_unit.pk)
        )

    # ------------------------------------------------------------------
    # Calendar Period
    # ------------------------------------------------------------------

    @classmethod
    def get_calendar_period(cls, calendar_period_id):
        """Return a calendar period by ID, or None."""
        if not calendar_period_id:
            return None

        try:
            return CalendarPeriod.objects.filter(
                pk=calendar_period_id,
            ).first()
        except (ValidationError, ValueError, TypeError):
            return None

    @classmethod
    def get_open_calendar_period(cls, org_unit_id):
        """Return the open calendar period for an organization unit."""
        if not org_unit_id:
            return None

        return CalendarPeriod.objects.filter(
            org_unit_id=org_unit_id,
            is_open=True,
        ).first()

    @classmethod
    def get_calendar_periods(cls, org_unit_id):
        """Return calendar periods scoped to an organization unit."""
        if not org_unit_id:
            return CalendarPeriod.objects.none()

        return CalendarPeriod.objects.filter(
            org_unit_id=org_unit_id,
        ).order_by("-start_day")

    @classmethod
    def get_org_unit_calendar_period(
        cls,
        calendar_period_id,
        org_unit_id,
    ):
        """Return a period only if it belongs to the specified unit."""
        if not calendar_period_id or not org_unit_id:
            return None

        try:
            return CalendarPeriod.objects.filter(
                pk=calendar_period_id,
                org_unit_id=org_unit_id,
            ).first()
        except (ValidationError, ValueError, TypeError):
            return None

    # ------------------------------------------------------------------
    # Request: Organization Unit
    # ------------------------------------------------------------------

    @classmethod
    def get_requested_org_unit_id(cls, request: HttpRequest):
        return request.POST.get(cls.ORG_UNIT_ID_KEY)

    @classmethod
    def get_requested_org_unit(cls, request: HttpRequest):
        return cls.get_org_unit(
            cls.get_requested_org_unit_id(request)
        )

    # ------------------------------------------------------------------
    # Request: Calendar Period
    # ------------------------------------------------------------------

    @classmethod
    def get_requested_calendar_period_id(cls, request: HttpRequest):
        return request.POST.get(cls.CALENDAR_PERIOD_ID_KEY)

    @classmethod
    def get_requested_calendar_period(cls, request: HttpRequest):
        return cls.get_calendar_period(
            cls.get_requested_calendar_period_id(request)
        )

    # ------------------------------------------------------------------
    # Session: Organization Unit
    # ------------------------------------------------------------------

    @classmethod
    def get_session_org_unit_id(cls, request: HttpRequest):
        return request.session.get(cls.ORG_UNIT_ID_KEY)

    @classmethod
    def get_session_org_unit(cls, request: HttpRequest):
        return cls.get_org_unit(
            cls.get_session_org_unit_id(request)
        )

    @classmethod
    def set_session_org_unit_id(cls, request: HttpRequest, org_unit_id):
        request.session[cls.ORG_UNIT_ID_KEY] = str(org_unit_id)

    @classmethod
    def clear_session_org_unit_id(cls, request: HttpRequest):
        request.session.pop(cls.ORG_UNIT_ID_KEY, None)

    # ------------------------------------------------------------------
    # Session: Calendar Period
    # ------------------------------------------------------------------

    @classmethod
    def get_session_calendar_period_id(cls, request: HttpRequest):
        return request.session.get(cls.CALENDAR_PERIOD_ID_KEY)

    @classmethod
    def get_session_calendar_period(cls, request: HttpRequest):
        return cls.get_calendar_period(
            cls.get_session_calendar_period_id(request)
        )

    @classmethod
    def set_session_calendar_period_id(
        cls,
        request: HttpRequest,
        calendar_period_id,
    ):
        request.session[cls.CALENDAR_PERIOD_ID_KEY] = str(
            calendar_period_id
        )

    @classmethod
    def clear_session_calendar_period_id(cls, request: HttpRequest):
        request.session.pop(cls.CALENDAR_PERIOD_ID_KEY, None)

    # ------------------------------------------------------------------
    # Combined Session Context
    # ------------------------------------------------------------------

    @classmethod
    def clear_session_selection(cls, request: HttpRequest):
        """Clear both selections."""
        cls.clear_session_calendar_period_id(request)
        cls.clear_session_org_unit_id(request)

    @classmethod
    def set_session_selection(
        cls,
        request: HttpRequest,
        org_unit: OrgUnit,
        calendar_period: CalendarPeriod | None = None,
    ):
        """
        Set the active organization unit and calendar period.

        Resolve the open period when no period is supplied.
        """
        if calendar_period is None:
            calendar_period = cls.get_open_calendar_period(
                org_unit.pk
            )
        elif calendar_period.org_unit_id != org_unit.pk:
            raise ValueError(
                "The calendar period does not belong to "
                "the selected organization unit."
            )

        cls.set_session_org_unit_id(request, org_unit.pk)

        if calendar_period is not None:
            cls.set_session_calendar_period_id(
                request,
                calendar_period.pk,
            )
        else:
            cls.clear_session_calendar_period_id(request)

    @classmethod
    def get_session_selection(cls, request: HttpRequest):
        """
        Return (org_unit, calendar_period).

        The period is returned only if it belongs to the
        organization unit stored in the session.
        """
        org_unit = cls.get_session_org_unit(request)

        if org_unit is None:
            return None, None

        calendar_period = cls.get_org_unit_calendar_period(
            cls.get_session_calendar_period_id(request),
            org_unit.pk,
        )

        return org_unit, calendar_period

    # ------------------------------------------------------------------
    # Context Resolution
    # ------------------------------------------------------------------

    @classmethod
    def resolve_user_selection(
        cls,
        request: HttpRequest,
        user,
        org_unit_id=None,
        calendar_period_id=None,
    ):
        """
        Validate and persist the active user context.

        Raises ValueError for invalid or unauthorized selections.
        """
        if not org_unit_id:
            cls.clear_session_selection(request)
            return None, None

        org_unit = cls.get_org_unit(org_unit_id)

        if org_unit is None:
            raise ValueError("Invalid organization unit.")

        if not cls.can_access_org_unit(user, org_unit):
            raise ValueError(
                "You do not have access to this organization unit."
            )

        if calendar_period_id:
            calendar_period = cls.get_org_unit_calendar_period(
                calendar_period_id,
                org_unit.pk,
            )

            if calendar_period is None:
                raise ValueError(
                    "The calendar period does not belong to "
                    "the selected organization unit."
                )
        else:
            calendar_period = cls.get_open_calendar_period(
                org_unit.pk
            )

        cls.set_session_selection(
            request,
            org_unit,
            calendar_period,
        )

        return org_unit, calendar_period