import requests

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlciIsInR5cGUiOiJhY2Nlc3MiLCJleHAiOjE3Njc0NzY3NTcsImlhdCI6MTc2NzQ3NDk1N30.p73uoOulutzYW0gBFOo8oFNsW3HL5auZjqjZ-IazpM8"

headers = {
    "Authorization": f"Bearer {token}"
}

response = requests.get("http://127.0.0.1:8000/protected", headers=headers)

print(response.json())