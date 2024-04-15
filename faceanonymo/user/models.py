from django.db import models

class User(models.Model):
    full_name = models.CharField(max_length=30)
    email_id = models.EmailField(max_length=254, unique=True)
    mobile_number = models.CharField(max_length=100, unique=True)
    username = models.CharField(max_length=100)
    password = models.TextField(max_length=1000)
