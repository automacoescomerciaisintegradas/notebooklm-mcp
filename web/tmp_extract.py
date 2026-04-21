import json, urllib.request, sys
url = 'http://127.0.0.1:5117/api/skills/extract'
payload = json.dumps({"urls": ["https://www.youtube.com/watch?v=VWNaa00aFqo"]}).encode('utf-8')
req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req) as resp:
    data = resp.read().decode()
    print(data)
