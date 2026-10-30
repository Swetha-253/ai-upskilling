# Tag: v3.0 - Auth Login and Refresh
from sdk import Auth
auth = Auth()
tok = auth.login(username='user_84', password='pw', token_ttl=3600)
ref = auth.refresh_token(refresh_token=tok.access_token)
print(ref)
