from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import User
from admin_settings.models import LoyaltyProfile


@receiver(post_save, sender=User)
def create_loyalty_profile(sender, instance, created, **kwargs):
    if created and not hasattr(instance, 'loyalty_profile'):
        LoyaltyProfile.objects.create(user=instance)
