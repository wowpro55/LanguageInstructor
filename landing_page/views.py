from django.shortcuts import redirect
import json
from django.views import View
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django_ratelimit.decorators import ratelimit
from django.core.exceptions import ObjectDoesNotExist
from chat.models import DifficultyLevel, Scenario, Persona, Chat
from .utils import initialize_model_context, load_vocabulary
import logging
import openai
from django.conf import settings


logger = logging.getLogger("languagetutor.custom")

@method_decorator(login_required, name='dispatch')
@method_decorator(ratelimit(key="ip", rate="5/1s", block=True), name="dispatch")
class SettingsView(View):
    def get(self, request):
        """Handle GET request and render the settings page."""
        try:
            difficulties = DifficultyLevel.objects.all()
            scenarios = Scenario.objects.all()
            personas = Persona.objects.all()

            return render(
                request,
                "landing_page/landing_page.html",
                {
                    "difficulties": difficulties,
                    "scenarios": scenarios,
                    "personas": personas,
                },
            )
        except Exception as e:
            logger.error(f"Error rendering settings page: {e}")
            return JsonResponse({"error": "Failed to load settings page."}, status=500)

    def post(self, request):
        try:
            logger.info(f"Raw request body: {request.body}")

            try:
                body = json.loads(request.body.decode("utf-8"))
                logger.info(f"Parsed request body: {body}")
            except json.JSONDecodeError as e:
                logger.error(f"JSON decoding failed: {e}")
                return JsonResponse({"error": "Invalid JSON payload."}, status=400)

            difficulty_id = body.get("difficulty_id")
            scenario_id = body.get("scenario_id")
            persona_id = body.get("persona_id")

            # Validate data
            if not difficulty_id or not scenario_id or not persona_id:
                logger.error(f"Missing form data: difficulty_id={difficulty_id}, scenario_id={scenario_id}, persona_id={persona_id}")
                return JsonResponse({"error": "All fields are required."}, status=400)

            # Continue with processing
            difficulty = DifficultyLevel.objects.get(ID=difficulty_id)  # Use `ID` as primary key
            scenario = Scenario.objects.get(id=scenario_id)
            persona = Persona.objects.get(id=persona_id)

            logger.info(f"Selected difficulty: {difficulty}, scenario: {scenario}, persona: {persona}")

            # Load vocabulary from selected difficulty
            vocab_list = difficulty.load_vocabulary()  # Fetch the vocabulary list from the difficulty
            logger.info(f"Vocabulary list loaded: {vocab_list}")

            # Create full context
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
                "vocabulary": vocab_list 
            }
            logger.info(f"Full context sent to initialize model: {full_context}")
            logger.info(f"Vocabulary list being sent to model: {vocab_list}")
            logger.info(f"Full context sent to initialize model: {full_context}")

            initialize_model_context(full_context, vocab_list)

            # Store reduced context in the session
            request.session["reduced_prompt_context"] = {
                "scenario": scenario.name,
                "persona": {
                    "description": persona.description,
                },
            }
            request.session["difficulty_id"] = difficulty_id

            return redirect("chat")

        except DifficultyLevel.DoesNotExist:
            logger.error(f"Invalid difficulty ID: {difficulty_id}")
            return JsonResponse({"error": "Invalid difficulty level."}, status=400)
        except Scenario.DoesNotExist:
            logger.error(f"Invalid scenario ID: {scenario_id}")
            return JsonResponse({"error": "Invalid scenario."}, status=400)
        except Persona.DoesNotExist:
            logger.error(f"Invalid persona ID: {persona_id}")
            return JsonResponse({"error": "Invalid persona."}, status=400)
        except Exception as e:
            logger.error(f"Unexpected error in SettingsView POST: {e}")
            return JsonResponse({"error": "An error occurred while updating settings."}, status=500)
