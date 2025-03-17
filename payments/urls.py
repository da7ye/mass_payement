from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.views import UserViewSet, AccountViewSet, BankProviderViewSet
from .views.mass_payments_views import MassPaymentViewSet
from .views.payment_template_views import PaymentTemplateViewSet
from .views.group_recipiants_views import RecipientGroupViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'accounts', AccountViewSet)
router.register(r'bank-providers', BankProviderViewSet)
router.register(r'mass-payments', MassPaymentViewSet)
router.register(r'payment-templates', PaymentTemplateViewSet)
router.register(r'recipient-groups', RecipientGroupViewSet)


urlpatterns = [
    path('', include(router.urls)),
]