from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'Transaction', views.TransactionViewSet)
router.register(r'Profile', views.ProfileViewSet)
router.register(r'User', views.UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]