import os

from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, HttpResponse
from .models import Uploadfile
from .remove_bg.remove_bg import remove_image
from .check_nudenet.check_nudenet import check_nude
from django.conf import settings
import json
from datetime import datetime


def index(request):
    return render(request, "index.html")


def send_files(request):
    if request.method == 'POST':
        myfile = request.FILES['uploadfiles']
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        Uploadfile(name=str(timestamp), my_files=myfile).save()
        path = get_path(timestamp)
        name = get_my_files(timestamp)
        if name.lower().endswith(('.png', '.jpg', '.jpeg')):
            unsafe = check_nude(path)
            if unsafe * 100 > 50:
                return invalid_photo(path)
            else:
                return success_photo(name)
        else:
            return invalid_photo(path)


def get_path(name):
    file = Uploadfile.objects.get(name=str(name))
    path = os.path.join(os.getcwd(), 'media/' + str(file.my_files))
    print(path)
    return path


def get_my_files(name):
    file = Uploadfile.objects.get(name=str(name))
    return str(file.my_files)


def invalid_photo(path):
    data = {
        'message': 'Invalid photo',
        'status': '400'
    }
    os.remove(path)
    return HttpResponse(json.dumps(data), content_type='application/json')


def success_photo(name):
    image = remove_image(name)
    data = {
        'message': 'Success',
        'status': '200',
        'image': str(settings.HOST + image)
    }
    return HttpResponse(json.dumps(data), content_type='application/json')
