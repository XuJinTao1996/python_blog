# 表单验证
from django.forms import Form, ModelForm, CharField
from django.contrib.auth.hashers import check_password
from .models import User

# 注册表单验证
class RegisterForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'passwd', 'head', 'age', 'sex']

# 登陆表单验证
class LoginForm(Form):
    username = CharField(max_length=64)
    passwd = CharField(max_length=64)

    # 验证用户名和密码是否正确
    def chk_passwd(self):
        # 取出表单中的值
        username = self.cleaned_data['username']
        passwd = self.cleaned_data['passwd']

        try:
            # 如果用户存在
            user = User.objects.get(username=username)
            # 进行密码验证并返回验证结果
            return user, check_password(passwd, user.passwd)
        except:
            return None, False