from django.db import IntegrityError
from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import Bank, Branch, Account
from ..exceptions import AccountAlreadyExistError


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


class TestModel(TestCase):
    def setUp(self):
        self.user1 = sample_user('one@gmail.com')
        self.user2 = sample_user('two@gmail.com')
        self.user3 = sample_user('three@gmail.com')
        self.user4 = sample_user('four@gmail.com')
        self.user5 = sample_user('five@gmail.com')

    def test_create_bank_successfully(self):
        """Test that bank can be created successfully"""
        bank_name = 'Pasargad'
        bank = sample_bank(name=bank_name)
        self.assertEqual(str(bank), bank_name)

    def test_create_branch_successfully(self):
        """Test that branch can be created for each bank successfully"""
        data = {'bank': sample_bank(),
                'name': 'USB',
                'address': 'address of usb',
                'teller': self.user2}

        branch = Branch.objects.create(**data)
        for key in data:
            self.assertEqual(getattr(branch, key), data[key])

    def test_branch_has_one_teller(self):
        """Test that the teller can not be teller of other branches"""
        bank = sample_bank(name='PASARGAD', banker=self.user1)
        sample_branch(name='USA', bank=bank, teller=self.user2)

        with self.assertRaises(IntegrityError):
            # It should an Integrity error
            sample_branch(name='USD', bank=bank, teller=self.user2)

    def test_create_account_successfully(self):
        """Test that account can be created successfully"""
        data = {
            'user': self.user1,
            'branch': sample_branch(),
        }
        account = Account.objects.create(**data)
        for key in data.keys():
            self.assertEquals(getattr(account, key), data[key])

    def test_multiple_account_for_each_bank_fails(self):
        """Test that for each bank ONLY one account can be created"""
        bank = sample_bank()
        branch_a = sample_branch(name='branch a', bank=bank, teller=self.user4)
        branch_b = sample_branch(name='branch b', bank=bank, teller=self.user5)

        data1 = {'user': self.user1, 'branch': branch_a}
        data2 = {'user': self.user1, 'branch': branch_a}
        data3 = {'user': self.user1, 'branch': branch_b}

        Account.objects.create(**data1)

        #  creating 2 accounts with the same user and same bank fails
        #  with the same branch
        with self.assertRaises(AccountAlreadyExistError):
            Account.objects.create(**data2)

        #  creating 2 accounts with the same user and same bank fails
        #  with different branches
        with self.assertRaises(AccountAlreadyExistError):
            Account.objects.create(**data3)

    def test_one_account_for_each_banks(self):
        """
            Test that each user can create at lease one account for each
            bank
        """
        meli_bank = sample_bank(name='Meli', banker=self.user1)
        pasargad_bank = sample_bank(name='Pasargad', banker=self.user2)

        branch_a = sample_branch(name='branch a',
                                 bank=meli_bank,
                                 teller=self.user3)

        branch_b = sample_branch(name='branch b',
                                 bank=pasargad_bank,
                                 teller=self.user4)

        Account.objects.create(user=self.user5, branch=branch_a)
        Account.objects.create(user=self.user5, branch=branch_b)

        accounts = Account.objects.filter(user=self.user5).count()
        self.assertEqual(accounts, 2)
