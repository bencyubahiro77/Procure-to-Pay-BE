from django.contrib.auth.models import User
from accounts.serializers import RegisterSerializer, UserSerializer, RoleSerializer
from rest_framework.permissions import IsAuthenticated
from accounts.models import Role
from rest_framework import generics, status, viewsets, filters, serializers
from rest_framework.response import Response

from accounts.permissions import IsApprover, IsFinance, IsStaff, IsAdmin
from procure_to_pay.utils import RequestPagination

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        try:
            print("Registration request data:", request.data)
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            print("Validated data:", serializer.validated_data)
            user = serializer.save()
            print("Registered user:", user)

            # Refresh the user to get the profile data
            user.refresh_from_db()

            return Response({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.profile.role,
                "message": "User registered successfully"
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            print("Registration error:", e)
            return Response({
                "message": "Registration failed",
                "details": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class MeView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

class UserListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdmin  | IsFinance]
    serializer_class = UserSerializer
    pagination_class = RequestPagination
    queryset = User.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    # Fields searchable using ?search=keyword
    search_fields = [
        'username',
        'email',
        'profile__role',
    ]

    # Fields sortable using ?ordering=-date_joined or ?ordering=username
    ordering_fields = [
        'date_joined',
        'username',
        'email',
    ]

class UserDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsAdmin  | IsStaff | IsApprover  | IsFinance]
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = 'id'

class ChangeUserRoleView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = User.objects.all()
    lookup_field = "id"
    
    class InputSerializer(serializers.Serializer):
        role = serializers.ChoiceField(choices=Role.choices)

    def get_serializer(self, *args, **kwargs):
        """Use the inline serializer only for input validation."""
        return self.InputSerializer(*args, **kwargs)

    def update(self, request, *args, **kwargs):
        user = self.get_object()

        # Validate request body
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Extract validated role
        new_role = serializer.validated_data["role"]

        # Update profile
        user.profile.role = new_role
        user.profile.save()

        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.profile.role,
                "message": "User role updated successfully"
            },
            status=status.HTTP_200_OK
        )

