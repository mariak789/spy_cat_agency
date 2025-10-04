from django.contrib import admin
from .models import SpyCat, Mission, Target

@admin.register(SpyCat)
class SpyCatAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "breed", "years_of_experience", "salary")

class TargetInline(admin.TabularInline):
    model = Target
    extra = 0

@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ("id", "cat", "complete", "created_at")
    inlines = [TargetInline]