from fcm_django.models import FCMDevice

def send_notification(user_id,title, message, data):
   try:
      device = FCMDevice.objects.filter(user=user_id).first()
      result = device.send_message(title=title,body=message,
                          data=data,sound=True)
      return result
   except:
      pass
