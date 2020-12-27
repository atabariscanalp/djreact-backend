from fcm_django.models import FCMDevice

def send_notification(user_id, title, message, data):
   try:
      device = FCMDevice.objects.filter(user=user_id).first()
      kwargs = {
        "content_available": True,
        'extra_kwargs': {"priority": "high", "mutable_content": True, 'notification': data },
      }
      if device.type == 'ios':
         device.send_message(title=title,body=message,data=data,sound='default',**kwargs)
      else:
         device.send_message(title=title,body=message,data=data,sound='default')
      #result = device.send_message(title=title,body=message,data=data,sound=)
      #return result
   except:
      pass
