from djangospice.rest.router import router
from apps.users.api.views import  GroupViewSet, UserViewSet

router.register_viewset(UserViewSet, basename="user")
router.register_viewset(GroupViewSet, basename="group")
