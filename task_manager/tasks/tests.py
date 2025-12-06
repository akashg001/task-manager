from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import User, Task


class AuthenticationTestCase(APITestCase):
    """Test user authentication"""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
    
    def test_user_registration(self):
        """Test user registration"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')
    
    def test_registration_missing_fields(self):
        """Test registration with missing required fields"""
        data = {'username': 'testuser'}
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_registration_duplicate_username(self):
        """Test registration with duplicate username"""
        User.objects.create_user(
            username='testuser',
            email='test1@example.com',
            password='pass123'
        )
        data = {
            'username': 'testuser',
            'email': 'test2@example.com',
            'password': 'pass123'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_login(self):
        """Test user login"""
        # Create user
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Login
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        data = {
            'username': 'nonexistent',
            'password': 'wrongpass'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TaskCRUDTestCase(APITestCase):
    """Test Task CRUD operations"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create user and get token
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Login to get token
        login_url = reverse('login')
        response = self.client.post(login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        self.task_list_url = reverse('task-list')
    
    def test_create_task(self):
        """Test creating a task"""
        data = {
            'title': 'Test Task',
            'description': 'Test Description',
            'completed': False
        }
        response = self.client.post(self.task_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['task']['title'], 'Test Task')
        self.assertFalse(response.data['task']['completed'])
    
    def test_create_task_without_auth(self):
        """Test creating task without authentication"""
        self.client.credentials()  # Remove credentials
        data = {'title': 'Test Task'}
        response = self.client.post(self.task_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_task_missing_title(self):
        """Test creating task without required title"""
        data = {'description': 'Test Description'}
        response = self.client.post(self.task_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_list_tasks(self):
        """Test listing all tasks"""
        # Create tasks
        Task.objects.create(
            title='Task 1',
            owner=self.user
        )
        Task.objects.create(
            title='Task 2',
            owner=self.user
        )
        
        response = self.client.get(self.task_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
    
    def test_retrieve_task(self):
        """Test retrieving a specific task"""
        task = Task.objects.create(
            title='Test Task',
            owner=self.user
        )
        
        url = reverse('task-detail', kwargs={'pk': task.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], task.id)
    
    def test_retrieve_nonexistent_task(self):
        """Test retrieving a task that doesn't exist"""
        url = reverse('task-detail', kwargs={'pk': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_update_task(self):
        """Test updating a task"""
        task = Task.objects.create(
            title='Original Title',
            owner=self.user
        )
        
        url = reverse('task-detail', kwargs={'pk': task.id})
        data = {
            'title': 'Updated Title',
            'completed': True
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['task']['title'], 'Updated Title')
        self.assertTrue(response.data['task']['completed'])
    
    def test_partial_update_task(self):
        """Test partially updating a task"""
        task = Task.objects.create(
            title='Original Title',
            description='Original Description',
            owner=self.user
        )
        
        url = reverse('task-detail', kwargs={'pk': task.id})
        data = {'completed': True}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['task']['completed'])
        self.assertEqual(response.data['task']['title'], 'Original Title')
    
    def test_delete_task(self):
        """Test deleting a task"""
        task = Task.objects.create(
            title='Task to Delete',
            owner=self.user
        )
        
        url = reverse('task-detail', kwargs={'pk': task.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify deletion
        self.assertFalse(Task.objects.filter(id=task.id).exists())


class TaskPaginationFilteringTestCase(APITestCase):
    """Test pagination and filtering"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create user and authenticate
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        login_url = reverse('login')
        response = self.client.post(login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        # Create test tasks
        for i in range(15):
            Task.objects.create(
                title=f'Task {i}',
                completed=(i % 2 == 0),
                owner=self.user
            )
        
        self.task_list_url = reverse('task-list')
    
    def test_pagination(self):
        """Test task pagination"""
        response = self.client.get(f'{self.task_list_url}?page=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)  # Default page size
        self.assertEqual(response.data['count'], 15)
    
    def test_filter_by_completed(self):
        """Test filtering tasks by completion status"""
        # Filter completed tasks
        response = self.client.get(f'{self.task_list_url}?completed=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for task in response.data['results']:
            self.assertTrue(task['completed'])
        
        # Filter incomplete tasks
        response = self.client.get(f'{self.task_list_url}?completed=false')
        for task in response.data['results']:
            self.assertFalse(task['completed'])
    
    def test_search_tasks(self):
        """Test searching tasks"""
        Task.objects.create(
            title='Unique Search Term',
            owner=self.user
        )
        
        response = self.client.get(f'{self.task_list_url}?search=Unique')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(response.data['count'], 0)


class TaskPermissionTestCase(APITestCase):
    """Test task permissions and authorization"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create two users
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123'
        )
        
        # Create admin user
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            role='admin'
        )
        
        # Create task for user1
        self.task = Task.objects.create(
            title='User1 Task',
            owner=self.user1
        )
    
    def get_token(self, username, password):
        """Helper method to get JWT token"""
        login_url = reverse('login')
        response = self.client.post(login_url, {
            'username': username,
            'password': password
        })
        return response.data['access']
    
    def test_user_cannot_access_other_tasks(self):
        """Test that users cannot access other users' tasks"""
        # Login as user2
        token = self.get_token('user2', 'pass123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Try to access user1's task
        url = reverse('task-detail', kwargs={'pk': self.task.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_user_can_access_own_tasks(self):
        """Test that users can access their own tasks"""
        # Login as user1
        token = self.get_token('user1', 'pass123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Access own task
        url = reverse('task-detail', kwargs={'pk': self.task.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_admin_can_access_all_tasks(self):
        """Test that admins can access all tasks"""
        # Login as admin
        token = self.get_token('admin', 'admin123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Access user1's task
        url = reverse('task-detail', kwargs={'pk': self.task.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_admin_endpoint_requires_admin_role(self):
        """Test that admin endpoints require admin role"""
        # Try with regular user
        token = self.get_token('user1', 'pass123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Try with admin
        token = self.get_token('admin', 'admin123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TaskStatsTestCase(APITestCase):
    """Test task statistics endpoint"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Create user and authenticate
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        login_url = reverse('login')
        response = self.client.post(login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        # Create tasks
        Task.objects.create(title='Task 1', completed=True, owner=self.user)
        Task.objects.create(title='Task 2', completed=True, owner=self.user)
        Task.objects.create(title='Task 3', completed=False, owner=self.user)
    
    def test_task_stats(self):
        """Test task statistics endpoint"""
        url = reverse('task-stats')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total'], 3)
        self.assertEqual(response.data['completed'], 2)
        self.assertEqual(response.data['pending'], 1)