# Tag: v3.0 - Stream Connection
from sdk import StreamClient
stream = StreamClient()
conn = stream.connect(stream_id='stream_65', heartbeat_sec=15)
print(conn)
