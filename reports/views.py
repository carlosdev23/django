from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.parsers import MultiPartParser

from .serializers import ReportSerializer,PointcloudSerializer
from .models import Report,Pointcloud
from projects.models import Project

import os
from django import forms


from rest_framework.response import Response

from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
import boto3

from boto3 import session
from botocore.client import Config
from boto3.s3.transfer import S3Transfer
from uuid import uuid4
from pathlib import Path
from django.core.files import File

import tempfile


import environ
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Parse .env file
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

class ReportModelViewSet(mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin,
                         mixins.ListModelMixin, viewsets.GenericViewSet):
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter, ]
    parser_classes = (MultiPartParser,)

    queryset = Report.objects.all()
    serializer_class = ReportSerializer

    filterset_fields = ['project', 'type', ]
    ordering_fields = ['uploaded_on', ]
    ordering = ['-uploaded_on', ]

    search_fields = ['title', ]
    
    def create(self, request, *args, **kwargs):


        appropriateProject = Project.objects.get(pk=request.data['project'])
        #print(appropriateProject)
        
        #newupload = Report(type=5,title='baba',project_id=1)
        #newupload.file.name = './MyLasTemporaryData/test.kml'
        
        #newupload.save()

        #fsd = FileSystemStorage(location=folder) #defaults to   MEDIA_ROOT  
        #FilePath = forms.FilePathField(path = "./MyLasTemporaryData")
        #f = open("./MyLasTemporaryData/test.kml", "rb")
        #path = Path('./MyLasTemporaryData/metadata.json')
        #QueryDict = {'client':'sample','project':'1','title':'aze','type':'1'}
        #with path.open(mode='rb') as f:
        #    newupload.file = File(f, name=path.name)
        #    newupload.save()

        #filee = File(name='./MyLasTemporaryData/test.kml')
        
        

        #f = open("./MyLasTemporaryData/test.kml", "r")
        #dd = f.read()
        #fp = tempfile.TemporaryFile()
        #fp.write("./MyLasTemporaryData/test.kml")

        #   serializer = self.get_serializer(data=newupload)
        
        #serializer.is_valid(raise_exception=True)
        #result = serializer.data
        #self.perform_create(serializer)
        #headers = self.get_success_headers(serializer.data)



        ClientName = request.data['client']
        folder='MyLasTemporaryData/'
        file = request.FILES['file']
        fileName, fileExtension = os.path.splitext(request.FILES['file'].name)

        fileName = ''.join(e for e in fileName if e.isalnum())

        UNIQUEID4 = uuid4()
        if fileExtension == '.las':
            fs = FileSystemStorage(location=folder) #defaults to   MEDIA_ROOT  

            #Generate unique name
            UniqueFileName = fileName + str(UNIQUEID4) + fileExtension

            #Save the las file to be proceeded
            filename = fs.save(UniqueFileName, file)

            #Generate the potree Converter data
            #PotreeConvertion = os.system('/var/www/html/dronotdata/potreeConverter/PotreeConverter-develop/build/PotreeConverter ./MyLasTemporaryData/'+UniqueFileName+' -o ./MyLasTemporaryData/LasData/'+str(UNIQUEID4)+'/')
            PotreeConvertion = os.system('/home/dronodat/www/potreeconverter/build/PotreeConverter ./MyLasTemporaryData/'+UniqueFileName+' -o ./MyLasTemporaryData/LasData/'+str(UNIQUEID4)+'/')
            if PotreeConvertion != 0 :
                return Response("An error Occured in Potree convertion", status=500)
            
            #os.system('/var/www/html/dronotdata/potreeConverter/PotreeConverter-develop/build/PotreeConverter ./MyLasTemporaryData/'+UniqueFileName+' -o ./MyLasTemporaryData/LasData/'+str(UNIQUEID4)+'/')
            #file_name = default_storage.save(file.name, file)
            # create new bucket
            #client.put_object(Bucket='dronospace', # The path to the directory you want to upload the object to, starting with your Space name.
            #                  Key='staging/test/projects/test2.las', # Object key, referenced whenever you want to access this file later.
            #                  #Body=b'Hello, World!', # The object's contents.
            #                  SourceFile = './MyLasTemporaryData/test2.las'
            #)

            
        
        serializer = self.get_serializer(data=request.data)
        
        #serializer.is_valid(raise_exception=True)
        #result = serializer.data
        #serializer.save()
        if serializer.is_valid():
                serializer.save()
        else :
            return Response("An error Occured while saving the report to DB", status=500)
        #self.perform_create(serializer)
        #self.perform_create(serializer)
        #headers = self.get_success_headers(serializer.data)
        #device = serializer.save()

        #Save the metadataJson url to call it later

       

        if fileExtension == '.las':
            session = boto3.session.Session()
            client = session.client('s3',
                                    region_name='ams3',
                                    endpoint_url='https://ams3.digitaloceanspaces.com',
                                    aws_access_key_id=env("AWS_ACCESS_KEY_ID"),
                                    aws_secret_access_key=env("AWS_SECRET_ACCESS_KEY"),
            )

            transfer = S3Transfer(client)
            
            for root,dirs,files in os.walk('./MyLasTemporaryData/LasData/'+str(UNIQUEID4)+'/'):
                for file in files:
                    transfer.upload_file('./MyLasTemporaryData/LasData/'+str(UNIQUEID4)+'/'+file, 'dronospace', env("AWS_LOCATION")+'/'+str(ClientName)+'/projects/pointclouddata/'+str(serializer.data['id'])+'/'+file, extra_args={'ACL': 'public-read'})
                    os.remove('./MyLasTemporaryData/LasData/'+str(UNIQUEID4)+'/'+file)

            #transfer.upload_file('./MyLasTemporaryData/'+UniqueFileName, 'dronospace', 'staging/test/projects/pointclouddata/'+str(serializer.data['id'])+'/'+str(UniqueFileName))
            
            #Save the point cloud Urls
            PointCloudpath = env("AWS_LOCATION")+'/'+str(ClientName)+'/projects/pointclouddata/'+str(serializer.data['id'])
            projectId = appropriateProject.id
            filename = str(appropriateProject.name)+"_"+request.data['title']+"_"+str(serializer.data['id'])

            PointCloudObject = Pointcloud(projectid=projectId,filename=filename,path=PointCloudpath)
            PointCloudObject.save()
            
            #Remove files(las and octreeFolder)
            if os.path.exists('./MyLasTemporaryData/'+UniqueFileName):
                os.remove('./MyLasTemporaryData/'+UniqueFileName)

            os.rmdir('./MyLasTemporaryData/LasData/'+str(UNIQUEID4)+'/') 

        #return HttpResponse(serializer.data['id'])
        
        #return Response(serializer.data['id'])
        return HttpResponse("Report is added successfully",status=200)


class PointcloudModelViewSet(mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin,
                         mixins.ListModelMixin, viewsets.GenericViewSet):
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter, ]
    parser_classes = (MultiPartParser,)

    queryset = Pointcloud.objects.all()
    serializer_class = PointcloudSerializer

    filterset_fields = ['projectid', ]
    ordering_fields = ['projectid', ]
    ordering = ['-projectid', ]

    search_fields = ['filename', ]
    
   

            
