import weaviate
from weaviate.classes.config import Configure
import pandas as pd

csv_file_path = "recipes_medium.csv"

client = weaviate.connect_to_local()

try:
    if client.is_ready():
        print("Weaviate is ready.")
        # Check for "Recept_medium" instead of "Recept_medium_2"
        if not client.collections.exists("Recept_medium"):
            print("Creating the Recept_medium collection.")
            recipes = client.collections.create(
                name="Recept_medium",
                vectorizer_config=Configure.Vectorizer.text2vec_ollama(
                    api_endpoint="http://host.docker.internal:11434",
                    model="nomic-embed-text",
                ),
                generative_config=Configure.Generative.ollama(
                    api_endpoint="http://host.docker.internal:11434",
                    model="llama3.2",
                )
            )

            data = pd.read_csv(csv_file_path)
            recipes = client.collections.get("Recept_medium")

            with recipes.batch.dynamic() as batch:
                for row in data.itertuples():
                    batch.add_object({
                        "title": row.title,
                        "directions": row.directions,
                        "NER": row.NER,
                        "ingredients": row.ingredients,
                    })
        else:
            print("Collection 'Recept_medium' already exists.")
    else:
        print("Weaviate is not ready yet. Please try again later.")

finally:
    client.close()  # Ensure the client is always closed

#Check if the data is loaded
""" 
import weaviate
import json

client = weaviate.connect_to_local()

questions = client.collections.get("Recept_medium")

response = questions.query.near_text(
    query="if i have chicken, mushrooms, and cheese, what can i make?",
    limit=1
)

for obj in response.objects:
    print(json.dumps(obj.properties, indent=2))

client.close()  # Free up resources 

import weaviate

client = weaviate.connect_to_local()

questions = client.collections.get("Question")

response = questions.generate.near_text(
    query="pie",
    limit=2,
    grouped_task="Write me how to make a pie."
)

print(response.generated)  # Inspect the generated text

client.close()  # Free up resources
"""

