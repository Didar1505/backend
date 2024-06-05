from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save

class User(AbstractUser):
    username = models.CharField(unique=True, max_length=50)
    email = models.EmailField(unique=True)
    full_name = models.CharField(unique=True, max_length=100)
    otp = models.CharField(max_length=100, blank=True, null=True)
    refresh_token = models.CharField(max_length=1000, null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username']

    def __str__(self) -> str:
        return self.email
    
    def save(self, *args, **kwargs):
        email_username = self.email.split("@")[0]
        if self.full_name == '' or self.full_name == None:
            self.full_name = email_username
        if self.username == '' or self.username == None:
            self.username = email_username
        return super(User, self).save(*args, **kwargs)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.FileField(upload_to='user_folder', default='default_user.jpg', blank=True, null=True)
    full_name = models.CharField(max_length=100)
    country = models.CharField(max_length=100, blank=True, null=True)
    about = models.TextField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        if self.full_name:
            return self.full_name
        else:
            return str(self.user.full_name)
        
    def save(self, *args, **kwargs):
        if self.full_name == '' or self.full_name == None:
            self.full_name = str(self.user.full_name)
        super(Profile, self).save(*args, **kwargs)


# Signal receiver function
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# Signal receiver function to save the profile when the user object is saved
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()