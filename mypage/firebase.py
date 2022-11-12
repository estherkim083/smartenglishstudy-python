
from firebase_init import init_firebase

db= init_firebase()


def add_friends_data_to_firebase(offset_withid, email):
    ref_db= db.collection(email).document(str(offset_withid))
    ref_db.set({})
    return "executed"

def delete_friends_data_to_firebase(offset_withid, email):
    db.collection(email).document(str(offset_withid)).set({}, merge= False)
    return "executed"

def update_chat(offset_withid, email, map_data):    # map data는 from ,id, time, message, date 을 포함하는 json
    data = {
        map_data.get('id'): map_data
    }
    db.collection(email).document(str(offset_withid)).set(data, merge=True)
    return "executed"