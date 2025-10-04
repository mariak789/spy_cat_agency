import json
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from agency.models import SpyCat, Mission, Target

@pytest.fixture
def client():
    return APIClient()

@pytest.mark.django_db
def test_create_cat_and_list(client, monkeypatch):
    from agency import serializers
    monkeypatch.setattr(serializers, "_BREEDS_CACHE", {"bengal", "siamese"})
    r = client.post("/api/cats/", {
        "name": "Mr. Whiskers",
        "years_of_experience": 3,
        "breed": "Bengal",
        "salary": "5000.00"
    }, format="json")
    assert r.status_code == 201
    r = client.get("/api/cats/")
    assert r.status_code == 200
    assert r.json()[0]["name"] == "Mr. Whiskers"

@pytest.mark.django_db
def test_create_mission_targets_and_autocomplete(client):
    cat = SpyCat.objects.create(name="Cat", years_of_experience=1, breed="Bengal", salary="1000.00")
    r = client.post("/api/missions/", {
        "cat": None,
        "targets": [
            {"name": "A", "country": "IT", "notes": "", "complete": False},
            {"name": "B", "country": "FR", "notes": "", "complete": False}
        ]
    }, format="json")
    assert r.status_code == 201
    mission_id = r.json()["id"]

    
    r = client.post(f"/api/missions/{mission_id}/assign-cat/", {"cat_id": cat.id}, format="json")
    assert r.status_code == 200
    targets = Target.objects.filter(mission_id=mission_id).order_by("id")
    for t in targets:
        rr = client.patch(f"/api/targets/{t.id}/", {"complete": True}, format="json")
        assert rr.status_code in (200, 202)

    r = client.get(f"/api/missions/{mission_id}/")
    assert r.status_code == 200
    assert r.json()["complete"] is True

@pytest.mark.django_db
def test_notes_frozen_when_completed(client):
    r = client.post("/api/missions/", {
        "cat": None,
        "targets": [{"name": "A", "country": "IT", "notes": "x", "complete": True}]
    }, format="json")
    tid = Target.objects.get(mission_id=r.json()["id"]).id
    r = client.patch(f"/api/targets/{tid}/", {"notes": "new"}, format="json")
    assert r.status_code == 400