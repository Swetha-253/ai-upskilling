# Tag: v2.4 - Auth Login
from sdk_v2 import Auth
auth = Auth()
tok = auth.login(username='user_32', password='pw', old_ttl=7200)
print(tok)
