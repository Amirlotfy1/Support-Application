from django.urls import path
from . import views

urlpatterns = [
    path('', views.ticket_list, name='ticket-list'),
    path('<int:pk>/', views.ticket_detail, name='ticket-detail'),
    path('<int:ticket_id>/replies/', views.ticket_replies, name='ticket-replies'),
    path('count/' , views.Count_ticket.as_view() , name= 'count_ticket'),
    path('type/' , views.filter_type_ticket , name= 'filter_type'),
]
