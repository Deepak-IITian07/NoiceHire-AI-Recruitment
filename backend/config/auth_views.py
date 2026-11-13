
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.authtoken.models import Token


class HRLoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is None or not user.is_active or not user.is_staff:
            return Response(
                {'error': 'Invalid credentials or unauthorized access.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'username': user.username,
            'is_admin': True,
        })


class HRLogoutView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        request.user.auth_token.delete()

        return Response({'message': 'Logged out successfully.'})
