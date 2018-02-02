"""blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from user import views as user_view
from post import views as post_view
from . import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'', post_view.index),

    # user_view视图
    path(r'user/login/', user_view.login),
    path(r'user/register/', user_view.register),
    path(r'user/info/', user_view.info),
    path(r'user/logout/', user_view.logout),
    path(r'user/update_head/', user_view.update_head),

    # post_view视图
    # index视图匹配带参和不带参两种
    path(r'post/index/', post_view.index),
    path(r'post/index/<int:start>/', post_view.index),
    path(r'post/publish/', post_view.publish),
    path(r'post/detail/', post_view.detail),
    # 评论
    path(r'post/comment/<int:aid>/', post_view.comment),
    # 搜索
    path(r'post/search/', post_view.search),
    # 编辑文章
    path(r'post/editor/', post_view.editor),
    # 文章删除
    path(r'post/delete/', post_view.delete)
]

# 添加media路由
urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
