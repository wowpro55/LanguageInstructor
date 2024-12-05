from django.http import JsonResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Chat
import random
from openai import OpenAI
import json
from django.conf import settings
from django.shortcuts import render

client = OpenAI(api_key=settings.OPENAI_API_KEY)


SENSITIVE_TOPICS = ["politics", "religion", "culture"]
GREETING_QUESTIONS = [
    "How are you today?",
    "What would you like to talk about?",
    "Tell me something interesting!"
]

@method_decorator(login_required, name='dispatch')
class ChatView(View):
    def get(self, request):
        """Fetch a greeting message when there is no chat history."""
        # Provide a greeting if no history exists (no DB interaction)
        greeting = f"Hello, {request.user.first_name}! {random.choice(GREETING_QUESTIONS)}"

        return render(request, 'chat/chat.html', {'greeting': greeting})

    def post(self, request):
        """Handle user input and provide agent response."""
        data = json.loads(request.body)
        user_message = data.get("message", "").strip()

        if not user_message:
            return JsonResponse({"error": "Message cannot be empty"}, status=400)

        # Check for sensitive topics
        if any(topic in user_message.lower() for topic in SENSITIVE_TOPICS):
            agent_response = "I prefer not to discuss politics, religion, or culture."
        else:
            if Chat.objects.filter(user=request.user).count() == 0:
                agent_response = f"Hello, {request.user.first_name}! {random.choice(GREETING_QUESTIONS)}"
            else:
                response = client.chat.completions.create(model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Speak in simple English."},
                    {"role": "user", "content": user_message}
                ])
                agent_response = response.choices[0].message.content

                if random.random() < 0.2:
                    agent_response += " By the way, have you ever wondered about space travel?"

        # Save the interaction to the database
        Chat.objects.create(user=request.user, user_message=user_message, agent_response=agent_response)

        return JsonResponse({"response": agent_response}, status=200)

    def delete(self, request):
        """Clear the chat history."""
        Chat.objects.filter(user=request.user).delete()
        return JsonResponse({"message": "Chat history cleared."}, status=200)
