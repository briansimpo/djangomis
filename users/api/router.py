from djangospice_api.router import router
from users.api.views import  GroupViewSet, UserViewSet

router.register_viewset(UserViewSet, basename="user")
router.register_viewset(GroupViewSet, basename="group")
