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
import logging
from core.utils import log_error

# Get the logger
logger = logging.getLogger(__name__)
# Fetch the API key from .env
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# Agent main prompting
MAIN_AGENT_PROMT_SETTING = "You are a helpful assistant. Speak in simple English."
RANDOM_QUESTION_AGENT_PROMT_SETTING = "You are a helpful assistant. Generate a simple and interesting question for the user."
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
        try:
            greeting = f"Hello, {request.user.first_name}! {random.choice(GREETING_QUESTIONS)}"
            return render(request, 'chat/chat.html', {'greeting': greeting})
        except Exception as e:
            logger.error(f"Failed to render chat page: {str(e)}")
            log_error(request.user, f"Failed to render chat page: {str(e)}", "get method")
            return JsonResponse({"error": "Failed to load chat page. Please try again later."}, status=500)

    def post(self, request):
        """Handle user input and provide agent response."""
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "").strip()

            if not user_message:
                return JsonResponse({"error": "Message cannot be empty"}, status=400)

            # Check for sensitive topics
            if any(topic in user_message.lower() for topic in SENSITIVE_TOPICS):
                agent_response = "I prefer not to discuss politics, religion, or culture."
            else:
                if not Chat.objects.filter(user=request.user).exists():
                    agent_response = f"Hello, {request.user.first_name}! {random.choice(GREETING_QUESTIONS)}"
                else:
                    try:
                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[{"role": "system", "content": MAIN_AGENT_PROMT_SETTING},
                                      {"role": "user", "content": user_message}]
                        )
                        agent_response = response.choices[0].message.content
                    except Exception as e:
                        agent_response = "Sorry, I couldn't process your message. Please try again later."
                        logger.error(f"API call failed: {str(e)}")
                        log_error(request.user, f"API call failed: {str(e)}", "post method - OpenAI API call")

                    # Random question generation
                    if random.random() < 0.2:
                        try:
                            question_response = client.chat.completions.create(
                                model="gpt-4o-mini",
                                messages=[{"role": "system", "content": RANDOM_QUESTION_AGENT_PROMT_SETTING}]
                            )
                            generated_question = question_response.choices[0].message.content
                            agent_response += " " + generated_question
                        except Exception as e:
                            agent_response += " By the way, do you have any questions for me?"
                            logger.error(f"API call failed when generating question: {str(e)}")
                            log_error(request.user, f"API call failed when generating question: {str(e)}", "post method - random question generation")

            # Save the interaction to the database
            try:
                Chat.objects.create(user=request.user, user_message=user_message, agent_response=agent_response)
            except Exception as e:
                logger.error(f"Failed to save chat interaction: {str(e)}")
                log_error(request.user, f"Failed to save chat interaction: {str(e)}", "post method - save to DB")

            return JsonResponse({"response": agent_response}, status=200)

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in request: {str(e)}")
            log_error(request.user, f"Invalid JSON in request: {str(e)}", "post method - JSON decode")
            return JsonResponse({"error": "Invalid JSON format."}, status=400)
        except Exception as e:
            logger.error(f"Unexpected error in post method: {str(e)}")
            log_error(request.user, f"Unexpected error in post method: {str(e)}", "post method - general exception")
            return JsonResponse({"error": "An unexpected error occurred. Please try again later."}, status=500)

    def delete(self, request):
        """Clear chat history."""
        try:
            Chat.objects.filter(user=request.user).delete()
            return JsonResponse({"message": "Chat history cleared."}, status=200)
        except Exception as e:
            logger.error(f"Failed to clear chat history: {str(e)}")
            log_error(request.user, f"Failed to clear chat history: {str(e)}", "delete method")
            return JsonResponse({"error": "Failed to clear chat history. Please try again later."}, status=500)
