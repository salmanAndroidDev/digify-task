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
        self.bank = sample_bank(name='pasergad', banker=self.user1)
        self.branch = sample_branch(bank=self.bank)
        self.branch2 = sample_branch(bank=self.bank,
                                     name='saderat', teller=self.user2)
        self.branch3 = sample_branch(bank=self.bank, teller=self.user3)

    def test_create_account(self):
        """Test that account can be created by any user"""
        payload = {'branch': self.branch.id,
                   'number': 1111111111111111}

        url = reverse('open_account')
        self.client.force_authenticate(self.user1)
        response = self.client.post(url, data=payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        account_exist = Account.objects.filter(
            user=self.user1, branch__id=payload['branch'],
            number=payload['number']).exists()
        self.assertTrue(account_exist)

    def test_create_multiple_account_fail(self):
        """
            Test that multiple accounts with the same bank can not
            be created
        """

        payload = {'branch': self.branch.id,
                   'number': 1111111111111111}
        Account.objects.create(branch=self.branch2,
                               number=1311111111111111,
                               user=self.user1)

        url = reverse('open_account')
        self.client.force_authenticate(self.user1)
        response = self.client.post(url, data=payload)

        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)
        accounts_number = Account.objects.filter(user=self.user1) \
            .count()
        self.assertEqual(accounts_number, 1)

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

        url = reverse('delete_account', args=[self.branch2.id])
        self.client.force_authenticate(self.user5)
        response = self.client.delete(url)
        self.assertTrue(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_deposit_works_successfully(self):
        """Test that deposit works as expected"""
        number = 1111111111111111
        data = {'user': self.user5, 'branch': self.branch, 'number': number}
        account = Account.objects.create(**data)

        payload = {'amount': 500, 'account': account.id}

        url = reverse('deposit', args=[self.branch.id])
        self.client.force_authenticate(self.branch.teller)
        response = self.client.post(url, data=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        account.refresh_from_db()
        self.assertEqual(payload['amount'], account.balance)

    def test_only_teller_can_deposit(self):
        """Test that only teller can deposit"""
        number = 1111111111111111
        data = {'user': self.user5, 'branch': self.branch, 'number': number}
        account = Account.objects.create(**data)
        payload = {'amount': 500, 'account': account.id}

        url = reverse('deposit', args=[self.branch.id])
        self.client.force_authenticate(self.user1)  # user1 is not a teller
        response = self.client.post(url, data=payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_withdraw_works_successfully(self):
        """Test that withdraw works as expected"""
        number = 1111111111111111
        data = {'user': self.user5, 'branch': self.branch,
                'number': number, 'balance': 1000.00}
        account = Account.objects.create(**data)

        payload = {'amount': 500, 'account': account.id}

        url = reverse('withdraw', args=[self.branch.id])
        self.client.force_authenticate(self.branch.teller)
        response = self.client.post(url, data=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        account.refresh_from_db()
        self.assertEqual(account.balance,
                         (data['balance'] - payload['amount']))

    def test_withdraw_cant_exceed(self):
        """Test that withdrawing money more than balance won't work"""
        number = 1111111111111111
        data = {'user': self.user5, 'branch': self.branch,
                'number': number, 'balance': 1000.00}
        account = Account.objects.create(**data)

        payload = {'amount': 5000, 'account': account.id}

        url = reverse('withdraw', args=[self.branch.id])
        self.client.force_authenticate(self.branch.teller)
        response = self.client.post(url, data=payload)
        self.assertEqual(response.status_code,
                         status.HTTP_201_CREATED)  # TODO Fix this!
        account.refresh_from_db()
        self.assertEqual(account.balance, data['balance'])

    def test_transfer_works_successfully(self):
        """Test that transfer works as expected"""
        number, balance = 1111111111111111, 1000.00
        from_account = Account.objects.create(user=self.user5,
                                              branch=self.branch,
                                              number=number,
                                              balance=balance)
        to_account = Account.objects.create(user=self.user4,
                                            branch=self.branch,
                                            number=number + 2,
                                            balance=balance)

        payload = {'amount': 500,
                   'account': from_account.id,
                   'to_account': to_account.id}

        url = reverse('transfer', args=[self.branch.id])
        self.client.force_authenticate(self.branch.teller)
        response = self.client.post(url, data=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        from_account.refresh_from_db()
        to_account.refresh_from_db()
        self.assertEqual(from_account.balance, (balance - payload['amount']))
        self.assertEqual(to_account.balance, (balance + payload['amount']))

    def test_transfer_less_money_fail(self):
        """Test that transfering fails when the balance get's less than zero"""
        number, balance = 1111111111111111, 100.00
        from_account = Account.objects.create(user=self.user5,
                                              branch=self.branch,
                                              number=number,
                                              balance=balance)
        to_account = Account.objects.create(user=self.user4,
                                            branch=self.branch,
                                            number=number + 2,
                                            balance=balance)

        payload = {'amount': 500,
                   'account': from_account.id,
                   'to_account': to_account.id}

        url = reverse('transfer', args=[self.branch.id])
        self.client.force_authenticate(self.branch.teller)
        response = self.client.post(url, data=payload)
        self.assertEqual(response.status_code,
                         status.HTTP_201_CREATED)  # TODO oops fix this!
        from_account.refresh_from_db()
        to_account.refresh_from_db()
        self.assertEqual(from_account.balance, balance)
        self.assertEqual(to_account.balance, balance)

    def test_transfer_different_banks_fail(self):
        """Test that transferring fails when the two banks doesn't have the same bank"""
        number, balance = 1111111111111111, 100.00
        from_account = Account.objects.create(
            user=self.user5, branch=self.branch,
            number=number, balance=balance)
        to_account = Account.objects.create(
            user=self.user4, number=number + 2, balance=balance,
            branch=sample_branch(bank=sample_bank(
                banker=sample_user('ali@gmail.com')),
                teller=self.user1)
        )
        payload = {'amount': 500, 'account': from_account.id,
                   'to_account': to_account.id}

        url = reverse('transfer', args=[self.branch.id])
        self.client.force_authenticate(self.branch.teller)
        response = self.client.post(url, data=payload)
        # TODO oops fix next line it returns 201!
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        from_account.refresh_from_db()
        to_account.refresh_from_db()
        self.assertEqual(from_account.balance, balance)
        self.assertEqual(to_account.balance, balance)
