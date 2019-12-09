from django.shortcuts import render
from django.http import HttpResponse
from web.rcmain import *
from web.rcdata import *
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGE_DIR = os.path.join(BASE_DIR, 'templates/web').replace('\\', '/')


def index(request):
    return render(request, 'web/index.html')


def process(request):
    # b, h, rc_type, A_s, steel_type, mode
    # shape, rc_type, A_s, steel_type, mode
    shape_type = Shape_Type[request.POST.get('shape_type')]
    b = int(request.POST.get('b')) if request.POST.get('b').isdigit() else 0
    h = int(request.POST.get('h')) if request.POST.get('h').isdigit() else 0
    bf = int(request.POST.get('bf')) if request.POST.get('bf').isdigit() else 0
    hf = int(request.POST.get('hf')) if request.POST.get('hf').isdigit() else 0
    d_out = int(request.POST.get('d_out')) if request.POST.get('d_out').isdigit() else 0
    d_in = int(request.POST.get('d_in')) if request.POST.get('d_in').isdigit() else 0
    rc_type = RC_Type[request.POST.get('rc_type')]
    A_s = int(request.POST.get('A_s')) if request.POST.get('A_s').isdigit() else 0
    steel_type = Steel_Type[request.POST.get('steel_type')]
    mode = Mode[request.POST.get('mode')]
    shape = {'shape': shape_type, 'b': b, 'h': h, 'bf': bf, 'hf': hf, 'd_out': d_out, 'd_in': d_in}
    anime_checked = bool(request.POST.get('anime'))

    # print(type(shape_type), shape_type)
    # print(type(b), b)
    # print(type(h), h)
    # print(type(rc_type), rc_type)
    # print(type(A_s), A_s)
    # print(type(steel_type), steel_type)
    # print(type(mode), mode)
    # test
    rc_set = RC(shape, rc_type, A_s, steel_type, mode)
    # print(rc_set.alpha, rc_set.beta)
    image_name = rc_set.plot()
    if anime_checked:
        anime_name = rc_set.display()
    else:
        anime_name = "loading.gif"

    return render(request, 'web/process.html',
                  {'alpha': rc_set.alpha, 'beta': rc_set.beta, 'image': image_name, 'anime': anime_name})


def images(request):
    image_path = IMAGE_DIR + request.path
    # print(image_path)
    pic = open(image_path, "rb")
    # os.remove(image_path) 如何删除
    return HttpResponse(pic.read(), content_type="image")
