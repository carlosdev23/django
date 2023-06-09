from email.policy import default
from django.db.models import Sum, F, FloatField
from django.db.models.fields.json import KeyTextTransform
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.functions import Cast, Coalesce
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField
from django.template.loader import get_template


from django.utils import timezone

from datetime import timedelta

from commons.utils.email import send_email

from annotations.models import Annotation
from geo.models import Powerline


class BaseWorkFLow(models.Model):
    class StatusChoices(models.IntegerChoices):
        PENDING = 1, _("Pending")
        IN_PROCESS = 2, _("In Process")
        DONE = 3, _("Done")

    class Meta:
        abstract = True

    name = models.CharField(
        _("name"),
        max_length=64,
        blank=True,
    )

    assignees = models.ManyToManyField(
        get_user_model(),
        related_name="+",
    )
    status = models.SmallIntegerField(
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
    )

    created_on = models.DateTimeField(
        auto_now_add=True,
        editable=False,
    )
    started_on = models.DateTimeField(
        null=True,
        blank=True,
    )
    finished_on = models.DateTimeField(
        null=True,
        blank=True,
    )

    def update_status(self, status):
        if self.status != status:
            self.status = status

            if self.status == self.StatusChoices.DONE.value:
                self.finished_on = timezone.now()
        return self.status

    @property
    def status_display(self):
        return self.StatusChoices(self.status).label


class Project(BaseWorkFLow):
    assignees = models.ManyToManyField(
        get_user_model(),
        related_name="projects",
    )
    address = models.CharField(
        _("address"),
        max_length=256,
        blank=True,
    )
    contact_person = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        related_name="+",
    )

    @property
    def pending_missions(self):
        return self.missions.filter(status=self.StatusChoices.PENDING)

    @property
    def under_processing_missions(self):
        return self.missions.filter(status=self.StatusChoices.IN_PROCESS)

    @property
    def completed_missions(self):
        return self.missions.filter(status=self.StatusChoices.DONE)

    @property
    def trimming_missions(self):
        return self.missions.filter(type=Mission.TypeChoices.TRIMMING.value)

    @property
    def flight_missions(self):
        return self.missions.filter(type=Mission.TypeChoices.FLIGHT.value)

    @property
    def trimming_missions_start_date(self):
        first_mission = (
            self.missions.filter(type=Mission.TypeChoices.TRIMMING.value)
            .order_by("started_on")
            .first()
        )
        if first_mission:
            return first_mission.started_on

    @property
    def flight_missions_start_date(self):
        first_mission = (
            self.missions.filter(type=Mission.TypeChoices.FLIGHT.value)
            .order_by("started_on")
            .first()
        )
        if first_mission:
            return first_mission.started_on

    @property
    def trimming_missions_end_date(self):
        last_mission = (
            self.missions.filter(type=Mission.TypeChoices.TRIMMING.value)
            .order_by("finished_on")
            .first()
        )
        if last_mission:
            return last_mission.finished_on

    @property
    def flight_missions_end_date(self):
        last_mission = (
            self.missions.filter(type=Mission.TypeChoices.FLIGHT.value)
            .order_by("finished_on")
            .first()
        )
        if last_mission:
            return last_mission.finished_on

    @cached_property
    def covered_area(self):

        return round(
            Powerline.objects.filter(project=self)
            .annotate(
                intersecting_data=Cast(
                    KeyTextTransform("neighbours_area", "properties"),
                    output_field=FloatField(),
                )
            )
            .aggregate(Sum("intersecting_data"))
            .get("intersecting_data__sum"),
            2,
        )

    @property
    def annotations(self):
        return Annotation.objects.filter(mission__in=self.missions.all())

    @property
    def area(self):
        return round(
            Powerline.objects.filter(project=self)
            .annotate(
                intersecting_data=Cast(
                    KeyTextTransform(
                        "area", KeyTextTransform("intersecting_data", "properties")
                    ),
                    output_field=FloatField(),
                )
            )
            .aggregate(Sum("intersecting_data"))
            .get("intersecting_data__sum"),
            2,
        )


class Mission(BaseWorkFLow):
    class TypeChoices(models.IntegerChoices):
        FLIGHT = 1, _("Flight")
        TRIMMING = 2, _("Trimming")

    assignees = models.ManyToManyField(
        get_user_model(),
        related_name="missions",
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="missions",
    )
    send_notification_email = models.BooleanField(default=False)
    is_reminder_sent = models.BooleanField(default=False)
    is_notification_sent = models.BooleanField(default=False)
    owners = ArrayField(models.EmailField(max_length=254), default=list, blank=True)
    type = models.SmallIntegerField(
        choices=TypeChoices.choices,
    )

    @property
    def type_display(self):
        return self.TypeChoices(self.type).label

    def send_mission_email_notification(self, status=None):
        if self.send_notification_email:
            name = self.name
            type = self.type_display
            assignees = self.assignees
            assignees_list = []

            for assignee in assignees.all():
                assignees_list.append(assignee.name)

            start_date = self.started_on

            context = {
                "name": name,
                "type": type,
                "assignees": assignees_list,
                "start_date": start_date,
                "covered_areas": self.geo_2d_locations.all(),
            }

            if status == "details":
                context["status"] = "Details"
                send_email(
                    f"Details: Mission {name}",
                    "projects/email/email_notification_message.html",
                    self.owners,
                    context,
                )
                return

            if timezone.now().date() >= start_date.date() - timedelta(days=1):
                if not self.is_reminder_sent:
                    context["status"] = "Reminder"
                    send_email(
                        f"Reminder: Mission {name}",
                        "projects/email/email_notification_message.html",
                        self.owners,
                        context,
                    )
                    self.is_reminder_sent = True
                    self.save()

                    return

            if timezone.now().date() >= start_date.date() - timedelta(days=14):
                if self.is_notification_sent:
                    if status == "delete":
                        context["status"] = "Cancelled"
                        send_email(
                            f"Cancelled: Mission {name}",
                            "projects/email/email_notification_message.html",
                            self.owners,
                            context,
                        )
                        return

                    if status == "update":
                        context["status"] = "Update"
                        send_email(
                            f"Updated: Mission {name}",
                            "projects/email/email_notification_message.html",
                            self.owners,
                            context,
                        )
                        return
                else:
                    context["status"] = "Notification"
                    send_email(
                        f"Notification: Mission {name}",
                        "projects/email/email_notification_message.html",
                        self.owners,
                        context,
                    )
                    self.is_notification_sent = True
                    self.save()
                    return

        return
