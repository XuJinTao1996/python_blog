from django.shortcuts import render, redirect
from .models import Article, Tags, Realtion_Article_Tags, Comment
from .helper import page_cache
from user.models import User
from .helper import set_click_num, get_article_top, statistic, delete_article_key
from user.helper import check_permission
from math import ceil
# Create your views here.


# 首页文章展示
@page_cache(2)
def index(request, start=1):
    # 用于标识首页的特殊性
    view_name = 'index'

    # 获得文章的数目
    article_num = Article.objects.count()

    # 每页分5条 总页数
    pages_num = ceil(article_num / 5)
    start = (start - 1) * 5

    # 取出当前页文章并排序
    articles = Article.objects.all().order_by('-date')[start: start + 5]

    # 生成所有页数
    page_num_list = [i for i in range(1, pages_num + 1)]
    uid = request.session.get('uid')

    # 获得top(n)的文章
    articles_count = get_article_top(10)

    # 默认无用户登陆
    user = None
    if uid:
        user = User.objects.get(id=uid)
    return render(request, 'index.html', {'articles': articles, 'user': user, 'pages_num_list': page_num_list, 'view_name': view_name,
                                          'articles_count': articles_count})

# 文章发表 还需要判断文章标题与内容是否输入
@check_permission('user')
def publish(request):
    if request.method == 'POST':

        # 创建文章 create方法会自动commit
        if request.POST.get('title') and request.POST.get('content'):
            article = Article.objects.create(title=request.POST['title'], content=request.POST['content'])

            # 创建标签, 默认标签以,号隔开
            tags = request.POST.get('tags')
            if tags:
                tags_list = tags.strip().split(',')

                # 使用模型内的自定义创建方法 创建标签
                tags = Tags.create_tags(tag_names=tags_list, aid=article.id)
                return redirect('/post/index/')
    return render(request, 'publish.html')

# 文章详情
@statistic
def detail(request):

    # 获取文章
    aid = request.GET.get('aid')
    if aid:
        article = Article.objects.get(id=aid)
        comments = Comment.objects.filter(aid=article.id)
        set_click_num(aid)
        return render(request, 'detail.html', {'article': article, 'comments': comments})
    else:
        return redirect('/post/index/')

# 评论 !需要设置权限
@check_permission('user')
def comment(request, aid):
    uid = request.session.get('uid')
    cont = request.POST.get('comment')

    # 获取之前跳转页面的地址
    before_url = request.META.get('HTTP_REFERER')

    # 如果用户未登录 评论为无效
    if aid and uid:
        if cont.strip() != '':
            # 获取当前用户
            user = User.objects.get(id=uid)
            comment = Comment.objects.create(aid=aid, name=user.username, content=cont)
    return redirect(before_url)

# 搜索 模糊查找
@page_cache(2)
def search(request):
    if request.method == 'POST':
        search_content = request.POST.get('search_content')

        # # # 如果搜索内容为空 直接返回之前的页面 不搜索
        if search_content.strip() == '':
            return redirect(request.META.get('TTP_REFERERH'))

        # 根据内容继续搜索 并对返回结果进行排序
        articles = Article.objects.filter(content__contains=search_content.strip())

        if articles:
            # 返回内容 内容会在模板中用过滤器进行过滤
            return render(request,'search.html' ,{'articles': articles})

    # 返回搜索界面
    return render(request, 'search.html')

# 编辑文章
@check_permission('admin')
def editor(request):
    aid = request.GET.get('aid')
    if aid is None:
        return redirect('/post/detail/?aid=%s' % aid)
    article = Article.objects.get(id=int(aid))
    if request.method == 'POST':
        title = request.POST.get('title').strip()
        content = request.POST.get('content').strip()
        tags = request.POST.get('tags').strip()
        if title or content or tags:
            print('************************************')
            tags_list = tags.split(',')
            article.title = title
            article.content = content
            article.updata_tags(tags_list)
            article.save()
        return redirect('/post/detail/?aid=%s' % aid)
    tags = ','.join([tag.name for tag in article.tags])
    return render(request, 'editor.html', {'article': article, 'tags': tags})

# 文章删除
@check_permission('admin')
def delete(request):
    aid = request.GET.get('aid')
    if aid:
        delete_article_key(aid)
        article = Article.objects.get(id=aid)
        article.del_all_relation()
        article.delete()
        comments = Comment.objects.filter(aid=aid)
        for comment in comments:
            comment.delete()
        return redirect('/post/index/')
    return redirect('/post/index/')
