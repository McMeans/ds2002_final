# Guy
!! VISIT HERE: http://34.27.14.14/

Recipies on your terms! Guy is a chatbot, powered by Flask, Python, and Gemini, that gives you recipies based on your desires!

## How It Works
- Users can start a conversation by clicking the **"Start Chatting"** button on the home page, or by clicking the **"Chat"** tab.
- Given a prompt, the following will occur:
  - First, prompts are processed through an [internal database](https://github.com/josephrmartinez/recipe-dataset) to find matching recipes.
  - If no matches are found, the prompt is sent to the [Spoonacular API](https://spoonacular.com/food-api) to get a response.
  - The database/API response is processed through Gemini 1.5-pro, where a message is generated and returned to the user.
- The system maintains context throughout the conversation, so you can follow up previous messages:
  - But it doesn't save... so don't expect it to come back to the same conversation when you refresh the page.
