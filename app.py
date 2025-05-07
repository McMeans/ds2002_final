from flask import Flask, render_template, request, jsonify
from services.recipe_service import RecipeService
from services.gemini_service import GeminiService

app = Flask(__name__)
recipe_service = RecipeService()
gemini_service = GeminiService()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/debug')
def debug():
    return "This is the debug route. Everything's (hopefully) fine."

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
def chat_api():
    try:
        # get message data and chat history
        data = request.get_json()
        user_message = data.get('message', '')
        conversation_history = data.get('history', [])
        
        # return error if no message
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # retrieve recipes
        recipes = recipe_service.search_recipes(user_message)
        
        try:
            # try to generate response using Gemini
            context = {'recipes': recipes} if recipes else None
            response = gemini_service.generate_response(
                user_message, 
                context,
                conversation_history
            )
            return jsonify({'response': response})
        except Exception as e:
            # if Gemini fails, format and return recipe information directly
            if recipes:
                formatted_response = "Here are some recipes I found:\n\n"
                for recipe in recipes:
                    formatted_response += f"## {recipe.get('title', 'Untitled Recipe')}\n\n"
                    
                    # add ingredients
                    if 'ingredients' in recipe:
                        formatted_response += "### Ingredients:\n"
                        if isinstance(recipe['ingredients'], list):
                            for ingredient in recipe['ingredients']:
                                formatted_response += f"- {ingredient}\n"
                        else:
                            formatted_response += f"- {recipe['ingredients']}\n"
                    
                    # add instructions
                    if 'instructions' in recipe:
                        formatted_response += "\n### Instructions:\n"
                        formatted_response += f"{recipe['instructions']}\n"
                    
                    formatted_response += "\n---\n\n"
                
                return jsonify({'response': formatted_response})
            else:
                return jsonify({'response': "I couldn't find any recipes matching your request. Could you try rephrasing your question?"})
            
    except Exception as e:
        # error in generation
        print(f"Error in chat API: {e}")
        return jsonify({'error': 'An error occurred'}), 500

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
