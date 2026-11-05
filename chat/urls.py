from django.urls import path , include

from rest_framework.routers import DefaultRouter

from .views import ChatRoomManageView, File_UploadMessageView , chatroomviewset

router = DefaultRouter()
router.register(r'rooms', chatroomviewset, basename='chatroom')

urlpatterns = [
    path('', include(router.urls)), #/rooms/
    path('rooms/<str:room_name>/manage/', ChatRoomManageView.as_view(), name='room-manage'),
    path('rooms/<str:room_name>/messages/', File_UploadMessageView.as_view(), name='room-upload-file'),
]




