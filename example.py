from google import genai

client = genai.Client(
    api_key="API_KEY",
    http_options={"api_version": "v1beta"}
)

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Explain CI/CD in simple terms"
)

print(response.text)