from django.db import models

class DHT(models.Model):
    humidity = models.FloatField()
    temperature = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.pk}::{self.humidity}::{self.temperature}::{self.created_at}'

