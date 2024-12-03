from django.http import JsonResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Chat
import random
import openai
import json
from django.conf import settings

openai.api_key = settings.OPENAI_API_KEY

# Sensitive topics to avoid
SENSITIVE_TOPICS = ["politics", "religion", "culture"]
GREETING_QUESTIONS = [
    "How are you today?",
    "What would you like to talk about?",
    "Tell me something interesting!"
]

@method_decorator(login_required, name='dispatch')
class ChatView(View):
    def get(self, request):
        """Fetch the last 10 chat messages."""
        history = Chat.objects.filter(user=request.user).order_by('-timestamp')[:10]
        history_data = [
            {"user": chat.user_message, "agent": chat.agent_response}
            for chat in history
        ]
        return JsonResponse({"history": history_data}, status=200)

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
            # Check if it's the user's first message
            if Chat.objects.filter(user=request.user).count() == 0:
                agent_response = f"Hello, {request.user.first_name}! {random.choice(GREETING_QUESTIONS)}"
            else:
                # Fetch agent response from OpenAI
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant. Speak in simple English."},
                        {"role": "user", "content": user_message}
                    ]
                )
                agent_response = response['choices'][0]['message']['content']

                # Occasionally switch topics
                if random.random() < 0.2:
                    agent_response += " By the way, have you ever wondered about space travel?"

                # Handle confusion
                if "I don't understand" in agent_response:
                    agent_response = "I'm sorry, I didn't quite catch that. Did you mean something like this?"

        # Save the interaction to the database
        Chat.objects.create(user=request.user, user_message=user_message, agent_response=agent_response)

        return JsonResponse({"response": agent_response}, status=200)

    def delete(self, request):
        """Clear the chat history."""
        Chat.objects.filter(user=request.user).delete()
        return JsonResponse({"message": "Chat history cleared."}, status=200)
