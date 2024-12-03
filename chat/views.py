# Create your views here.

import openai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .models import Chat
import os
from dotenv import load_dotenv
from django.db.models import F

@method_decorator(csrf_exempt, name='dispatch')
class ChatView(View):
    def post(self, request):
        try:
            import json
            data = json.loads(request.body)
            user_message = data.get("message", "")

            if not user_message:
                return JsonResponse({"error": "Message cannot be empty"}, status=400)

            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_message}
                ]
            )

            agent_response = response['choices'][0]['message']['content']

            # Save to database
            chat = Chat(user_message=user_message, agent_response=agent_response)
            chat.save()

            # Fetch recent conversation history (last 10 messages)
            history = Chat.objects.order_by(F('timestamp').asc())[-10:]
            history_data = [
                {"user": chat.user_message, "agent": chat.agent_response}
                for chat in history
            ]

            return JsonResponse({
                "response": agent_response,
                "history": history_data
            }, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    def get(self, request):
        try:
            # Fetch all conversation history (adjust to limit results if needed)
            history = Chat.objects.filter(user=request.user).order_by(F('timestamp').asc())[-10:]
            history_data = [
                {"user": chat.user_message, "agent": chat.agent_response}
                for chat in history
            ]

            return JsonResponse({"history": history_data}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
