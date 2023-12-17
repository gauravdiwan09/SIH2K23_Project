from django.db import models

# Create your models here.
class users(models.Model):
    uid=models.BigAutoField(primary_key=True)
    name=models.CharField(max_length=100)
    email=models.CharField(max_length=100,unique=True)
    password=models.CharField(max_length=100)
    register_time=models.DateTimeField(auto_now_add=True)
    user_type=models.CharField(max_length=25)
    user_image=models.TextField()
    user_login=models.SmallIntegerField()
    examcredits=models.IntegerField(default=7)
    
class questions(models.Model):
    questions_uid=models.BigAutoField(primary_key=True)
    test_id=models.CharField(max_length=100)
    qid=models.CharField(max_length=25)
    q=models.TextField()
    a=models.CharField(max_length=100)
    b=models.CharField(max_length=100)
    c=models.CharField(max_length=100)
    d=models.CharField(max_length=100)
    ans=models.CharField(max_length=10)
    marks=models.IntegerField()
    uid=models.BigIntegerField()
    
class teachers(models.Model):
    tid=models.BigAutoField(primary_key=True)
    email=models.CharField(max_length=100)
    test_id=models.CharField(max_length=100)
    test_type=models.CharField(max_length=75)
    start=models.DateTimeField(auto_now_add=True)
    end=models.DateTimeField()
    duration=models.IntegerField()
    show_ans=models.IntegerField()
    password=models.CharField(max_length=100)
    subject=models.CharField(max_length=100)
    topic=models.CharField(max_length=100)
    proctoring_type=models.SmallIntegerField()
    uid=models.BigIntegerField()
    
class studenttestinfo(models.Model):
    stiid=models.BigAutoField(primary_key=True)
    email=models.CharField(max_length=100)
    test_id=models.CharField(max_length=100)
    time_left=models.IntegerField()
    completed=models.SmallIntegerField(default=0)
    uid=models.BigIntegerField()
    
class students(models.Model):
    sid=models.BigAutoField(primary_key=True)
    email= models.CharField(max_length=100)
    test_id= models.CharField(max_length=100)
    qid= models.CharField(max_length=25)
    ans=models.TextField()
    uid=models.BigIntegerField()
    
class proctoring_log(models.Model):
    pid=models.BigAutoField(primary_key=True)
    email=models.CharField(max_length=100)
    name=models.CharField(max_length=100)
    test_id=models.CharField(max_length=100)
    voice_db=models.IntegerField(null=True,blank=True,default=0)
    img_log=models.TextField()
    user_movements_updown=models.SmallIntegerField()
    user_movements_lr=models.SmallIntegerField()
    user_movements_eyes=models.SmallIntegerField()
    phone_detection=models.SmallIntegerField()
    person_status=models.SmallIntegerField()
    log_time=models.DateTimeField(auto_now_add=True)
    uid=models.BigIntegerField()
    
class practicalqa(models.Model):
    pracqa_qid=models.BigAutoField(primary_key=True)
    test_id=models.CharField(max_length=100)
    qid=models.CharField(max_length=25)
    q=models.TextField()
    compiler=models.SmallIntegerField()
    marks=models.IntegerField()
    uid=models.BigIntegerField()
    
class practicaltest(models.Model):
    pid=models.BigAutoField(primary_key=True)
    email=models.CharField(max_length=100)
    test_id=models.CharField(max_length=100)
    qid=models.CharField(max_length=25)
    code=models.TextField(null=True,blank=True)
    input=models.TextField(null=True,blank=True)
    executed=models.CharField(max_length=125)
    marks=models.IntegerField()
    uid=models.BigIntegerField()
    
        
