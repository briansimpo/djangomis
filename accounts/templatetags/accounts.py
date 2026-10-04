from django import template
from djangospice.urls import safe_reverse
register = template.Library()


@register.filter(name='add_class')
def add_class(field, css):
    return field.as_widget(attrs={"class": css})


@register.simple_tag(takes_context=True)
def redirection_url(context):
    user = context.get("user")

    if user and user.is_authenticated:
        return safe_reverse("account_redirect")

    return safe_reverse("home")