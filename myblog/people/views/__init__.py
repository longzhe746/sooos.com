from people.views.follow import follow, following, un_follow
from people.views.handle import *
from people.views.settings import *

class MyMiddleware(object):
    def process_request(self, request):
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            ip =  request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.META["REMOTE_ADDR"]

        if request.user.is_authenticated():
            request.user.last_ip = ip
            request.user.save()
        #获取真实IP
        return None
        #返回None是为了继续调用Django系统的中间件对象，来接着处理业务