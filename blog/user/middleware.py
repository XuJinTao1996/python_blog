from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from .models import User

class CurrentUserCheckMiddleware(MiddlewareMixin):
    # 在发起轻轻之前验证
    def process_request(self, request):
        # 查看用户是否登陆
        uid = request.session.get('uid')
        if uid:
            request.user = User.objects.get(id=uid)