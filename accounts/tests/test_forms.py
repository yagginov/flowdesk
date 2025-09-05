from django.test import TestCase
from django.contrib.auth import get_user_model

from accounts.forms import SignUpForm, UserUpdateForm, ProfileUpdateForm

User = get_user_model()


class TestSignUpForm(TestCase):
    form_class = SignUpForm

    def setUp(self):
        self.data = {
            "username": "user",
            "password1": "asldhfS)(F8dsajsdf)",
            "password2": "asldhfS)(F8dsajsdf)",
            "email": "test@test.com",
            "first_name": "first_name",
            "last_name": "last_name",
        }

    def test_valid_form(self):
        form = self.form_class(data=self.data)
        self.assertTrue(form.is_valid())

    def test_username_with_dots(self):
        self.data["username"] = "dot.username"
        form = self.form_class(data=self.data)
        self.assertTrue(form.is_valid())

        form.instance.username = "more.dot.username"
        self.assertTrue(form.is_valid())

        form.instance.username = "dots.....inline"
        self.assertTrue(form.is_valid())

        form.instance.username = ".start.from.dots"
        self.assertTrue(form.is_valid())

    def test_username_with_underscores(self):
        self.data["username"] = "underscore_username"
        form = self.form_class(data=self.data)
        self.assertTrue(form.is_valid())

        form.instance.username = "u_s_e_r_n_a_m_e"
        self.assertTrue(form.is_valid())

        form.instance.username = "more_____underscores"
        self.assertTrue(form.is_valid())

        form.instance.username = "_start_with_underscore"
        self.assertTrue(form.is_valid())

    def test_small_username_size(self):
        self.data["username"] = "s"
        form = self.form_class(data=self.data)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_big_username_size(self):
        self.data["username"] = "u" * 31
        form = self.form_class(data=self.data)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_username_with_spaces(self):
        self.data["username"] = "u  sername"
        form = self.form_class(data=self.data)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_username_with_upercase_letters(self):
        self.data["username"] = "USERNAME"
        form = self.form_class(data=self.data)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_username_with_invalid_symbols(self):
        self.data["username"] = "|\\)*&^daf"
        form = self.form_class(data=self.data)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_username_with_cyrilic_symbols(self):
        self.data["username"] = "юзернейм"
        form = self.form_class(data=self.data)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_save_two_users_with_same_username(self):
        form1 = self.form_class(data=self.data)
        form1.save()
        form2 = self.form_class(data=self.data)
        self.assertFalse(form2.is_valid())
        self.assertIn("username", form2.errors)


class TestUserUpdateForm(TestSignUpForm):
    form_class = UserUpdateForm

    def setUp(self):
        self.data = {
            "username": "user",
            "email": "test@test.com",
            "first_name": "first_name",
            "last_name": "last_name",
        }
