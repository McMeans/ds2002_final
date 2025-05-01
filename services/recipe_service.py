import sqlite3
import os
import ast
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
        
        # common words to ignore in search
        self.ignore_words = {'i', 'please', 'thank', 'you', 'thanks', 'would', 'like', 'dish', 'with', 'and', 'want', 'give', 'the', 'a', 'an', 'some', 'any', 'all', 'my', 'your', 'their', 'our', 'this', 'that', 'these', 'those', 'what', 'which', 'who', 'whom', 'whose', 'where', 'when', 'why', 'how', 'if', 'then', 'else', 'when', 'as', 'because', 'since', 'while', 'after', 'before', 'until', 'unless', 'although', 'though', 'even', 'if', 'whether', 'while', 'whereas', 'despite', 'in', 'on', 'at', 'by', 'for', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'}

    def search_recipes_db(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        try:
            # split query into each word/term and filter out common words
            search_terms = [term.strip() for term in query.lower().split() 
                          if len(term.strip()) > 2 and term.strip() not in self.ignore_words]
            
            if not search_terms:
                return []
            
            # create conditions for each search term
            title_conditions = []
            ingredient_conditions = []
            params = []
            
            for term in search_terms:
                title_conditions.append("LOWER(title) LIKE ?")
                ingredient_conditions.append("LOWER(ingredients) LIKE ?")
                params.append(f'%{term}%')
                params.append(f'%{term}%')
            
            # create the final condition that requires ALL terms to be present in either the title OR the ingredients
            final_condition = f"""
                (
                    ({' AND '.join(title_conditions)})
                    OR
                    ({' AND '.join(ingredient_conditions)})
                )
            """
            
            # create the final query
            sql_query = f'''
                SELECT * FROM recipes 
                WHERE {final_condition}
                LIMIT ?
            '''
            params.append(limit)
            
            # connect to db and find matches
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(sql_query, params)
            recipes = cursor.fetchall()
            conn.close()
            
            # return matches, if any
            if recipes:
                results = []
                for recipe in recipes:
                    # convert ingredients from python list string to actual list
                    try:
                        ingredients = ast.literal_eval(recipe['ingredients']) if recipe['ingredients'] else []
                    except (SyntaxError, ValueError) as e:
                        # if parsing fails, treat it as a single string
                        ingredients = [recipe['ingredients']] if recipe['ingredients'] else []
                    
                    recipe_dict = dict(recipe)
                    recipe_dict['ingredients'] = ingredients
                    results.append(recipe_dict)
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
            results = response.json().get('results', [])
            return results
        except Exception as e:
            # error handling
            print(f"Error calling Spoonacular API: {e}")
            return []

    def search_recipes(self, query: str) -> List[Dict[str, Any]]:
        # try local database
        results = self.search_recipes_db(query)
        
        # try api if no results
        if not results:
            results = self.search_spoonacular(query)
            
        return results