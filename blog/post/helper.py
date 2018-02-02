import logging

from redis import Redis
from django.core.cache import cache
from django.conf import settings

from post.models import Article

# 使redis配置生效 **代表将字典转换为键=值得形式
rds = Redis(**settings.REDIS)
logger = logging.getLogger('statistic')

# 定义页面缓存装饰器
def page_cache(timeout):
    def wrap1(view_func):
        def wrap2(request, *args, **kwargs):

            # 根据返回页面的url创建键
            key = 'PAGES-%s' % request.get_full_path()

            # 获取cache里面对应的值 获取则为值 否则为None
            response = cache.get(key)

            # 判断是否为None 不是则直接返回 是的话 先获取值 存入缓存 然后返回值
            if response is not None:
                print('RETURN FROM CACHE')
                return response
            else:
                print('RETURN FROM VIEW')

                # 执行视图函数获取视图函数返回的response 存入缓存
                response = view_func(request, *args, **kwargs)

                # 添加入缓存
                cache.set(key, response, timeout)
                return response
        return wrap2
    return wrap1

# 记录文章的点击次数
def set_click_num(aid, count=1):

    # Redis Zincrby 命令对有序集合中指定成员的分数加上增量 increment
    # 在这个函数中设置了初始count 后面的点击会在这个基础上每次叠加一个count的默认值 也就是每次点击加1
    # 命令格式 conn.zincrby(变量 key val)
    # 存入的是个有序的集合 会按val从达到小进行排序
    rds.zincrby('article-click', aid, count)

# 取出top(n)的文章
def get_article_top(number):

    # Redis Zrevrange 命令返回有序集中，指定区间内的成员。
    # 根据val的范围拿出有序集合的前10条 命令与上者类似、
    # ``withscores`` indicates to return the scores along with the values
    #   The return type is a list of (value, score) pairs  设置为True返回的列表中的元素是元组
    articles_click = rds.zrevrange('article-click', 0, number, withscores=True)

    # 由于存储的是字符型的 所以需要先转换类型
    articles_click = [[int(aid), int(count)] for aid, count in articles_click]

    # 取出所有的文章id 并转换成文章实例
    aid_list = [row[0] for row in articles_click]

    # 批量查询并原来列表中的aid转换为文章实例
    # 批量查询的返回值是 {5: <Article: Article object (5)>, 6: <Article: Article object (6)>, 9: <Article: Article object (9)>}
    # 以aid为键 以查询到的对象为值得字典
    articles = Article.objects.in_bulk(aid_list)
    # print('----------------------', articles)

    # 在这里必须以内部列表作为一个整体进行变历 否则不能改变内部列表中的值
    for row in articles_click:
        aid = row[0]
        row[0] = articles[aid]

    return articles_click

# 删除redis中已经删除的文章
def delete_article_key(aid):
    # 有序集合的操作前面都是z开头
    rds.zrem('article-click', aid)

# 日志文件写入
def statistic(viem_func):
    def wrap1(request, *args, **kwargs):
        # 获得response
        response = viem_func(request, *args, **kwargs)
        #　状态码
        if response.status_code == 200:
            ip = request.META['REMOTE_ADDR']
            aid = request.GET.get('aid')
            # 将ip和aid写入日志文件
            logger.info('%s %s' % (ip, aid))
        return response
    return wrap1





