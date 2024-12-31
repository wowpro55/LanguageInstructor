from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.views import View
from django.shortcuts import redirect, render
from django.http import JsonResponse
import openai
from .models import Chat, Persona, Scenario, DifficultyLevel
from openai import OpenAI
import json
from langdetect import detect, LangDetectException
import logging
from django.conf import settings


logger = logging.getLogger("languagetutor.custom")
client = OpenAI(api_key=settings.OPENAI_API_KEY)

@method_decorator(csrf_protect, name="dispatch")
@method_decorator(login_required, name="dispatch")
class ChatView(View):
    def get(self, request):
        try:
            reduced_context = request.session.get("reduced_prompt_context")
            difficulty_id = request.session.get("difficulty_id")

            if not reduced_context or not difficulty_id:
                return JsonResponse({"error": "Session data is missing. Please set up your settings first."}, status=400)

            difficulties = DifficultyLevel.objects.all()
            scenarios = Scenario.objects.all()
            personas = Persona.objects.all()

            greeting = f"Hallo, {request.user.first_name}! Worüber möchtest du reden?"
            csrf_token = request.META.get("CSRF_COOKIE")

            return render(
                request,
                "chat/chat.html",
                {
                    "greeting": greeting,
                    "difficulties": difficulties,
                    "scenarios": scenarios,
                    "personas": personas,
                    "csrf_token": csrf_token,
                },
            )
        except Exception as e:
            logger.error(f"Error in GET request: {e}")
            return JsonResponse({"error": "An error occurred. Please try again later."}, status=500)

    def post(self, request):
        """
        Handle POST requests synchronously.
        """
        try:
            body = json.loads(request.body.decode("utf-8"))
            user_message = body.get("message", "").strip()

            if not user_message:
                return JsonResponse({"error": "Message cannot be empty."}, status=400)

            try:
                language = detect(user_message)
                if language != "de":
                    return JsonResponse({"response": "Entschuldigung, ich verstehe nur Deutsch!"}, status=200)
            except LangDetectException:
                return JsonResponse({"error": "Language detection failed. Please try again."}, status=400)

            reduced_context = request.session.get("reduced_prompt_context")
            if not reduced_context:
                return JsonResponse({"error": "Settings not configured. Please set difficulty, scenario, and persona."}, status=400)

            # Interact with OpenAI API
            system_prompt = json.dumps(reduced_context)
            response = client.chat.completions.create(model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ])
            chatbot_response = response.choices[0].message.content

            # Store chat in the database 
            difficulty_id = request.session.get("difficulty_id")
            Chat.objects.create(
                user=request.user,
                user_message=user_message,
                agent_response=chatbot_response,
                context={"difficulty": difficulty_id},
            )

            return JsonResponse({"response": chatbot_response}, status=200)

        except openai.OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            return JsonResponse({"error": "An error occurred with the chatbot. Please try again later."}, status=500)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return JsonResponse({"error": "An error occurred. Please try again later."}, status=500)
