from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from .models import SpyCat, Mission, Target
from .serializers import (
    SpyCatSerializer,
    MissionSerializer,
    MissionReadSerializer,
    TargetSerializer,
)

class SpyCatViewSet(viewsets.ModelViewSet):
    queryset = SpyCat.objects.all().order_by("id")
    serializer_class = SpyCatSerializer


class MissionViewSet(viewsets.GenericViewSet,
                     mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin):
    queryset = Mission.objects.prefetch_related("targets").select_related("cat").order_by("-id")

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return MissionReadSerializer
        return MissionSerializer

    def destroy(self, request, *args, **kwargs):
        mission = self.get_object()
        if mission.cat_id is not None:
            return Response({"detail": "Cannot delete a mission already assigned to a cat."},
                            status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=["post"], url_path="assign-cat")
    @transaction.atomic
    def assign_cat(self, request, pk=None):
        mission = self.get_object()
        if mission.cat_id is not None:
            return Response({"detail": "Mission already has a cat."}, status=400)
        cat_id = request.data.get("cat_id")
        if not cat_id:
            return Response({"detail": "cat_id is required."}, status=400)
        try:
            cat = SpyCat.objects.get(pk=cat_id)
        except SpyCat.DoesNotExist:
            return Response({"detail": "Cat not found."}, status=404)
        if hasattr(cat, "active_mission"):
            return Response({"detail": "This cat already has an active mission."}, status=400)
        mission.cat = cat
        mission.save(update_fields=["cat"])
        return Response(MissionReadSerializer(mission).data, status=200)


class TargetViewSet(viewsets.GenericViewSet, mixins.UpdateModelMixin, mixins.RetrieveModelMixin):
    queryset = Target.objects.select_related("mission").all()

    def get_serializer_class(self):
        return TargetSerializer

    def partial_update(self, request, *args, **kwargs):
        target = self.get_object()
        if target.complete or target.mission.complete:
            if "notes" in request.data and request.data.get("notes") != target.notes:
                return Response({"detail": "Notes are frozen for completed target/mission."}, status=400)

        response = super().partial_update(request, *args, **kwargs)

        target.refresh_from_db()
        mission = target.mission
        if mission.targets.exists() and mission.targets.filter(complete=True).count() == mission.targets.count():
            if not mission.complete:
                mission.complete = True
                mission.save(update_fields=["complete"])
        return response