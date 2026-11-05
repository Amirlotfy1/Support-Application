from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .services import OperatorStatisticsService

User = get_user_model()

class OperatorReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, operator_id=None):
        if operator_id:
            operator = get_object_or_404(User, pk=operator_id)
        else:
            operator = request.user

        ticket_type = request.query_params.get('type', None)
        use_jalali = request.query_params.get('jalali', 'false').lower() == 'true'

        stats = OperatorStatisticsService.get_monthly_report(
            operator=operator,
            ticket_type=ticket_type,
            use_jalali=use_jalali
        )

        return Response(stats, status=status.HTTP_200_OK)
