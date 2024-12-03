# Create your views here.

import os
import requests
from django.shortcuts import render
from .forms import ChatForm
from .models import ChatMessage
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
API_URL = "https://api.openai.com/v1/chat/completions"

def chat_view(request):
    response = None
    if request.method == "POST":
        form = ChatForm(request.POST)
        if form.is_valid():
            user_message = form.cleaned_data["user_message"]

            # Call the API
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": user_message}]
            }

            try:
                api_response = requests.post(API_URL, json=payload, headers=headers)
                api_response.raise_for_status()
                agent_response = api_response.json()["choices"][0]["message"]["content"]

                # Save to database
                ChatMessage.objects.create(user_message=user_message, agent_response=agent_response)

                response = agent_response
            except requests.exceptions.RequestException as e:
                response = f"Error: {str(e)}"
    else:
        form = ChatForm()

    # Load chat history
    chat_history = ChatMessage.objects.all().order_by("-timestamp")[:10]

    return render(request, "chat/chat.html", {"form": form, "response": response, "chat_history": chat_history})



    