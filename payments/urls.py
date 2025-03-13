from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, AccountViewSet, BankProviderViewSet, MassPaymentViewSet
from payments import views


router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'accounts', AccountViewSet)
router.register(r'bank-providers', BankProviderViewSet)
router.register(r'mass-payments', MassPaymentViewSet)
router.register(r'payment-templates', views.PaymentTemplateViewSet)


urlpatterns = [
    path('', include(router.urls)),
]