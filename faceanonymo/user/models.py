from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class InstaUserManager(BaseUserManager):
    def create_user(self, email_id, full_name, mobile_number, username, password=None):
        if not email_id:
            raise ValueError('Users must have an email_id address')
        
        user = self.model(
            email_id=self.normalize_email(email_id),
            full_name=full_name,
            mobile_number=mobile_number,
            username=username
        )

        user.set_password(password)  # Hash the password
        user.save(using=self._db)
        return user

    def create_superuser(self, email_id, full_name, mobile_number, username, password=None):
        user = self.create_user(
            email_id,
            full_name=full_name,
            mobile_number=mobile_number,
            username=username,
            password=password
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
    
class InstaUser(AbstractBaseUser):
    full_name = models.CharField(max_length=30)
    email_id = models.EmailField(max_length=254, unique=True)
    mobile_number = models.CharField(max_length=100, unique=True)
    username = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = InstaUserManager()

    USERNAME_FIELD = 'email_id'
    REQUIRED_FIELDS = ['full_name', 'mobile_number', 'username']

    def __str__(self):
        return self.email_id

class PostImageManager(models.Manager):
    def create_post_image(self, user, image_file, comment=''):
        # Create a new PostImage instance with the provided data
        post_image = self.model(user=user, image=image_file, comment=comment)
        post_image.save()
        return post_image

class PostImage(models.Model):
    user = models.ForeignKey(InstaUser, on_delete=models.CASCADE)  # Change to ForeignKey
    image = models.ImageField(upload_to='post_images/')
    comment = models.TextField(blank=True)
    likes = models.IntegerField(default=0)

    objects = PostImageManager()  # Assign the custom manager

    @classmethod
    def create_post_image(cls, user, image_file, comment=''):
        return cls.objects.create_post_image(user=user, image_file=image_file, comment=comment)
