from generated_openai_sdk import HelloWorldClient

client = HelloWorldClient(base_url="http://localhost:8000")

print("Testing root endpoint...")
print(client.health_check())
