from django.urls import path

from .views import IndexView, ContactView


urlpatterns = [
    path('contacto/',
        ContactView.as_view(), name='vss_landing_contact'),
    
    path('', IndexView.as_view(), name='vss_landing_index'),
]