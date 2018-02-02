from django.db import models
# 用于生成密码的hash值
from django.contrib.auth.hashers import make_password

# Create your models here.
# 创建用户名
class User(models.Model):
    username = models.CharField(max_length=64, unique=True, null=False, blank=False)
    passwd = models.CharField(max_length=64, null=False, blank=False)
    head = models.ImageField()
    age = models.IntegerField()
    sex = models.IntegerField()
    # 权限设置  默认为1
    pid = models.IntegerField(default=1)

    # 重写save方法
    def save(self):
        if not self.id:
            self.passwd = make_password(self.passwd)
        super().save()

    @property
    def permission(self):
        per = Permission.objects.get(id=self.pid)
        return per.perm

class Permission(models.Model):
    perm = models.IntegerField()
    name = models.CharField(max_length=64)
