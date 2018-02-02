from django.db import models
from django.utils.functional import cached_property

# Create your models here.
# 文章模型
class Article(models.Model):
    # 文章标题
    title = models.CharField(max_length=128)
    # 创建时间 默认为系统当前时间
    date = models.DateTimeField(auto_now_add=True)
    # 文章内容
    content = models.TextField()

    # 查询文章的标签 自定义函数
    @property
    def tags(self):
        # 找到与当前博客所对应所有的标签 通过关系表 只通过一个字段tid获取会增加效率
        tags = Realtion_Article_Tags.objects.filter(aid=self.id).only('tid')
        # 获取所有标签的id
        tag_ids = [t.tid for t in tags]
        # 返回所有符合条件的标签对象
        return Tags.objects.filter(id__in=tag_ids)

    # 更新标签
    def updata_tags(self, tagnames):
        # 原来的标签
        old_tags_name = set([tag.name for tag in self.tags])
        # 获取需要新增加的标签 删除新标签中不存在的标签
        need_add = set(tagnames) - old_tags_name
        need_delete = old_tags_name - set(tagnames)

        # 创建新的关系
        Tags.create_tags(need_add, self.id)
        # 删除关系
        need_delete_ids = [tag.id for tag in Tags.objects.all() if tag.name in need_delete]
        for releation in Realtion_Article_Tags.objects.filter(aid=self.id):
            if releation.tid in need_delete_ids:
                releation.delete()
    # 删除全部关系
    def del_all_relation(self):
        reletions = Realtion_Article_Tags.objects.filter(aid=self.id)
        for reletion in reletions:
            reletion.delete()


# 标签
class Tags(models.Model):
    # 标签的名称
    name = models.CharField(max_length=64)
    # 新建标签
    @classmethod
    def create_tags(cls, tag_names, aid):
        # 查询出已经存在的标签
        exist_tags = cls.objects.filter(name__in=tag_names).only('name')
        # 将查询结果转化成一个集合 方便后面的集合运算
        exist = set([tag.name for tag in exist_tags])
        print('++++++++++++++++++++++++=', exist)
        # 获得新增加的标签
        new_tag_names = set(tag_names) - exist
        # 因为获得是对象需要转换成列表形式， 通过列表生成式
        new_names = [tag_name for tag_name in new_tag_names]

        # 进行批量创建 必须先转为为对象
        cls.objects.bulk_create([cls(name=tag) for tag in new_names])

        # 更新关系表
        # 获取新建的关系
        tags = cls.objects.filter(name__in=tag_names)
        for t in tags:
            # 对新建的关系进行更新 不存在则新建
            Realtion_Article_Tags.objects.update_or_create(aid=aid, tid=t.id)
        return tags

    # 使用这个装饰器 第一次调用的使用 会将计算过的结果也就是返回的值存入一个字典中 当下一次调用这个方法的时候就可以直接将这个值从字典中取出来
    # 即cache的概念
    # -------------------------待使用---------------------------------
    @cached_property
    def articles(self):
        relations = Realtion_Article_Tags.objects.filter(tid=self.id)
        aid_list = [relation.aid for relation in relations]
        articles = Article.objects.filter(aid__in=aid_list)
        return articles

# 文章的评论
class Comment(models.Model):
    aid = models.IntegerField()
    name = models.CharField(max_length=64)
    date = models.DateTimeField(auto_now_add=True)
    content = models.TextField()

# 文章与标签的关系
class Realtion_Article_Tags(models.Model):
    # 文章与标签是多对多的关系
    aid = models.IntegerField()
    tid = models.IntegerField()