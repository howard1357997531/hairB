from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.conf import settings
from .serializers import LineUserSerializer
from .models import LineUser
import requests

LINE_CHANNEL_ACCESS_TOKEN = settings.LINE_CHANNEL_ACCESS_TOKEN

# {18: {'id': 18, 'line_id': 'wqdasdasdasasdWQEQWE', 'display_name': 'Lisa', 'picture_url': 'https://i.imgur.com/zVKLv1O.jpg', 
# 'is_admin': False, 'is_staff': True, 'become_staff_time': '2024/05/27 00:33', 'created_at': '2024/05/02 17:01'}}
pre_lineUser_data = {}

@receiver(pre_save, sender=LineUser)
def lineUser_pre_save_signal(sender, instance, **kwargs):
    if instance.id:
        try:
            pre_data = sender.objects.filter(id=instance.id).first()
            serializer = LineUserSerializer(pre_data, many=False)
            pre_lineUser_data[instance.id] = serializer.data
        except:
            pass

def check_change(pre_data, post_data, id):
    if pre_data[id].get('display_name') != post_data.get('display_name') or \
       pre_data[id].get('picture_url') != post_data.get('picture_url'):
        return "display_name_or_picture_url"
    elif pre_data[id].get('is_admin') != post_data.get('is_admin'):
        return "is_admin"
    elif pre_data[id].get('is_staff') != post_data.get('is_staff'):
        return "is_staff"
    

@receiver(post_save, sender=LineUser)
def lineUser_post_save_signal(sender, instance, created, **kwargs):
    headers = {
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    line_id = instance.line_id
    admin_richmenu_id = 'richmenu-cd369eb495b63537e9566715093dbd25'
    staff_richmenu_id = 'richmenu-5d740ed39492352328b2c12766e7225e'

    post_lineUser_data = LineUserSerializer(instance, many=False).data
    check_change_data = check_change(pre_lineUser_data, post_lineUser_data, instance.id)
    request_method = 'POST'
    print(check_change_data)
    if not created:
        if check_change_data == 'display_name_or_picture_url':
            return
        
        elif check_change_data == 'is_admin':
            if instance.is_admin:
                richmenu_id = admin_richmenu_id
            else:
                # 若取消 admin 時為 is_staff = True, 換成 staff 的 richmenu
                if instance.is_staff:
                    richmenu_id = staff_richmenu_id
                # 若取消 admin 時為 is_staff = False, 取消使用任何 richmenu
                else:
                    request_method = 'DELETE'
                
        elif check_change_data == 'is_staff':
            # 若 is_admin = True，不管是新增或取消 staff 都會使用 admin richmenu
            if instance.is_admin:
                return
            
            if instance.is_staff:
                # 若新增 staff 時為 is_admin = False, 會使用 staff 的 richmenu
                richmenu_id = staff_richmenu_id
            else:
                # 若取消 staff 時為 is_admin = False, 取消使用任何 richmenu
                request_method = 'DELETE'
        
        if request_method == 'POST':
            url = f'https://api.line.me/v2/bot/user/{line_id}/richmenu/{richmenu_id}'
            requests.request('POST', url, headers=headers)

        elif request_method == 'DELETE':
            url = f'https://api.line.me/v2/bot/user/{line_id}/richmenu'
            requests.request('DELETE', url, headers=headers)
        