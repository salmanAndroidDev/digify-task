from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from ..models import Bank, Branch, Account


def sample_user(email='test@gmail.com', password='test1234'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email=email, password=password)


def sample_bank(name='Meli', address='Tehran', banker=None):
    """Create a sample bank"""
    if banker is None:
        banker = sample_user()
    return Bank.objects.create(name=name, address=address, banker=banker)


def sample_branch(bank=None, name='USB', address='USB city', teller=None):
    """Create a sample branch"""
    if bank is None:
        bank = sample_bank()
    if teller is None:
        teller = sample_user('teller@gmail.com')

    return Branch.objects.create(name=name, address=address, bank=bank,
                                 teller=teller)


class TestModel(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = sample_user('one@gmail.com')
        self.user2 = sample_user('two@gmail.com')
        self.user3 = sample_user('three@gmail.com')
        self.user4 = sample_user('four@gmail.com')
        self.user5 = sample_user('five@gmail.com')
        self.bank = sample_bank()
        self.branch = sample_branch(bank=self.bank)

    def test_create_account(self):
        """Test that account can be created by any user"""
        data = {'branch': self.branch.id,
                'number': 1111111111111111}

        url = reverse('open_account')
        self.client.force_authenticate(self.user1)
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        account_exist = Account.objects.filter(user=self.user1,
                                               branch__id=data['branch'],
                                               number=data['number']).exists()
        self.assertTrue(account_exist)

    def test_no_auth_create_account_fail(self):
        """Test that account can not be created with no authentication"""
        data = {'branch': self.branch.id,
                'number': 1111111111111111}

        url = reverse('open_account')
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_account_successfully(self):
        """
            Test that account can be deleted from the branch that was
            created
        """
        data = {'user': self.user5,
                'branch': self.branch,
                'number': 1111111111111111}
        Account.objects.create(**data)

        url = reverse('delete_account', args=[self.branch.id])
        self.client.force_authenticate(self.user5)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        account_exist = Account.objects.filter(**data).exists()
        self.assertFalse(account_exist)

    def test_delete_account_wrong_branch_fail(self):
        """
            Test that account can not be deleted from the branch that was
            not created
        """
        data = {'user': self.user5,
                'branch': self.branch,
                'number': 1111111111111111}
        Account.objects.create(**data)
        new_branch = sample_branch(name='Pasergad',
                                   teller=self.user2,
                                   bank=self.bank)
        url = reverse('delete_account', args=[new_branch.id])
        self.client.force_authenticate(self.user5)
        response = self.client.delete(url)
        self.assertTrue(response.status_code, status.HTTP_403_FORBIDDEN)
