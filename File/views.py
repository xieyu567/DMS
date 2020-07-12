import os
import time
import re
from .forms import RegistrationForm, LoginForm
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect, QueryDict, JsonResponse, FileResponse
from django.contrib import messages
from .models import *

# 用户登录
def loginView(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None and user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('File:index'))
        else:
            # 登陆失败
            return render(request, 'File/login.html', {'form': form,
                                                            'message': 'Wrong password. Please try again.'})
    else:
        form = LoginForm()
    return render(request, 'File/login.html', {'form': form})

#用户注销
@login_required
def logoutUser(request):
    logout(request)
    return HttpResponseRedirect("File/login.html")

# 跳到上传文件页面
@login_required
def index(request):
    return render(request, 'File/index.html')
# ajax文件上传


def fileload(request):
    if request.method == 'POST':  # 判断是否post请求
        print("1")
        myFile = request.FILES.get('file-7[]', None)  # 获取上传的文件，没有默认为None
        if not myFile:  # 判断文件是否为空
            return JsonResponse({"result": "No File For Upload"})
        print(os.path.exists('statics/filepath/'+myFile.name))
        if not os.path.exists('statics/filepath/' + myFile.name):  # 判断文件是否已经存在
            classify = request.POST.getlist('classify')  # checkbox类型的取值
            classifyStr = "".join(classify)  # 将list转成字符串输出
            loadtime = time.strftime(
                "%Y-%m-%d", time.localtime())  # 获取时间年-月-日
            # if not myFile:
            # return HttpResponse("no file for upload")
            destination = open(os.path.join(
                "statics/filepath", myFile.name), "wb+")  # 创建了一个file对象
            try:
                file = models.Filename.objects.create(
                    name=myFile.name, classify=classifyStr, time=loadtime)  # 将文件名存进数据库表中
            except:
                return JsonResponse({'result': 'File Upload Fail'})
            for chunk in myFile.chunks():  # 分块写入文件
                destination.write(chunk)
            destination.close()  # 关闭
            # return redirect(reverse(index))
            return JsonResponse({'result': 'Upload Success'})
        else:
            return JsonResponse({'result': 'File Already Exists'})


# 展示页面
def fileview(request):
    fileinfo = models.Filename.objects.all()
    nametime = {}
    for i in fileinfo:
        nametime[i.name] = i.time  # 给字典赋值
    Fnametime = list(nametime.items())
    Fnametime.reverse()
    contacts = paging(request, Fnametime)  # 分页
    # paginator = Paginator(Fnametime,3)
    # page = request.GET.get('page')
    # try:
    #     contacts = paginator.page(page)
    # except PageNotAnInteger:
    #     contacts = paginator.page(1)
    # except EmptyPage:
    #     contacts = paginator.page(paginator.num_pages)
    if request.user.is_authenticated:  # 判断用户是否登录
        Islogin = True
    else:
        Islogin = False
    return render(request, 'file_list.html', {'data': contacts, 'user': Islogin})


# 下载
# def filedown(request):
#     filename = "".join(request.GET.getlist('name'))
#     file = open('statics/filepath/'+filename, 'rb')
#     response = FileResponse(file)
#     response['Content-Type'] = 'application/octet-stream'
#     response['Content-Disposition'] = 'attachment;filename=''{}'.format(
#         escape_uri_path(filename))  # 解决下载中文文件名的问题
#     return response


# 关键字搜索
def keyQuery(request):
    keyname = request.POST.get('keyvalue')
    filename = models.Filename.objects.filter(name__contains=keyname).all()
    nametime = {}
    for i in filename:
        nametime[i.name] = i.time
    Fnametime = list(nametime.items())
    Fnametime.reverse()
    contacts = paging(request, Fnametime)
    if request.user.is_authenticated:  # 判断用户是否登录
        Islogin = True
    else:
        Islogin = False
    return render(request, "file_list.html", {'data': contacts, 'user': Islogin})


# 按照条件查询
def queryfile(request):
    classify = request.GET.getlist('classify')  # 取到前端a标签里面传来的值
    classifyStr = "".join(classify)  # 将list转成字符串
    filename = models.Filename.objects.filter(
        classify__contains=classifyStr).all()
    nametime = {}
    for i in filename:
        nametime[i.name] = i.time
    Fnametime = list(nametime.items())  # 将字典转换成items()组成的列表
    Fnametime.reverse()  # 列表反转
    contacts = paging(request, Fnametime)  # 分页
    if request.user.is_authenticated:  # 判断用户是否登录
        Islogin = True
    else:
        Islogin = False
    return render(request, 'file_list.html', {'data': contacts, 'user': Islogin})


def pageNotFound(request):
    return render(request, '404.html')


def userRegister(request):
    return render(request, 'register.html')


def unauthorized(request):
    return render(request, '401.html')


def internalServerError(request):
    return render(request, '500.html')


# 用户登录验证
def loginVerify(request):
    username = "".join(request.POST.getlist("username")
                       )  # 取到ajax传过来的username值并转化成字符串
    password = "".join(request.POST.getlist("password")
                       )  # 取到ajax传过来的password值并转化成字符串
    user = authenticate(username=username, password=password)
    if user:
        login(request, user)  # 将user存进session中
        return JsonResponse({"success": "success"})
    else:
        return JsonResponse({"error": "fail"})


# 删除文件
# 删除数据库的记录，以及filepath文件夹下的文件
def deletefile(request):
    filename = request.GET.get("filename")  # 获取要删除文件的名称
    if os.path.exists("statics/filepath/"+filename):  # 判断文件是否存在
        deleteobj = models.Filename.objects.filter(name=filename)  # 去数据库查找文件记录
        if deleteobj:  # 判断数据库是否存在文件
            try:
                os.remove("statics/filepath/" + filename)  # 删除路径下的文件
                deleteobj.delete()  # 删除数据库中的记录
            except:
                return HttpResponse(u"删除失败")
            return redirect('fileview')
        else:
            return HttpResponse(u"数据库检索不到此文件")
    else:
        return HttpResponse(u"文件不存在")


# 分页函数
def paging(request, Fnametime):
    paginator = Paginator(Fnametime, 11)
    page = request.GET.get('page')
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)
    return contacts
