import datetime
import pathlib
import tempfile

from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.core.files import File
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema, no_body
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.reverse import reverse
import pdfkit

from reports.models import Report
from reports.serializers import ReportSerializer
from .models import Project, Mission
from .serializers import ProjectSerializer, MissionSerializer
from .utils import get_months


class WorkflowModelViewSetMixin:
    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
        SearchFilter,
    ]
    filterset_fields = [
        "assignees",
        "status",
    ]
    ordering_fields = [
        "created_on",
        "started_on",
        "finished_on",
    ]
    ordering = [
        "-created_on",
        "-started_on",
        "-finished_on",
    ]

    search_fields = [
        "name",
    ]

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        is_manager = self.request.user.groups.filter(name="manager").exists()
        if not is_manager:
            queryset = queryset.filter(assignees__id=self.request.user.id)
        return queryset

    def get_queryset(self):
        queryset = super(WorkflowModelViewSetMixin, self).get_queryset()
        return queryset.prefetch_related("assignees")


class ProjectModelViewSet(WorkflowModelViewSetMixin, viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    @swagger_auto_schema(
        methods=["post"], request_body=no_body, responses={200: ReportSerializer()}
    )
    @action(methods=["POST"], detail=True)
    def generate_report(self, request, pk=None):

        options = {
            "dpi": 365,
            "page-size": "A4",
            "margin-top": "0in",
            "margin-right": "0in",
            "margin-bottom": "0in",
            "margin-left": "0in",
            'footer-right': '[page] of [topage]'
        }

        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as header_html:
            options["header-html"] = header_html.name
            header_html.write(
                render_to_string("projects/project_full_report_header.html", {}).encode(
                    "utf-8"
                )
            )

        # with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as footer_html:
        #     options["footer-html"] = footer_html.name
        #     footer_html.write(
        #         render_to_string("projects/project_full_report_footer.html", {}).encode(
        #             "utf-8"
        #         )
        #     )

        project = self.get_object()
        html_report = render_to_string(
            "projects/project_full_report.html",
            {
                "project": project,
                "user": request.user,
                "months": get_months(project.created_on),
            },
        )
        output_pdf_path = "pdfreport.pdf"
        pdfkit.from_string(html_report, output_pdf_path, options=options)
        report = Report.objects.create(
            title=f"project-{project.id}-report-{datetime.datetime.now()}",
            project_id=project.id,
            type=Report.TypeChoices.PDF.value,
            file=File(
                open(output_pdf_path, mode="br"),
                name=f"project-{project.id}-report.pdf",
            ),
            processed=True,
        )
        pathlib.Path(output_pdf_path).unlink()
        return redirect(reverse("reports:report-detail", (report.pk,)))


class MissionModelViewSet(WorkflowModelViewSetMixin, viewsets.ModelViewSet):
    queryset = Mission.objects.all()
    serializer_class = MissionSerializer
    filterset_fields = WorkflowModelViewSetMixin.filterset_fields + [
        "project",
        "type",
    ]

    def get_queryset(self):
        queryset = super(MissionModelViewSet, self).get_queryset()
        queryset = queryset.prefetch_related("geo_2d_locations", "geo_3d_locations")
        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            instance = self.get_object()
            if request.data.get("send_email"):
                instance.send_mission_email_notification("delete")
            self.perform_destroy(instance)
        except Http404:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["POST"], detail=True)
    def send_email(self, request, pk=None):
        instance = get_object_or_404(Mission, pk=pk)
        if instance.owners:
            instance.send_mission_email_notification("details")

        return Response(status=status.HTTP_200_OK)
