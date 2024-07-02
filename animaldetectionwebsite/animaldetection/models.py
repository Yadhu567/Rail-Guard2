from django.db import models

class Detection(models.Model):
    documentno = models.CharField(max_length=100)
    area_name = models.CharField(max_length=100)
    animal_name = models.CharField(max_length=100)
    confidence = models.FloatField()
    time = models.CharField(max_length=100)
    animal_image = models.CharField(max_length=255)
    sound_file = models.CharField(max_length=255)
    no_detection = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.animal_name} - {self.time}"

class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    detections = models.ManyToManyField(Detection)

    def __str__(self):
        return self.name
