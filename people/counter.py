from django.db import models

class Counter(models.Model):
    current_value = models.IntegerField(default=0)

    def __str__(self):
        return f"Case Number Counter (Current Value: {self.current_value})"
