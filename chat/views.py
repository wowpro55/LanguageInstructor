from random import choice
from django.views import View
from django.http import JsonResponse
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django_ratelimit.decorators import ratelimit
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from .models import Chat, ChatFormalityLevel, Persona, Scenario, DifficultyLevel, ScenarioPersonaDifficulty
import logging
import json
import openai
import os

openai.api_key = settings.OPENAI_API_KEY

# Logger setup
logger = logging.getLogger(__name__)

CACHE_TIMEOUT = 3600

# Helper functions
def validate_response_with_vocab(response, vocab_set):
    """Ensure the response strictly adheres to the provided vocabulary list."""
    words = response.split()
    validated = [word if word in vocab_set else "[REDACTED]" for word in words]
    return " ".join(validated)

def initialize_model_context(context):
    """Send a one-time initialization prompt to the model."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": json.dumps(context)}
            ]
        )
        logger.info("Model context initialized successfully.")
    except Exception as e:
        logger.error(f"Error during model initialization: {e}")

def load_vocabulary(file_path):
    """Load vocabulary words from a given file path."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Vocabulary file not found: {file_path}")
    
    with open(file_path, "r", encoding="utf-8") as file:
        return [line.strip() for line in file.readlines()]


@method_decorator(csrf_protect, name="dispatch")
@method_decorator(login_required, name="dispatch")
@method_decorator(ratelimit(key="ip", rate="1/3s", block=True), name="dispatch")
class ChatView(View):
    def get(self, request):
        """Render the chat page for GET requests."""
        try:
            greeting = f"Hello, {request.user.first_name}! Let's chat."
            return render(request, "chat/chat.html", {"greeting": greeting})
        except Exception as e:
            logger.error(f"Error rendering chat page: {e}")
            return JsonResponse({"error": "Unable to load the chat page. Please try again later."}, status=500)

    def post(self, request):
        """Handle user input and provide chatbot response."""
        try:
            body = json.loads(request.body.decode("utf-8"))
            user_message = body.get("message", "").strip()

            if not user_message:
                logger.debug("Empty message detected.")
                return JsonResponse({"error": "Message cannot be empty."}, status=400)

            # Retrieve reduced context from session
            reduced_context = request.session.get("reduced_prompt_context")
            if not reduced_context:
                logger.error("Reduced context not set in session.")
                return JsonResponse({"error": "Settings not configured. Please set difficulty, scenario, and persona."}, status=400)

            # Use the context to construct the system message
            system_prompt = json.dumps(reduced_context)

            # Send the user message with the reduced context
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            )

            chatbot_response = response.choices[0].message.content

            # Validate the response
            difficulty_id = request.session.get("difficulty_id")
            difficulty = get_object_or_404(DifficultyLevel, id=difficulty_id)
            vocab_set = set(difficulty.vocabulary_list)
            validated_response = validate_response_with_vocab(chatbot_response, vocab_set)

            Chat.objects.create(
                user=request.user,
                user_message=user_message,
                agent_response=validated_response,
                context={"difficulty": difficulty_id}
            )

            return JsonResponse({"response": validated_response}, status=200)

        except ObjectDoesNotExist as e:
            logger.error(f"Invalid reference in ChatView POST handler: {e}")
            return JsonResponse({"error": "Invalid settings. Please verify your selection."}, status=400)
        except Exception as e:
            logger.error(f"Error in ChatView POST handler: {e}")
            return JsonResponse({"error": "An error occurred. Please try again later."}, status=500)

@method_decorator(ratelimit(key="ip", rate="1/5s", block=True), name="dispatch")
class SettingsView(View):
    def post(self, request):
        try:
            body = json.loads(request.body.decode("utf-8"))
            difficulty_id = body.get("difficulty_id")
            scenario_id = body.get("scenario_id")
            persona_id = body.get("persona_id")

            # Validate inputs
            try:
                difficulty = DifficultyLevel.objects.get(id=difficulty_id)
                scenario = Scenario.objects.get(id=scenario_id)
                persona = Persona.objects.get(id=persona_id)
            except DifficultyLevel.DoesNotExist:
                return JsonResponse({"error": "Invalid difficulty level."}, status=400)
            except Scenario.DoesNotExist:
                return JsonResponse({"error": "Invalid scenario."}, status=400)
            except Persona.DoesNotExist:
                return JsonResponse({"error": "Invalid persona."}, status=400)

            # Load vocabulary from the file path if it exists
            vocabulary_list = []
            vocabulary_file_path = difficulty.vocabulary_file_path
            if vocabulary_file_path:  # Check if the path is not empty or NULL
                try:
                    vocabulary_list = load_vocabulary(vocabulary_file_path)
                except FileNotFoundError:
                    # Log the error and raise it only if a non-empty file path is invalid
                    logger.error(f"Vocabulary file not found: {vocabulary_file_path}")
                    return JsonResponse({"error": f"Vocabulary file not found: {vocabulary_file_path}"}, status=500)

            # Generate the full context for initialization
            full_context = {
                "difficulty_level": difficulty.name,
                "scenario": scenario.name,
                "persona": {
                    "name": persona.name,
                    "description": persona.description,
                    "formality_guidelines": {
                        "level": persona.formality_level.level,
                        "characteristics": persona.formality_level.characteristics,
                        "too_formal": persona.formality_level.example_too_formal,
                        "too_casual": persona.formality_level.example_too_casual,
                        "correct": persona.formality_level.example_correct,
                    },
                },
                "vocabulary_list": vocabulary_list,  # Empty list if no file is found or path is missing
            }

            # Send full context to initialize the model
            initialize_model_context(full_context)

            # Store reduced context without vocabulary list in session
            reduced_context = {
                "scenario": scenario.name,
                "persona": {
                    "description": persona.description,
                },
            }

            request.session["reduced_prompt_context"] = reduced_context
            request.session["difficulty_id"] = difficulty_id

            # Clear chat history upon settings change
            Chat.objects.filter(user=request.user).delete()

            return JsonResponse({"message": "Settings updated successfully."}, status=200)

        except ObjectDoesNotExist as e:
            logger.error(f"Invalid reference in SettingsView POST handler: {e}")
            return JsonResponse({"error": "Invalid settings. Please verify your selection."}, status=400)
        except Exception as e:
            logger.error(f"Error in SettingsView POST handler: {e}")
            return JsonResponse({"error": "An error occurred while updating settings."}, status=500)
