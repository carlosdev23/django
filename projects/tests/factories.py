from datetime import datetime
import factory

from projects.models import Project, Mission

class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project
    
    name = 'test project'

class MissionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Mission

    project  = factory.SubFactory(ProjectFactory)
    name = 'test mission'
    type = 1
    started_on = datetime(2022, 8, 24)
    finished_on = datetime(2022, 8, 25)
    send_notification_email=True
    owners=['test@email.com']