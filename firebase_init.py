
# from firebase_admin import firestore, initialize_app
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate('serviceAccount.json')
app = firebase_admin.initialize_app(cred)
db = firestore.client()

def init_firebase():
    # Use a service account.
    return db
