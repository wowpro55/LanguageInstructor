import os
import csv
from django.core.management.base import BaseCommand
from chat.models import (
    DifficultyLevel,
    ChatFormalityLevel,
    Persona,
    Scenario,
    ScenarioPersonaDifficulty,
)

class Command(BaseCommand):
    help = "Populate the database with initial data from CSV files."

    def handle(self, *args, **options):
        base_dir = "/mnt/c/users/basti/desktop/work/programmieren/CodingProjects/LanguageInstructor/languagetutor"
        data_dir = os.path.join(base_dir, "chat/data/tables/")
        vocabulary_dir = os.path.join(data_dir, "vocabulary_lists/")

        # Step 1: Load Difficulty Levels
        self.stdout.write("Loading Difficulty Levels...")
        with open(os.path.join(data_dir, "difficulty_levels.csv"), "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                file_path = os.path.join(vocabulary_dir, f"vocabulary_list_{row['ID']}.csv")
                DifficultyLevel.objects.get_or_create(
                    ID=row["ID"],
                    defaults={
                        "name": row["name"],
                        "description": row["description"],
                        "listening": row["listening"],
                        "reading": row["reading"],
                        "writing": row["writing"],
                        "speaking_spoken_interaction": row["speaking_spoken_interaction"],
                        "speaking_spoken_production": row["speaking_spoken_production"],
                        "vocabulary_file_path": file_path,
                    },
                )

        # Step 2: Load Chat Formality Levels
        self.stdout.write("Loading Chat Formality Levels...")
        with open(os.path.join(data_dir, "chat_formality_levels.csv"), "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                ChatFormalityLevel.objects.get_or_create(
                    level=row["level"],
                    defaults={
                        "characteristics": row["characteristics"],
                        "example_too_formal": row["example_too_formal"],
                        "example_too_casual": row["example_too_casual"],
                        "example_correct": row["example_correct"],
                    },
                )

        # Step 3: Load Personas
        self.stdout.write("Loading Personas...")
        with open(os.path.join(data_dir, "personas.csv"), "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                formality_level = ChatFormalityLevel.objects.filter(level=row["formality_level"]).first()
                Persona.objects.get_or_create(
                    name=row["name"],
                    defaults={
                        "description": row["description"],
                        "formality_level": formality_level,
                    },
                )

        # Step 4: Load Scenarios
        self.stdout.write("Loading Scenarios...")
        with open(os.path.join(data_dir, "scenarios.csv"), "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                Scenario.objects.get_or_create(
                    name=row["name"],
                    defaults={"description": row["description"]},
                )

        # Step 5: Load Scenario-Persona-Difficulty Relationships
        self.stdout.write("Loading Scenario-Persona-Difficulty Relationships...")
        with open(os.path.join(data_dir, "scenario_persona_difficulty.csv"), "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                scenario = Scenario.objects.get(name=row["scenario"])
                persona = Persona.objects.get(name=row["persona"])
                difficulty = DifficultyLevel.objects.get(ID=row["difficulty_level"])
                ScenarioPersonaDifficulty.objects.get_or_create(
                    scenario=scenario,
                    persona=persona,
                    difficulty_level=difficulty,
                )

        self.stdout.write(self.style.SUCCESS("Database population complete!"))
