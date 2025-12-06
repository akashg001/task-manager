from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import User, Task
from .serializers import (
    UserSerializer, 
    UserLoginSerializer, 
    TaskSerializer,
    TaskCreateUpdateSerializer
)
from .permissions import IsOwnerOrAdmin, IsAdminUser


# ==================== Authentication Views ====================

@extend_schema(
    request=UserSerializer,
    responses={201: UserSerializer},
    description="Register a new user"
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user
    """
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'message': 'User registered successfully',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=UserLoginSerializer,
    responses={200: {'access': 'string', 'refresh': 'string', 'user': UserSerializer}},
    description="Login and receive JWT tokens"
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Login and receive JWT tokens
    """
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        
        return Response({
            'error': 'Invalid username or password'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==================== Task ViewSet ====================

class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Task CRUD operations with pagination and filtering
    """
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['completed']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'completed']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Return tasks based on user role
        - Regular users see only their own tasks
        - Admins see all tasks
        """
        user = self.request.user
        if user.is_admin:
            return Task.objects.all()
        return Task.objects.filter(owner=user)
    
    def get_serializer_class(self):
        """
        Use different serializers for different actions
        """
        if self.action in ['create', 'update', 'partial_update']:
            return TaskCreateUpdateSerializer
        return TaskSerializer
    
    @extend_schema(
        description="Retrieve a list of all tasks with pagination and filtering",
        parameters=[
            OpenApiParameter(
                name='completed',
                description='Filter by completion status',
                required=False,
                type=bool
            ),
            OpenApiParameter(
                name='search',
                description='Search in title and description',
                required=False,
                type=str
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """List all tasks"""
        return super().list(request, *args, **kwargs)
    
    @extend_schema(description="Retrieve details of a specific task")
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific task"""
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        request=TaskCreateUpdateSerializer,
        responses={201: TaskSerializer},
        description="Create a new task"
    )
    def create(self, request, *args, **kwargs):
        """Create a new task"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Set owner to current user
        task = serializer.save(owner=request.user)
        
        return Response({
            'message': 'Task created successfully',
            'task': TaskSerializer(task).data
        }, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        request=TaskCreateUpdateSerializer,
        responses={200: TaskSerializer},
        description="Update details of a specific task"
    )
    def update(self, request, *args, **kwargs):
        """Update a task"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        
        return Response({
            'message': 'Task updated successfully',
            'task': TaskSerializer(task).data
        }, status=status.HTTP_200_OK)
    
    @extend_schema(
        request=TaskCreateUpdateSerializer,
        responses={200: TaskSerializer},
        description="Partially update a specific task"
    )
    def partial_update(self, request, *args, **kwargs):
        """Partially update a task"""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)
    
    @extend_schema(
        responses={200: {'message': 'string'}},
        description="Delete a specific task"
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a task"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'message': 'Task deleted successfully'
        }, status=status.HTTP_200_OK)
    
    @extend_schema(
        description="Get statistics about user's tasks",
        responses={200: {
            'total': 'integer',
            'completed': 'integer',
            'pending': 'integer'
        }}
    )
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get task statistics for the current user
        """
        queryset = self.get_queryset()
        total = queryset.count()
        completed = queryset.filter(completed=True).count()
        pending = total - completed
        
        return Response({
            'total': total,
            'completed': completed,
            'pending': pending
        })


# ==================== Admin Views ====================

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing users (Admin only)
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    @extend_schema(description="Get list of all users (Admin only)")
    def list(self, request, *args, **kwargs):
        """List all users"""
        return super().list(request, *args, **kwargs)
    
    @extend_schema(description="Get details of a specific user (Admin only)")
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific user"""
        return super().retrieve(request, *args, **kwargs)

