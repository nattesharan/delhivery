from bson import ObjectId
from delhivery.models import DelhiveryUser
def get_id_from_rooms(rooms):
    for room in rooms:
        try:
            return ObjectId(room)
        except:
            pass

def get_active_user_ids():
    active_users = DelhiveryUser.objects.filter(is_online=True).only('id')
    return [str(active_user.id) for active_user in active_users]