from django.db import models


class movie(models.Model):
    title=models.CharField(max_length=20)
    description=models.CharField(max_length=50)
    language=models.CharField(max_length=20)
    year=models.IntegerField()
    poster=models.ImageField(upload_to="images")

