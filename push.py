
import os, json
try:
    import firebase_admin
    from firebase_admin import messaging, credentials
except Exception:
    firebase_admin = None

FIREBASE_CREDS = os.environ.get('FIREBASE_CREDS')  # JSON string

if FIREBASE_CREDS and firebase_admin:
    cred_dict = json.loads(FIREBASE_CREDS)
    cred = credentials.Certificate(cred_dict)
    try:
        firebase_admin.initialize_app(cred)
    except Exception:
        pass

def send_push_to_token(token: str, title: str, body: str, data: dict = None):
    if not firebase_admin:
        return None
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        token=token,
        data=data or {}
    )
    return messaging.send(message)
