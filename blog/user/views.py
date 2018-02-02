from django.shortcuts import render, redirect
from .forms import LoginForm, RegisterForm
from .models import User
from PIL import Image
import random
import os

# Create your views here.
# 登陆
def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        # 判断表单提交是否存在空值 存在空值则无效
        if form.is_valid():
            # 执行表单内的验证方法 返回user和验证结果
            user, chk_password_result = form.chk_passwd()
            # 验证成功chk结果会返回True 否则会返回False
            if chk_password_result:
                # 将用户id存入session
                request.session['uid'] = user.id
                # 回到首页
                return redirect('/user/info/')
            else:
                # 否则返回登陆页 并且提示表单验证错误
                return render(request, 'login.html', {'errors': form.errors})
    return render(request, 'login.html')

# 注册视图
def register(request):
    if request.method == 'POST':
        # 验证表达输入内容
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            # 因为该表单与模型关联 可以直接调用save方法 设置不提交 在下面手动提交
            user = form.save(commit=False)
            user.save()
            # 为了防止图片过多消耗资源在这里存储缩略图
            img = Image.open('medias/' + str(user.head))
            img.thumbnail((64, 64))
            img.save('medias/'+str(user.head))

            # 设置用户为登陆状态 设置session
            request.session['uid'] = user.id
            return redirect('/post/index/')
        else:
            return render(request, 'register.html', {'errors': form.errors})
    return render(request, 'register.html')

# 用户信息
def info(request):
    # 在中间件中已经验证过这里直接判断是否有设置过的额属性即可, 有则返回 无则为None
    user = getattr(request, 'user', None)
    if user:
        return render(request, 'info.html', {'user': user})
    return redirect('/user/login/')

# 用户注销
def logout(request):
    # 清楚指定的键值
    request.session.flush()
    return redirect('/post/index')

def update_head(request):
    if request.method == 'POST':
        user = getattr(request, 'user', None)

        # 在更新头像之前 先删除掉以前的头像
        # 担心误操作已经删除过头像所以这这里try一下
        try:
            os.remove('./medias/' + str(user.head))
        except:
            pass

        # 获取上传的文件对象
        image = request.FILES.get('head')
        filename = ''.join([random.choice('1324345656789ewretrytuyusfdgfh') for i in range(20)]) + os.path.splitext(image.name)[1]
        full_path = './medias/' + str(filename)
        with open(full_path, 'wb') as file:
            for chunk in image.chunks():
                file.write(chunk)
        if user:
            # 保存数据库
            user.head = filename
            user.save()

            # 做成缩略图
            img = Image.open(full_path)
            img.thumbnail((64, 64))
            img.save(full_path)
    return redirect('/user/info/')