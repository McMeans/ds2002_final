import google.generativeai as genai
from dotenv import load_dotenv
import os
from typing import Dict, Any, List

load_dotenv()

class GeminiService:
    def __init__(self):
        # set up gemini
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        genai.configure(api_key=self.api_key)
        
        # retrieve model
        self.model = genai.GenerativeModel('models/gemini-1.5-pro')
        
        # starting prompt to guide the model's behavior
        self.system_prompt = """You are a helpful cooking assistant (named 'Guy') that can only provide information about recipes. 
        You have access to a recipe database and the Spoonacular API. 
        You should:
        1. Only provide information about recipes and cooking
        2. Be friendly and conversational
        3. Use markdown formatting in your responses
        4. If you don't know something about a recipe, say so
        5. Never make up information
        6. When providing recipes, include ingredients and instructions
        7. If you need to use mathematical expressions, use LaTex
        8. Maintain context from previous messages in the conversation
        """

    def generate_response(self, user_message: str, context: Dict[str, Any] = None, conversation_history: List[Dict[str, str]] = None) -> str:
        try:
            # prepare the prompt with context and conversation history
            prompt = f"{self.system_prompt}\n\n"
            
            # add conversation history if available
            if conversation_history:
                prompt += "Previous conversation:\n"
                for msg in conversation_history:
                    role = "User" if msg["role"] == "user" else "Assistant"
                    prompt += f"{role}: {msg['content']}\n"
                prompt += "\n"
            
            # add recipe context if found in db/api
            if context:
                prompt += f"Here is some relevant recipe information:\n{context}\n\n"
            
            prompt += f"User: {user_message}\n\nAssistant:"
            
            # generate response
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            # handle error in generation
            print(f"Error generating Gemini response: {e}")
            return "I apologize, but I'm having trouble processing your request right now. Please try again later." 