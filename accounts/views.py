from django.contrib.auth import get_user_model

from rest_framework.generics import  RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated

from .serializers import  EditSerializer


User = get_user_model()



class EditView (RetrieveUpdateAPIView):
    serializer_class = EditSerializer

    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    