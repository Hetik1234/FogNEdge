from django.db import models

class VenueAlert(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    status_priority = models.CharField(max_length=50)
    details = models.TextField()

    occupancy = models.IntegerField(default=0)
    co2_level = models.IntegerField(default=400)
    temperature = models.FloatField(default=22.0)
    hvac_airflow = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.status_priority} at {self.timestamp}"