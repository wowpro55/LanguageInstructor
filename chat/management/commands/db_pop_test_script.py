import csv
from django.core.management.base import BaseCommand
from chat.models import (
    DifficultyLevel,
    ChatFormalityLevel,
    Persona,
    Scenario,
    ScenarioPersonaDifficulty,
    Chat,
    ChatInteraction,
)

class Command(BaseCommand):
    help = "Validate data population and export results to CSV."

    def handle(self, *args, **options):
        results = []

        # Validate Difficulty Levels
        self.stdout.write("Validating Difficulty Levels...")
        difficulty_levels = DifficultyLevel.objects.all()
        if difficulty_levels.exists():
            results.append(["Difficulty Levels", "PASSED", len(difficulty_levels)])
        else:
            results.append(["Difficulty Levels", "FAILED", 0])

        # Validate Chat Formality Levels
        self.stdout.write("Validating Chat Formality Levels...")
        formality_levels = ChatFormalityLevel.objects.all()
        if formality_levels.exists():
            results.append(["Chat Formality Levels", "PASSED", len(formality_levels)])
        else:
            results.append(["Chat Formality Levels", "FAILED", 0])

        # Validate Personas
        self.stdout.write("Validating Personas...")
        personas = Persona.objects.all()
        if personas.exists():
            results.append(["Personas", "PASSED", len(personas)])
        else:
            results.append(["Personas", "FAILED", 0])

        # Validate Scenarios
        self.stdout.write("Validating Scenarios...")
        scenarios = Scenario.objects.all()
        if scenarios.exists():
            results.append(["Scenarios", "PASSED", len(scenarios)])
        else:
            results.append(["Scenarios", "FAILED", 0])

        # Validate Scenario-Persona-Difficulty Relationships
        self.stdout.write("Validating Scenario-Persona-Difficulty Relationships...")
        spd_relationships = ScenarioPersonaDifficulty.objects.all()
        if spd_relationships.exists():
            results.append(["Scenario-Persona-Difficulty Relationships", "PASSED", len(spd_relationships)])
        else:
            results.append(["Scenario-Persona-Difficulty Relationships", "FAILED", 0])

        # Validate Chats
        self.stdout.write("Validating Chats...")
        chats = Chat.objects.all()
        if chats.exists():
            results.append(["Chats", "PASSED", len(chats)])
        else:
            results.append(["Chats", "FAILED", 0])

        # Validate Chat Interactions
        self.stdout.write("Validating Chat Interactions...")
        chat_interactions = ChatInteraction.objects.all()
        if chat_interactions.exists():
            results.append(["Chat Interactions", "PASSED", len(chat_interactions)])
        else:
            results.append(["Chat Interactions", "FAILED", 0])

       # Export Results to CSV
        output_file = "/mnt/c/users/basti/desktop/work/programmieren/CodingProjects/LanguageInstructor/Test_Results/DB/validation_results.csv"
        self.stdout.write(f"Exporting results to {output_file}...")
        with open(output_file, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Category", "Status", "Count"])  # Write header row
            writer.writerows(results)  # Write the data rows

        self.stdout.write(self.style.SUCCESS("Validation complete. Results exported to validation_results.csv."))
