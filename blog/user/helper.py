from .models import Permission, User
from django.http import HttpResponse



# 权限验证装饰器
def check_perm(uid, name):
    # 当前用户
    current_user = User.objects.get(id=uid)
    # 需要的权限
    need_perm = Permission.objects.get(name=name)
    # 返回用户权限和所需权限的对比结果
    return current_user.permission >= need_perm.perm


def check_permission(name):
    def wrap1(viem_func):
        def wrap2(request, *args, **kwargs):
            # 获取当前用户id
            uid = request.session.get('uid')
            if uid:
                res = check_perm(uid, name)
                if res:
                    response = viem_func(request, *args, **kwargs)
                    return response
            return HttpResponse('滚犊子')
        return wrap2
    return wrap1