from django.db import models

# Create your models here.
class users(models.Model):
    uid=models.AutoField(primary_key=True)
    name=models.CharField(max_length=100)
    email=models.CharField(max_length=100,unique=True)
    password=models.CharField(max_length=100)
    register_time=models.DateTimeField(auto_now_add=True)
    user_type=models.CharField(max_length=25)
    user_image=models.TextField()
    user_login=models.SmallIntegerField()
    examcredits=models.IntegerField(default=7)
    
    