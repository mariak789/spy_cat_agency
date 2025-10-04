import os
import requests
from rest_framework import serializers
from .models import SpyCat, Mission, Target
from django.db import transaction

_BREEDS_CACHE = None

def fetch_breeds():
    global _BREEDS_CACHE
    if _BREEDS_CACHE is not None:
        return _BREEDS_CACHE
    url = "https://api.thecatapi.com/v1/breeds"
    headers = {}
    api_key = os.getenv("THECATAPI_KEY")
    if api_key:
        headers["x-api-key"] = api_key
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    _BREEDS_CACHE = {b["name"].lower() for b in resp.json()}
    return _BREEDS_CACHE


class SpyCatSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpyCat
        fields = ["id", "name", "years_of_experience", "breed", "salary"]

    def validate_breed(self, value):
        breeds = fetch_breeds()
        if value.lower() not in breeds:
            raise serializers.ValidationError("Invalid cat breed (checked via TheCatAPI).")
        return value


class TargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Target
        fields = ["id", "mission", "name", "country", "notes", "complete"]
        read_only_fields = ["mission"]

    def validate(self, data):
        mission = self.instance.mission if self.instance else self.context.get("mission")
        if self.instance:
            if self.instance.complete or self.instance.mission.complete:
                if "notes" in self.initial_data and self.initial_data["notes"] != self.instance.notes:
                    raise serializers.ValidationError("Notes are frozen for completed target/mission.")
        if mission and mission.complete and ("notes" in data or "complete" in data):
            if self.partial:
                raise serializers.ValidationError("Mission is completed. Targets are frozen.")
        return data


class MissionCreateTarget(serializers.Serializer):
    name = serializers.CharField(max_length=120)
    country = serializers.CharField(max_length=80)
    notes = serializers.CharField(allow_blank=True, required=False, default="")
    complete = serializers.BooleanField(required=False, default=False)


class MissionSerializer(serializers.ModelSerializer):
    targets = MissionCreateTarget(many=True, write_only=True, required=True)
    targets_detail = TargetSerializer(source="targets", many=True, read_only=True)
    cat = serializers.PrimaryKeyRelatedField(queryset=SpyCat.objects.all(), allow_null=True, required=False)

    class Meta:
        model = Mission
        fields = ["id", "cat", "complete", "targets", "targets_detail", "created_at"]
        read_only_fields = ["complete", "created_at"]

    def validate(self, data):
        targets = self.initial_data.get("targets", [])
        if not (1 <= len(targets) <= 3):
            raise serializers.ValidationError("A mission must have between 1 and 3 targets.")
        cat = data.get("cat")
        if cat and hasattr(cat, "active_mission"):
            raise serializers.ValidationError("This cat already has an active mission.")
        return data

    @transaction.atomic
    def create(self, validated_data):
        targets_payload = validated_data.pop("targets")
        mission = Mission.objects.create(**validated_data)
        for t in targets_payload:
            Target.objects.create(mission=mission, **t)
        if mission.targets.exists() and mission.targets.filter(complete=True).count() == mission.targets.count():
            mission.complete = True
            mission.save(update_fields=["complete"])
        return mission


class MissionReadSerializer(serializers.ModelSerializer):
    targets = TargetSerializer(many=True, read_only=True)

    class Meta:
        model = Mission
        fields = ["id", "cat", "complete", "targets", "created_at"]