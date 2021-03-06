import json

from django.core import serializers
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View

# CBV 방식
from django.views.decorators.csrf import csrf_exempt

from api.models import DHT


class TestView(View):

    # GET 요청을 처리하기 위해서 get 함수를 재정의
    def get(self, request, *args, **kwargs):
        # python의 딕셔너리를 이용해서 클라이언트로 전달할 데이터를 작성
        data = {
            'message': 'success'
        }

        # data 딕셔너리를 직렬화된 JSON 객체로 변경하여
        # 아두이노 클라이언트로 전달한다.
        return JsonResponse(data, status=200)

class DHTView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(DHTView, self).dispatch(request, *args, **kwargs)

    # def get(self, request, *args, **kwargs):
    #     dhts = serializers.serialize("json", DHT.objects.all())
    #     print(dhts)
    #     return JsonResponse(dhts,
    #                         safe=False,
    #                         json_dumps_params={'ensure_ascii: False'},
    #                         status=200)

    # POST 요청을 처리하기 위해서 post 함수를 재정의
    def post(self, request, *args, **kwargs):
        if request.META['CONTENT_TYPE'] == 'application/json':
            req = json.loads(request.body)
            print('humidity: ' + str(req['humidity']) + '\n')
            print('temperature: ' + str(req['temperature']) + '\n')

            dht = DHT(humidity=req['humidity'], temperature=req['temperature'])
            dht.save()

            data = {
                'message': 'success'
            }
            return JsonResponse(data, status=200)

        data = {
            'message': 'failed'
        }
        return JsonResponse(data, status=404)
