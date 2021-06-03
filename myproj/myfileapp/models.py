from django.db import models
import os


# Create your models here.
class Uploadfile(models.Model):
    name = models.CharField(max_length=255)
    my_files = models.FileField(upload_to="")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
