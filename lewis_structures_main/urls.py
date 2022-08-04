from django.urls import include, path
from rest_framework import routers
from lewis_structures_main import views

# router = routers.DefaultRouter()
# router.register(r"molecules", views.MoleculeViewSet)

urlpatterns = [
    # path("", include(router.urls)),
    path('api/', views.index, name='index'),
    path('molecules/', views.get_molecule_list, name="molecule_list"),
    path('molecules/<int:id>', views.get_molecule_by_id, name="molecule")
]