import openai
import json
import os
import logging

print(f"Module {__name__} imported")

logger = logging.getLogger(__name__)

def initialize_model_context(context, vocab_list):
    """Send a one-time initialization prompt to the model, enforcing German and vocabulary usage."""
    try:
        # Create a system message that includes instructions for Germanonly conversation
        system_message = {
            "role": "system",
            "content": json.dumps({
                "context": context,
                "instructions": f"""
                    Please respond **only in German**. 
                    Only use the following German words during the conversation: {', '.join(vocab_list)}.
                    If a non-German input is provided, respond with: "Entschuldigung, ich verstehe leider nur Deutsch!".
                    Do NOT use any words outside of the provided list. ONLY USE WORDS FROM THE vocab_list! Your answers should not exceed 30 words.
                """
            })
        }
        
        # Send the request to the OpenAI model with the context and vocabularylist
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[system_message]
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
