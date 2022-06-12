from django.urls import path, include

from .views import (
        TxOutDetailView,
        TxOutListView,
        TxOutCreateView,
        TxOutUpdateView,
        TxOutDeleteView,
        ActorDetailView,
        ActorListView,
        ActorCreateView,
        ActorUpdateView,
        ActorDeleteView,
        tx_lookup,
        txout_detail_json,
        txout_backup_json,
    )

urlpatterns = [
    path('<int:pk>/', TxOutDetailView.as_view(), name="txout_detail"),
    path('api/<int:pk>/', txout_detail_json, name="txout_detail_json"),
    path('api/backup/', txout_backup_json, name="txout_backup_json"),
    path('new/', TxOutCreateView.as_view(), name="txout_new"),
    path('edit/<int:pk>/', TxOutUpdateView.as_view(), name="txout_edit"),
    path('delete/<int:pk>/', TxOutDeleteView.as_view(), name="txout_delete"),
    path('actors/', ActorListView.as_view(), name="actor_list"),
    path('actors/<int:pk>/', ActorDetailView.as_view(), name="actor_detail"),
    path('actors/new/', ActorCreateView.as_view(), name="actor_new"),
    path('actors/edit/<int:pk>/', ActorUpdateView.as_view(), name="actor_edit"),
    path('actors/delete/<int:pk>/', ActorDeleteView.as_view(), name="actor_delete"),
    path('api/tx_lookup', tx_lookup, name="tx_lookup"),
    path('', TxOutListView.as_view(), name="txout_list"),
    path('list/', TxOutListView.as_view(), name="txout_list"),
]
