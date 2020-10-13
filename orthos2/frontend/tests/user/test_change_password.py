from django.contrib.auth.models import User
from django.urls import reverse
from django_webtest import WebTest


class ChangePassword(WebTest):

    csrf_checks = True

    fixtures = [
        'frontend/tests/fixtures/serverconfigs.json',
        'frontend/tests/user/fixtures/users.json'
    ]

    def test_successful_change_password(self):
        """Test if a new user can create an account."""
        form = self.app.get(reverse('frontend:preferences_user'), user='user').form
        form['old_password'] = 'linux'
        form['new_password'] = 'linux1234'
        form['new_password2'] = 'linux1234'
        page = form.submit().maybe_follow()

        self.assertEqual(page.context['user'].username, 'user')
        self.assertIn(reverse('frontend:preferences_user'), page.request.url)
        self.assertContains(page, 'Password successfully changed')

        user = User.objects.get(username='user')
        self.assertTrue(user.check_password('linux1234'))

    def test_wrong_current_password(self):
        """Check current (old) password."""
        form = self.app.get(reverse('frontend:preferences_user'), user='user').form
        form['old_password'] = 'wrongpassword'
        form['new_password'] = 'linux1234'
        form['new_password2'] = 'linux1234'
        page = form.submit().maybe_follow()

        self.assertEqual(page.context['user'].username, 'user')
        self.assertIn(reverse('frontend:preferences_user'), page.request.url)
        self.assertContains(page, 'Current password is wrong')

    def test_password_too_short(self):
        """Check if password is too short (at least 8 characters)."""
        form = self.app.get(reverse('frontend:preferences_user'), user='user').form
        form['old_password'] = 'linux'
        form['new_password'] = '1234'
        form['new_password2'] = '1234'
        page = form.submit().maybe_follow()

        self.assertEqual(page.context['user'].username, 'user')
        self.assertIn(reverse('frontend:preferences_user'), page.request.url)
        self.assertContains(page, 'Password is too short')

    def test_password_confirmation_not_match(self):
        """Check if passwords do match."""
        form = self.app.get(reverse('frontend:preferences_user'), user='user').form
        form['old_password'] = 'wrongpassword'
        form['new_password'] = 'linux1234'
        form['new_password2'] = '1234linux'
        page = form.submit().maybe_follow()

        self.assertEqual(page.context['user'].username, 'user')
        self.assertIn(reverse('frontend:preferences_user'), page.request.url)
        self.assertContains(page, 'Password and confirmation password do not match')
