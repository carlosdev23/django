from fileinput import filename
import os

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class Pointcloud(models.Model):
    projectid = models.IntegerField()
    filename = models.CharField(max_length=500)
    path = models.CharField(max_length=500)
    uploaded_on = models.DateTimeField(auto_now_add=True, editable=False, )

    class Meta:
        ordering = ['projectid', ]



class BaseReport(models.Model):
    class Meta:
        abstract = True

    uploaded_on = models.DateTimeField(auto_now_add=True, editable=False, )
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='reports', )

    @staticmethod
    def get_file_upload_path(instance, filename):
        name, extension = os.path.splitext(filename)
        
        return f'projects/{instance.project.id}/reports/{name}--{timezone.now()}{extension}'


class Report(BaseReport):
    class TypeChoices(models.IntegerChoices):
        KML = 1, _('kml')
        PDF = 2, _('pdf')
        XLSX = 3, _('xlsx')
        LAS = 4, _('las')
        METADATA = 5, _('METADATA')

    file = models.FileField(upload_to=BaseReport.get_file_upload_path, )
    type = models.SmallIntegerField(choices=TypeChoices.choices, )
    title = models.CharField(_('title'), max_length=256, blank=True, )
    processed = models.BooleanField(default=False)
    details = models.JSONField(default=dict)

    class Meta:
        ordering = ['uploaded_on', ]

    def delete(self, using=None, keep_parents=False):
        if self.file:
            self.file.delete(save=False)

            #If it's a las report we remove converted data as well
            if self.type == 4:
                Pointcloud.objects.filter(path__contains='pointclouddata/'+str(self.id)).delete()

        return super(Report, self).delete(using=using, keep_parents=keep_parents)
