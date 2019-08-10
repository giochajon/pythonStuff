from django.db import models


class Job(models.Model):
    image = models.ImageField(upload to 'images/')
    summary = models.CharField(max_lenght=200)
    

# Create your models here.
