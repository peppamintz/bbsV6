from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
import json


ACCESS_KEY_ID = ""  #用户AccessKey
ACCESS_KEY_SECRET = ""  #Access Key Secret

class SMS:
    def __init__(self,signName,templateCode):
        self.signName = signName
        self.templateCode = templateCode
        self.client = client = AcsClient(ACCESS_KEY_ID, ACCESS_KEY_SECRET, 'cn-hangzhou')

    def send(self, phone_numbers, template_param):
        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain('dysmsapi.aliyuncs.com')
        request.set_method('POST')
        request.set_protocol_type('https')  # https | http
        request.set_version('2017-05-25')
        request.set_action_name('SendSms')

        request.add_query_param('RegionId', "cn-hangzhou")
        request.add_query_param('PhoneNumbers', phone_numbers)
        request.add_query_param('SignName', self.signName)
        request.add_query_param('TemplateCode', self.templateCode)
        # print(kwargs)
        request.add_query_param('TemplateParam', template_param)
        print(request)
        # print(request['TemplateParam'])
        response = self.client.do_action_with_exception(request)
        return response

    def convert(self, data):
        str = data.decode()
        data = json.loads(str)
        return data['Message']

# 发送短信的人，以下填签名和短信的模板code
sms = SMS(" "," ")


# if __name__ == '__main__':
#     # 以下填发送短信到的手机号和验证码（测试）
#     # result = sms.send('13060867339', '5267')
#     resp = sms.send('18813754838', {'code': '9857'})
#     str = resp.decode()
#     print(str)
#     if sms.convert(resp) == 'OK':
#         print('success')
   