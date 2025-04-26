import sqlite3
import os
from typing import List, Dict, Any
import requests
from dotenv import load_dotenv

load_dotenv()

class RecipeService:
    def __init__(self):
        # base information
        self.db_path = 'data/cleaned_recipes.db'
        self.csv_path = 'data/cleaned_recipes.csv'
        self.spoonacular_api_key = os.getenv('SPOONACULAR_API_KEY')
        self.base_url = 'https://api.spoonacular.com/recipes'

    def search_recipes_db(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        try:
            # split query into each word/term
            search_terms = [term.strip() for term in query.lower().split() if len(term.strip()) > 2]
            
            if not search_terms:
                return []
            
            # create conditions for these terms
            conditions = []
            params = []
            for term in search_terms:
                conditions.extend([
                    "LOWER(title) LIKE ?",
                    "LOWER(ingredients) LIKE ?",
                    "LOWER(instructions) LIKE ?"
                ])
                params.extend([f'%{term}%'] * 3)
            
            # combine conditions for a full query
            sql_query = f'''
                SELECT * FROM recipes 
                WHERE {' OR '.join(conditions)}
                LIMIT ?
            '''
            params.append(limit)
            
            # connect to db and find matches
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(sql_query, params)
            recipes = cursor.fetchall()
            conn.close()
            
            # return matches, if any
            if recipes:
                columns = [description[0] for description in cursor.description]
                results = [dict(zip(columns, recipe)) for recipe in recipes]
                return results
            return []
        except Exception as e:
            # error handling
            print(f"Error searching database: {e}")
            return []

    def search_spoonacular(self, query: str, number: int = 5) -> List[Dict[str, Any]]:
        if not self.spoonacular_api_key:
            return []
            
        try:
            # use complex search to find a recipe
            url = f"{self.base_url}/complexSearch"
            params = {
                'apiKey': self.spoonacular_api_key,
                'query': query,
                'number': number,
                'instructionsRequired': True,
                'addRecipeInformation': True
            }
            # return a match
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json().get('results', [])
        except Exception as e:
            # error handling
            print(f"Error calling Spoonacular API: {e}")
            return []