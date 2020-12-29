from fcm_django.models import FCMDevice
from users.models import CustomUser

def send_notification(user_id, title, message, data):
   try:
      user = CustomUser.objects.get(pk=user_id)
      device = FCMDevice.objects.get(user=user)
#       kwargs = {
#         "content_available": True,
#         'extra_kwargs': {"priority": "high", "mutable_content": True, 'notification': data },
#       }
#       if device.type == 'ios':
#          device.send_message(title=title,body=message,data=data,sound='default',**kwargs)
#       else:
#          device.send_message(title=title,body=message,data=data,sound='default')
      result = device.send_message(title=title,body=message,data=data,sound='default')
      return result
   except:
      pass
