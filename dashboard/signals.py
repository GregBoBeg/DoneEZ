from django.db.models.signals import post_save
from django.conf import settings
from django.dispatch import receiver

from doneez_app.models import Business


# This function receives a signal when the database CREATES a new User record. 
# Upon receiving the signal, it CREATES a corresponding Business (Profile) record.
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Business.objects.create(user=instance)


# This function receives a signal when the database SAVES an existing User record. 
# Upon receiving the signal, it also SAVES the corresponding Business (Profile) record.
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_profile(sender, instance, **kwargs):
    instance.business.save()

