from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
import ollama
import weaviate
import json
import re
import logging

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level = logging.INFO, format = '%(asctime)s - %(levelname)s - %(message)s')

# API Key for USDA
usda_key = os.getenv('API_KEY')


# Function to get nutrients for a food item
def get_nutrients(food):
    url = f'https://api.nal.usda.gov/fdc/v1/foods/search?api_key={usda_key}&query={food}&pageSize=1'
    response = requests.get(url)

    #print(response.content)
    # Load JSON data
    data = response.json()

    nutrient_data = {}
    target_nutrients = {"Total lipid (fat)": "Fat", "Protein": "Protein", "Carbohydrate, by difference": "Carbs",
                        "Energy": "Calories"}

    for food in data.get('foods', []):
        food_name = food.get('description', 'Unknown')
        nutrients = food.get('foodNutrients', [])
        relevant_nutrients = {
            target_nutrients[nutrient['nutrientName']]: {
                'value': nutrient['value'],
                'unit': nutrient['unitName']
            }
            for nutrient in nutrients if nutrient['nutrientName'] in target_nutrients
        }
        nutrient_data[food_name] = relevant_nutrients
    food = ""
    # Display the results
    for food, nutrients in nutrient_data.items():
        for nutrient, details in nutrients.items():
            food = food + " " + nutrient + " " + str(details['value']) + " " + details['unit']
    return food


# Function to generate text using Ollama
def generate_text(prompt, model = 'llama3.2', options = ollama.Options(temperature = 0.5)):
    logging.info("Generating text with Ollama...")
    response = ollama.generate(
        model = model,
        options = options,
        prompt = prompt
    )
    logging.info("Text generated successfully.")
    return response


@app.route('/process', methods = ['GET'])
def process_input():
    try:
        # Parse input data from GET parameters
        user_input = request.args.get('input', '')
        logging.info(f"Received input: {user_input}")

        # Step 1: Process input
        first_prompt = f'''
        Do not make python code!!!!
        
        You need to extrac food-related data from a user's input. The input will describe ingredients, their quantities (if available), and sometimes nutrient requirements for a meal. Your job is to:

        Identify the ingredients mentioned in the input and list them in a ingredients array.
        Extract or infer the weights (in grams) corresponding to each food item. If no weight is provided for an item, assign reasonable default weights based on common serving sizes.
        Extract the nutrients array if specified. If this is missing, use the default values [600, 60, 40, 20] (representing calories, proteins, carbs and fats respectively).

        Input: The user will describe the meal or list of foods and optionally provide weights and nutrient requirements in natural language.

        The input is: {user_input}

        Output only three lists: ingredients, weights and nutrients (calories, proteins, carbs, fats) in this format:

        ingredients = [ingredient1, ingredient2, ingredient3]
        weights = [weight1, weight2, weight3]
        nutrients = [calories, protein, carbs, fat]  

        numbers need to be integers like 500, 50, 30, not 500.0, 50.0, 30.0!
        weights should contain appropriate measurement units like grams, milliliters, oz. or no units for individual items like eggs, apples, etc. (e.g. ['200g', '15', '100ml'])
        nutrients should only contain 4 values: calories, protein, carbs, fats and should be in the same order as the example above.

        example:
        ingredients = ['chicken', 'rice', 'curry', 'eggs', 'mustard', 'salt', 'olive oil']
        weights = ['200g', '100g', '50g', '3', '5ml', '1 tsp', '10ml']
        nutrients = [600, 60, 40, 20]

        Do not include any explanation, code, or additional text in the response.

        IMPORTANT: dont output program code, just output the lists as described above! for weights use units only for items that need them and wrap them in quotes like '200g' or '100ml' or '15' or '3' etc. dont put None or null, put estimated values if needed.
        '''
        completion = generate_text(first_prompt)
        response = completion['response']
        logging.info(f"Extracted response from the first prompt. {response}")

        # Updated regex patterns to include the keys
        ingredients_pattern = r"ingredients\s*=\s*(\[[^\]]+\])"
        weights_pattern = r"weights\s*=\s*(\[[^\]]+\])"
        nutrients_pattern = r"nutrients\s*=\s*(\[[^\]]+\])"

        # Extract the values using the updated patterns
        ingredients_match = re.search(ingredients_pattern, response)
        weights_match = re.search(weights_pattern, response)
        nutrients_match = re.search(nutrients_pattern, response)

        # Parse the matched groups
        ingredients = eval(ingredients_match.group(1)) if ingredients_match else []
        weights = eval(weights_match.group(1)) if weights_match else []
        nutrients = eval(nutrients_match.group(1)) if nutrients_match else []
        logging.info(f"Extracted ingredients: {ingredients}, weights: {weights}, nutrients: {nutrients}")

        # Step 2: Get nutritional values for each food
        meal_nutrients = ""
        for ingredient in ingredients:
            meal_nutrients += "\n" + get_nutrients(ingredient)

        # Step 3: Generate recipe
        client = weaviate.connect_to_local()
        questions = client.collections.get("Recept_medium")
        recepti = questions.query.near_text(
            query = f"if I have {', '.join(ingredients)}, what can I make?",
            limit = 1
        )
        recipe = ""
        for obj in recepti.objects:
            recipe += json.dumps(obj.properties, indent = 2)
        client.close()
        logging.info("Fetched recipe suggestions from Weaviate.")

        # Step 4: Generate final prompt for recipe
        final_prompt = f'''You are an expert in nutrition and cooking. Your task is to create a recipe using only the available ingredients that meet specific nutritional goals. Your input includes:

        The list of available ingredients: {ingredients}
        The amount of each ingredient (in corresponding unit or without unit): {weights}
        The nutritional values of each ingredient (calories, protein, carbs, fats): {meal_nutrients}
        A list of recipes that serve as inspiration for creating the dish: {recipe}

        Your goal is to create a unique recipe that:

        - Contains a total of(calories, protein, carbs, fats): {nutrients} (with an acceptable deviation of ±5%).
        - Uses only the available ingredients.
        - Includes detailed preparation instructions, specifying ingredient proportions and cooking or preparation methods.
        - Can serve as a complete meal.

        Format the output as follows:

        - Recipe name
        - List of ingredients with precise quantities (in grams or other measures)
        - Nutritional values of the final dish (calories, protein, carbs, fats)
        - Detailed preparation instructions
        - Do not mention yourself or anything that could lead users to think the recipe was generated by an AI, just write it as if you were a human expert in nutrition and cooking.

        IMPORTANT: You must ensure that the recipe uses only the available ingredients and weights provided in the input. If I have 200g of chicken and 100g of rice, the recipe should use these exact quantities (or less).

        If the specified nutritional goals cannot be met with the available ingredients, explain the limitations and suggest alternative ingredient combinations or adjustments.
        '''
        final_completion = generate_text(final_prompt)

        logging.info("Final recipe generated successfully.")

        return jsonify({
            "ingredients": ingredients,
            "weights": weights,
            "nutrients": nutrients,
            "recipe": final_completion['response']
        })
    except Exception as e:
        logging.error(f"Error processing input: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 8090)
