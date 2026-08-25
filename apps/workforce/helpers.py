from apps.workforce.resolvers.workforce_context import WorkforceContext

def get_user_org_unit(user):
    user_org_unit = WorkforceContext.get_user_org_unit(user)
    return user_org_unit
