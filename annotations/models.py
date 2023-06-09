import uuid
from pathlib import Path

from django.contrib.auth import get_user_model
from django.contrib.gis.db import models


class Annotation(models.Model):
    creator = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    mission = models.ForeignKey(
        "projects.Mission", on_delete=models.CASCADE, related_name="annotations"
    )
    created_on = models.DateTimeField(auto_now_add=True)
    coordinates = models.PointField()
    note = models.TextField(blank=True)

    class Meta:
        ordering = [
            "-created_on",
        ]

    @property
    def pictures_root_path(self):
        return f"missions/{self.pk}/pictures/"

    @property
    def coordinates_list(self):
        return [coords for coords in self.coordinates]


def get_picture_upload_path(instance, filename):
    *_, extension = filename.split(".")
    return Path(instance.annotation.pictures_root_path) / f"{uuid.uuid4()}.{extension}"


class AnnotationPicture(models.Model):
    annotation = models.ForeignKey(
        Annotation, on_delete=models.CASCADE, related_name="pictures"
    )
    picture = models.ImageField(upload_to=get_picture_upload_path)
    created_on = models.DateTimeField(auto_now_add=True)
