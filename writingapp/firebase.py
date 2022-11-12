
from firebase_init import init_firebase

db= init_firebase()

def init_comment_data(email, id, userid):
    data= {}
    document_id= email+"@"+str(id)+"@"+str(userid)
    print(document_id)
    db.collection('comment').document(document_id).create(data)
    return "executed"


def submit_comment_data(res, email, id, userid):
    data= {
        'data_json': res
    }
    document_id= email+"@"+str(id)+"@"+str(userid)
    db.collection('comment').document(document_id).set(data, merge= True)
    return "executed"

def create_current_user_data(res, email):
    db.collection('current_user_data').document(email).set(res, merge= True)
    return "executed"


def init_book_comment_data(email, id, userid):
    data= {}
    document_id= email+"@"+str(id)+"@"+str(userid)
    print(document_id)
    db.collection('book_comment').document(document_id).create(data)
    return "executed"

def submit_book_comment_data(res, email, id, userid):
    data= {
        'data_json': res
    }
    document_id= email+"@"+str(id)+"@"+str(userid)
    db.collection('book_comment').document(document_id).set(data, merge= True)
    return "executed"