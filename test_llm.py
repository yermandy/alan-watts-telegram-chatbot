from ollama import chat

response = chat(model="llama3", messages=[{"role": "user", "content": "Why is the sky blue? Keep the answer short."}])
print(response["message"]["content"])
