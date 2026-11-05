from django.urls import path

from .views import OperatorReportView

urlpatterns = [
    path('operator/me/', OperatorReportView.as_view(), name='operator-my-report'),

    path('operator/<int:operator_id>/', OperatorReportView.as_view(), name='operator-detail-report'),
]
