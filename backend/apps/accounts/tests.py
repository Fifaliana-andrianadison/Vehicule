from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import Profile


class ProfileModelTest(TestCase):
    def test_profile_created_on_user_creation(self):
        user = User.objects.create_user(username='testuser', password='pass1234')
        self.assertTrue(hasattr(user, 'profile'))
        self.assertIsInstance(user.profile, Profile)

    def test_profile_defaults(self):
        user = User.objects.create_user(username='testuser', password='pass1234')
        self.assertEqual(user.profile.phone, '')
        self.assertEqual(user.profile.address, '')
        self.assertEqual(user.profile.notification_email, True)

    def test_profile_str(self):
        user = User.objects.create_user(username='testuser', password='pass1234')
        self.assertEqual(str(user.profile), 'Profil de testuser')

    def test_profile_update(self):
        user = User.objects.create_user(username='testuser', password='pass1234')
        user.profile.phone = '0123456789'
        user.profile.address = '1 Rue de Paris'
        user.profile.notification_email = False
        user.profile.save()
        user.profile.refresh_from_db()
        self.assertEqual(user.profile.phone, '0123456789')
        self.assertEqual(user.profile.address, '1 Rue de Paris')
        self.assertFalse(user.profile.notification_email)


class RegisterViewTest(TestCase):
    def test_register_get(self):
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')

    def test_register_post_valid(self):
        data = {
            'username': 'newuser',
            'email': 'new@test.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        }
        response = self.client.post(reverse('accounts:register'), data)
        self.assertRedirects(response, reverse('dashboard:home'))
        self.assertEqual(User.objects.filter(username='newuser').count(), 1)
        user = User.objects.get(username='newuser')
        self.assertEqual(user.email, 'new@test.com')
        self.assertTrue(hasattr(user, 'profile'))

    def test_register_post_invalid(self):
        data = {
            'username': 'newuser',
            'email': 'new@test.com',
            'password1': 'pass1234',
            'password2': 'different',
        }
        response = self.client.post(reverse('accounts:register'), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(username='newuser').count(), 0)

    def test_register_auto_login(self):
        data = {
            'username': 'autologin',
            'email': 'auto@test.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        }
        self.client.post(reverse('accounts:register'), data)
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)

    def test_register_duplicate_username(self):
        User.objects.create_user(username='existing', password='pass1234')
        data = {
            'username': 'existing',
            'email': 'new@test.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
        }
        response = self.client.post(reverse('accounts:register'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')


class LoginViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass1234')

    def test_login_get(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)

    def test_login_post_valid(self):
        data = {'username': 'testuser', 'password': 'pass1234'}
        response = self.client.post(reverse('accounts:login'), data)
        self.assertRedirects(response, reverse('dashboard:home'))

    def test_login_post_invalid(self):
        data = {'username': 'testuser', 'password': 'wrongpassword'}
        response = self.client.post(reverse('accounts:login'), data)
        self.assertEqual(response.status_code, 200)

    def test_login_already_authenticated(self):
        self.client.login(username='testuser', password='pass1234')
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)

    def test_login_redirects_to_dashboard(self):
        User.objects.create_user(username='user2', password='pass1234')
        data = {'username': 'user2', 'password': 'pass1234'}
        response = self.client.post(reverse('accounts:login'), data)
        self.assertRedirects(response, reverse('dashboard:home'))


class LogoutViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass1234')

    def test_logout(self):
        self.client.login(username='testuser', password='pass1234')
        response = self.client.get(reverse('accounts:logout'))
        self.assertRedirects(response, reverse('accounts:login'))
        response = self.client.get(reverse('dashboard:home'))
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('dashboard:home')}")

    def test_logout_requires_no_auth(self):
        response = self.client.get(reverse('accounts:logout'))
        expected = f"{reverse('accounts:login')}?next={reverse('accounts:logout')}"
        self.assertRedirects(response, expected)


class ProfileViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@test.com',
            password='pass1234',
        )

    def test_profile_requires_login(self):
        response = self.client.get(reverse('accounts:profile'))
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('accounts:profile')}")

    def test_profile_get(self):
        self.client.login(username='testuser', password='pass1234')
        response = self.client.get(reverse('accounts:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('user_form', response.context)
        self.assertIn('profile_form', response.context)

    def test_profile_update(self):
        self.client.login(username='testuser', password='pass1234')
        data = {
            'username': 'testuser',
            'email': 'updated@test.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '0612345678',
            'address': '15 Rue de Paris',
            'notification_email': False,
        }
        response = self.client.post(reverse('accounts:profile'), data)
        self.assertRedirects(response, reverse('accounts:profile'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'updated@test.com')
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')
        self.assertEqual(self.user.profile.phone, '0612345678')
        self.assertEqual(self.user.profile.address, '15 Rue de Paris')
        self.assertFalse(self.user.profile.notification_email)

    def test_profile_update_invalid(self):
        self.client.login(username='testuser', password='pass1234')
        data = {
            'username': '',
            'email': 'invalid',
        }
        response = self.client.post(reverse('accounts:profile'), data)
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'test@test.com')


class LoginRedirectTest(TestCase):
    def test_redirect_to_login_when_not_authenticated(self):
        protected_urls = [
            reverse('dashboard:home'),
            reverse('vehicles:list'),
            reverse('maintenance:list'),
            reverse('documents:list'),
        ]
        for url in protected_urls:
            response = self.client.get(url)
            self.assertRedirects(response, f"{reverse('accounts:login')}?next={url}")
