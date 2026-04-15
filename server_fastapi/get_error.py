import urllib.request
import urllib.error

try:
    resp = urllib.request.urlopen('http://localhost:5000/api/judgments/710486ba5c44f90f063ad064')
    print(resp.read().decode())
except urllib.error.HTTPError as e:
    print("HTTP ERROR:", e.code)
    print(e.read().decode())
except Exception as e:
    print("Error:", e)