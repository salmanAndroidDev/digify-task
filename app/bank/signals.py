from django.db.models.signals import post_save
from .models import Transaction
from django.dispatch import receiver


@receiver(post_save, sender=Transaction)
def actions_for_transaction_creation(sender, instance, **kwargs):
    """
        Send message to user when a transaction related to his/her
        account was created
     """
    # TODO, Use Celery and RabbitMQ to for sending mail or SMS
    pass
