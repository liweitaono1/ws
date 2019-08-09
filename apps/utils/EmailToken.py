import base64
from itsdangerous import URLSafeTimedSerializer as utsr
from django.conf import settings as django_settings


class Token:
    '''
    import itsdangerous

    salt='sdaf'#加盐，指定一个盐值，别让别人知道哦，否则就可以解密出来了
    t=itsdangerous.TimedJSONWebSignatureSerializer(salt,expires_in=600)#过期时间600秒

    # ==============如何加密==================
    res=t.dumps({'username':'yangfan','user_id':1})# 在t中加入传输的数据
    token=res.decode()#指定编码格式
    print(token)
    # 得到的数据如下，就是包含数据和盐值的token了，只有在知道盐值的时候才能被解密出来
    # eyJhbGciOiJIUzUxMiIsImlhdCI6MTU0MTgxOTcyMCwiZXhwIjoxNTQxODIwMzIwfQ.eyJ1c2VybmFtZSI6InlhbmdmYW4iLCJ1c2VyX2lkIjoxfQ.VjCgry9Sr-4iRsK_MHYThcn_O7js9BERrXzocc7BI1aavC3N3s3e0wWMsvq2-Qp-ol_WNMD23wxiYRrA1kwCbg

    # ======================加密的数据如何解析=================
    res=t.loads('eyJhbGciOiJIUzUxMiIsImlhdCI6MTU0MTgxOTcyMCwiZXhwIjoxNTQxODIwMzIwfQ.eyJ1c2VybmFtZSI6InlhbmdmYW4iLCJ1c2VyX2lkIjoxfQ.VjCgry9Sr-4iRsK_MHYThcn_O7js9BERrXzocc7BI1aavC3N3s3e0wWMsvq2-Qp-ol_WNMD23wxiYRrA1kwCbg')
    print(res)
    # 返回的数据如下：
    # {'username': 'yangfan', 'user_id': 1}
    # 我们试一下将解析的数据改一个字母，或者超过了过期时间
    '''

    def __init__(self, security_key):
        self.security_key = security_key
        self.salt = base64.b64encode(security_key.encode(encoding='utf-8'))

    def generate_validate_token(self, username):
        serializer = utsr(self.security_key)
        return serializer.dumps(username, self.salt)

    def confirm_validate_token(self, token, expiration=3600):
        serializer = utsr(self.security_key)
        return serializer.loads(token, salt=self.salt, max_age=expiration)

    def remove_validate_token(self, token):
        serializer = utsr(self.security_key)
        print(serializer.loads(token, salt=self.salt))
        return serializer.loads(token, salt=self.salt)


token_confirm = Token(django_settings.SECRET_KEY)
# 定义为全局变量
