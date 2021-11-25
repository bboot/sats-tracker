from django.urls import path, include

from .views import TxOutDetailView, TxOutListView

urlpatterns = [
    path('<int:pk>/', TxOutDetailView.as_view(), name="txout_detail"),
    path('', TxOutListView.as_view(), name="txout_list"),
]
