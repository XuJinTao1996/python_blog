import time
from django.utils.deprecation import MiddlewareMixin

# 允许每秒最大访问量为20
MAX_PER_SECOND_REQUEST_NUM = 20

# 限制爬虫中间件
class RestrictSpiderRequestMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # 获取当次请求时间
        now = time.time()
        # 获取session里存储的请求时间队列
        request_time_queue = request.session.get('request_time_queue', [])
        if len(request_time_queue) < MAX_PER_SECOND_REQUEST_NUM:
            request_time_queue.append(now)
            request.session['request_time_queue'] = request_time_queue
            print('-------------放行------------------')
        else:
            if (now - request_time_queue[0]) < 1:
                print('--------------请求太过频繁---请等待--------------')
                time.sleep(10)
                print('--------------继续操作-------------------------')

                # 继续向队列中添加当前时间
                request_time_queue.append(now)
                # 请求之间是连绵不间断的 所以在这里我们需要让队列进行滚动更新。
                request.session['request_time_queue'] = request_time_queue[1:]
