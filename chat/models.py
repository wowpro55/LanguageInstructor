from django.db import models
from django.contrib.auth.models import User
import os
import json
import csv

class DifficultyLevel(models.Model):
    ID = models.CharField(max_length=3, unique=True, primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    listening = models.TextField()
    reading = models.TextField()
    writing = models.TextField()
    speaking_spoken_interaction = models.TextField()
    speaking_spoken_production = models.TextField()
    vocabulary_file_path = models.CharField(
        max_length=255, null=True, blank=True)  # Structured storage for vocabulary

    def __str__(self):
        return self.name
    
    def load_vocabulary(self):
        """Load vocabulary words from the referenced file (supports JSON and CSV)."""
        if not self.vocabulary_file_path:
            return []  # Return an empty list if no file path is provided

        if not os.path.exists(self.vocabulary_file_path):
            return []  # Return an empty list if the file doesn't exist

        try:
            file_extension = os.path.splitext(self.vocabulary_file_path)[1].lower()

            if file_extension == ".json":
                # Load vocabulary from JSON file
                with open(self.vocabulary_file_path, "r") as file:
                    data = json.load(file)
                    return data.get("words", [])  # Extract "words" key

            elif file_extension == ".csv":
                # Load vocabulary from CSV file
                with open(self.vocabulary_file_path, "r") as file:
                    reader = csv.reader(file)
                    return [row[0] for row in reader if row]  # Extract first column

            else:
                # Unsupported file type
                return []

        except Exception as e:
            # Handle any error during file reading
            return []

class ChatFormalityLevel(models.Model):
    level = models.CharField(max_length=20)
    characteristics = models.TextField()
    example_too_formal = models.TextField()
    example_too_casual = models.TextField()
    example_correct = models.TextField()

    def __str__(self):
        return self.level


class Persona(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    formality_level = models.ForeignKey(ChatFormalityLevel,on_delete=models.SET_NULL,  null=True, blank=True)
    
 
    def __str__(self):
        return self.name


class Scenario(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name


class ScenarioPersonaDifficulty(models.Model):
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, related_name="difficulty_personas")
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name="scenario_difficulties")
    difficulty_level = models.ForeignKey(DifficultyLevel, on_delete=models.CASCADE, related_name="scenario_personas")

    class Meta:
        unique_together = ("scenario", "persona", "difficulty_level")

    def __str__(self):
        return f"{self.scenario.name} - {self.persona.name} ({self.difficulty_level.name})"


class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_message = models.TextField()
    agent_response = models.TextField()
    context = models.JSONField(null=True, blank=True)  # Stores conversation metadata
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat by {self.user.username} at {self.timestamp}"


class ChatInteraction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    persona = models.ForeignKey(Persona, on_delete=models.SET_NULL, null=True, related_name="interactions")
    scenario = models.ForeignKey(Scenario, on_delete=models.SET_NULL, null=True, related_name="interactions")
    difficulty_level = models.ForeignKey(DifficultyLevel, on_delete=models.SET_NULL, null=True, related_name="interactions")

    def __str__(self):
        return f"Interaction by {self.user.username} at {self.timestamp}"
