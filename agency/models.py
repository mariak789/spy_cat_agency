from django.db import models
from django.core.exceptions import ValidationError

class SpyCat(models.Model):
    name = models.CharField(max_length=120)
    years_of_experience = models.PositiveIntegerField(default=0)
    breed = models.CharField(max_length=120)
    salary = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.breed})"


class Mission(models.Model):
    cat = models.OneToOneField(
        SpyCat, on_delete=models.PROTECT, null=True, blank=True, related_name="active_mission"
    )
    complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if not self.pk:  
            return
        count = self.targets.count()
        if count < 1 or count > 3:
            raise ValidationError("A mission must have between 1 and 3 targets.")

    def __str__(self):
        return f"Mission #{self.pk} (cat={self.cat_id}, complete={self.complete})"


class Target(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name="targets")
    name = models.CharField(max_length=120)
    country = models.CharField(max_length=80)
    notes = models.TextField(blank=True, default="")
    complete = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} @ {self.country} (done={self.complete})"