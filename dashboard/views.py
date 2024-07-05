from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.decorators import api_view, parser_classes
from django.conf import settings
from rest_framework.pagination import PageNumberPagination
from .serializers import *
from datetime import datetime
from .models import UploadTasks
from .tasks import *
import os

def login(request):
    context = {
        'title' : f"Login | {settings.SITE_NAME}"
    }

    return render(request, "login.html", context)
 
def upload_data_view(request):
    context = {
        'title' : f"Upload Data | {settings.SITE_NAME}"
    }
        
    return render(request, "dashboard_upload.html", context) 

def query_builder(request):
    context = {
        'title' : f"Query Builder | {settings.SITE_NAME}"
    
    }
    return render(request, "dashboard_query_builder.html", context) 

def users(request):
    context = {
        'title' : f"Users | {settings.SITE_NAME}"
    }

    return render(request, "dashboard_users.html", context)

class ChunkedUploadView(APIView):
    parser_classes = [MultiPartParser]

    def get(self,request,task_id):
        try:
            taskObj = UploadTasks.objects.get(task_id = task_id)
            response = {
                'task_id': str(task_id),
                'status': str(taskObj.task_state),
                'state':True,
            }
            if taskObj.task_state in ['FINISHED', 'FAILED']:
                taskObj.delete()
            return Response(response)
        except Exception as e:
            return Response({'state':False,'message':'Task FINISHED/FAILED or DOES NOT EXIST'})

    def post(self, request,task_id):
        file = request.FILES['file']
        chunk_number = int(request.data['chunkNumber'])
        total_chunks = int(request.data['totalChunks'])
        file_name = request.data['fileName']
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp', file_name)
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir, exist_ok=True)

        chunk_file_path = os.path.join(temp_dir, f'{file_name}_part{chunk_number}')
        with open(chunk_file_path, 'wb') as chunk_file:
            for chunk in file.chunks():
                chunk_file.write(chunk)

        if chunk_number == total_chunks:
            final_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
            os.makedirs(final_dir, exist_ok=True)

            final_file_path = os.path.join(final_dir, file_name)
            with open(final_file_path, 'wb') as final_file:
                for i in range(1, total_chunks + 1):
                    part_path = os.path.join(temp_dir, f'{file_name}_part{i}')
                    with open(part_path, 'rb') as part_file:
                        final_file.write(part_file.read())

            for i in range(1, total_chunks + 1):
                os.remove(os.path.join(temp_dir, f'{file_name}_part{i}'))
            os.rmdir(temp_dir)

            task = process_csv.delay(final_file_path)            
            UploadTasks.objects.create(task_id=task.id)
            return Response({'status': 'done','task_id':task.id})

        return Response({'status': 'chunk uploaded'})


@api_view(['GET'])
def industries_get(request):
    industries = Industry.objects.all()
    serializer = IndustrySerializer(industries, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def query_data(request):
    data = request.data
    industry = data['industry'].lower()
    keyword = data['keyword'].lower()
    year_founded = datetime.strptime(data['year_founded'], '%Y-%m-%d').year if data['year_founded'] else ""
    city = data['city'].lower()
    state = data['state'].lower()
    country = data['country'].lower()
    employees_from = int(data['employees_from']) if data['employees_from'] else ""
    employees_to = int(data['employees_to']) if data['employees_to'] else ""

    print(industry,keyword,year_founded,city,state,country,employees_from,employees_to)
    
    filter_kwargs = {}
    if industry:
        filter_kwargs['industry'] = industry
    # if keyword:
    #     filter_kwargs['company_name__icontains'] = keyword
    if year_founded:
        filter_kwargs['year_founded__year'] = year_founded
    # if city:
    #     filter_kwargs['locality__icontains'] = city
    # if state:
    #     filter_kwargs['locality__icontains'] = state
    if country:
        filter_kwargs['country__icontains'] = country
    if employees_from:
        filter_kwargs['current_estimate__gte'] = employees_from
    if employees_to:
        filter_kwargs['current_estimate__lte'] = employees_to

    company_data = CompanyData.objects.filter(**filter_kwargs).order_by('id')

    paginator = PageNumberPagination()
    result_page = paginator.paginate_queryset(company_data, request)

    serializer = CompanyDataSerializer(result_page, many=True)

    return paginator.get_paginated_response(serializer.data)