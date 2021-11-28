from django.urls import path, include

from .views import TxOutDetailView, TxOutListView, ActorListView

urlpatterns = [
    path('<int:pk>/', TxOutDetailView.as_view(), name="txout_detail"),
    path('actors/', ActorListView.as_view(), name="actor_list"),
    path('', TxOutListView.as_view(), name="txout_list"),
]
