from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from .views import CustomUserCreationForm, EmailAuthenticationForm


class CustomUserCreationFormTests(TestCase):
    """Tests for the CustomUserCreationForm"""

    def test_valid_user_creation(self):
        """Test that a valid form creates a user with email as username"""
        form_data = {
            'email': 'test@example.com',
            'password1': 'securepass123',
            'password2': 'securepass123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.username, 'test@example.com')
        self.assertTrue(user.check_password('securepass123'))

    def test_duplicate_email_validation(self):
        """Test that duplicate emails are rejected"""
        # Create first user
        User.objects.create_user(
            username='existing@example.com',
            email='existing@example.com',
            password='password123'
        )

        # Try to create user with same email
        form_data = {
            'email': 'existing@example.com',
            'password1': 'securepass123',
            'password2': 'securepass123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('already exists', str(form.errors['email']))

    def test_password_mismatch(self):
        """Test that mismatched passwords are rejected"""
        form_data = {
            'email': 'test@example.com',
            'password1': 'securepass123',
            'password2': 'differentpass456'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_invalid_email_format(self):
        """Test that invalid email format is rejected"""
        form_data = {
            'email': 'not-an-email',
            'password1': 'securepass123',
            'password2': 'securepass123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_empty_email(self):
        """Test that empty email is rejected"""
        form_data = {
            'email': '',
            'password1': 'securepass123',
            'password2': 'securepass123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


class EmailAuthenticationFormTests(TestCase):
    """Tests for the EmailAuthenticationForm"""

    def setUp(self):
        """Create a test user"""
        self.user = User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password='testpass123'
        )

    def test_valid_authentication(self):
        """Test authentication with valid email and password"""
        form_data = {
            'email': 'testuser@example.com',
            'password': 'testpass123'
        }
        form = EmailAuthenticationForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.get_user(), self.user)

    def test_invalid_email(self):
        """Test authentication with non-existent email"""
        form_data = {
            'email': 'nonexistent@example.com',
            'password': 'testpass123'
        }
        form = EmailAuthenticationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Please enter a correct email and password', str(form.errors))

    def test_invalid_password(self):
        """Test authentication with incorrect password"""
        form_data = {
            'email': 'testuser@example.com',
            'password': 'wrongpassword'
        }
        form = EmailAuthenticationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Please enter a correct email and password', str(form.errors))

    def test_inactive_user(self):
        """Test that inactive users cannot authenticate"""
        self.user.is_active = False
        self.user.save()

        form_data = {
            'email': 'testuser@example.com',
            'password': 'testpass123'
        }
        form = EmailAuthenticationForm(data=form_data)
        self.assertFalse(form.is_valid())
        # Inactive users show the same error as invalid credentials for security
        self.assertIn('Please enter a correct email and password', str(form.errors))

    def test_empty_fields(self):
        """Test authentication with empty fields"""
        form_data = {
            'email': '',
            'password': ''
        }
        form = EmailAuthenticationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('password', form.errors)


class SignupViewTests(TestCase):
    """Tests for the signup view"""

    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('signup')

    def test_signup_page_loads(self):
        """Test that signup page loads correctly"""
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/signup.html')
        self.assertContains(response, 'email')
        self.assertContains(response, 'password')

    def test_successful_signup(self):
        """Test successful user registration"""
        form_data = {
            'email': 'newuser@example.com',
            'password1': 'securepass123',
            'password2': 'securepass123'
        }
        response = self.client.post(self.signup_url, form_data)

        # Should redirect to dashboard after successful signup
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))

        # User should be created
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

        # User should be logged in
        user = User.objects.get(email='newuser@example.com')
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_signup_with_duplicate_email(self):
        """Test signup with already existing email"""
        # Create existing user
        User.objects.create_user(
            username='existing@example.com',
            email='existing@example.com',
            password='password123'
        )

        form_data = {
            'email': 'existing@example.com',
            'password1': 'securepass123',
            'password2': 'securepass123'
        }
        response = self.client.post(self.signup_url, form_data)

        # Should stay on signup page
        self.assertEqual(response.status_code, 200)
        # Check that form has email error
        self.assertContains(response, 'A user with this email already exists.')

    def test_authenticated_user_redirected(self):
        """Test that authenticated users are redirected to dashboard"""
        user = User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser@example.com', password='testpass123')

        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))


class LoginViewTests(TestCase):
    """Tests for the login view"""

    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.user = User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password='testpass123'
        )

    def test_login_page_loads(self):
        """Test that login page loads correctly"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')

    def test_successful_login(self):
        """Test successful login with email"""
        form_data = {
            'email': 'testuser@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, form_data)

        # Should redirect to dashboard
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))

        # User should be logged in
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)

    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials"""
        form_data = {
            'email': 'testuser@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, form_data)

        # Should stay on login page
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a correct email and password')

    def test_login_with_nonexistent_email(self):
        """Test login with non-existent email"""
        form_data = {
            'email': 'nonexistent@example.com',
            'password': 'somepassword'
        }
        response = self.client.post(self.login_url, form_data)

        # Should stay on login page
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a correct email and password')

    def test_authenticated_user_redirected(self):
        """Test that authenticated users are redirected to dashboard"""
        self.client.login(username='testuser@example.com', password='testpass123')

        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))


class IndexViewTests(TestCase):
    """Tests for the index (landing page) view"""

    def setUp(self):
        self.client = Client()
        self.index_url = reverse('index')

    def test_index_page_loads(self):
        """Test that index page loads for unauthenticated users"""
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/index.html')

    def test_authenticated_user_redirected(self):
        """Test that authenticated users are redirected to dashboard"""
        user = User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser@example.com', password='testpass123')

        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))


class PasswordResetTests(TestCase):
    """Tests for password reset functionality"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password='oldpassword123'
        )
        self.password_reset_url = reverse('password_reset')

    def test_password_reset_page_loads(self):
        """Test that password reset page loads"""
        response = self.client.get(self.password_reset_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/password_reset.html')

    def test_password_reset_request(self):
        """Test password reset request submission"""
        form_data = {
            'email': 'testuser@example.com'
        }
        response = self.client.post(self.password_reset_url, form_data)

        # Should redirect to password reset done page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('password_reset_done'))
