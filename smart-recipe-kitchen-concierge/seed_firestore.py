# Copyright 2026 Google LLC
# Seed recipes into Firestore for Smart Recipe & Kitchen Concierge

from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-5dcffec924a4"
COLLECTION_NAME = "recipes"

SEED_RECIPES = [
    {
        "id": "lemon-herb-roast-chicken",
        "title": "Lemon Herb Roasted Chicken",
        "cuisine": "Mediterranean",
        "prep_time_minutes": 15,
        "cook_time_minutes": 50,
        "servings": 4,
        "difficulty": "Easy",
        "dietary_tags": ["gluten-free", "high-protein", "dairy-free"],
        "ingredients": [
            "1 whole chicken (cut into pieces) or 4 bone-in thighs",
            "2 lemons (juiced and sliced)",
            "4 cloves garlic (minced)",
            "2 tbsp fresh rosemary (chopped)",
            "2 tbsp olive oil",
            "1 tsp salt",
            "1/2 tsp black pepper"
        ],
        "instructions": [
            "Preheat oven to 400°F (200°C).",
            "Whisk olive oil, lemon juice, minced garlic, rosemary, salt, and pepper in a bowl.",
            "Toss chicken in the marinade and arrange in a baking dish with lemon slices.",
            "Roast for 45-50 minutes until skin is golden brown and internal temp reaches 165°F (74°C).",
            "Rest for 5 minutes before serving."
        ]
    },
    {
        "id": "creamy-tuscan-white-bean-soup",
        "title": "Creamy Tuscan White Bean Soup",
        "cuisine": "Italian",
        "prep_time_minutes": 10,
        "cook_time_minutes": 25,
        "servings": 4,
        "difficulty": "Easy",
        "dietary_tags": ["vegan", "vegetarian", "gluten-free", "dairy-free"],
        "ingredients": [
            "2 cans (15 oz each) cannellini beans (rinsed)",
            "1 medium yellow onion (diced)",
            "3 cloves garlic (minced)",
            "4 cups vegetable broth",
            "2 cups chopped Tuscan kale",
            "1 tsp dried oregano",
            "2 tbsp olive oil",
            "Salt and black pepper to taste"
        ],
        "instructions": [
            "Heat olive oil in a pot over medium heat; sauté onion and garlic until fragrant (4 mins).",
            "Add oregano, 1.5 cans of beans, and vegetable broth. Simmer for 15 minutes.",
            "Blend half the soup with an immersion blender to create a rich creamy base.",
            "Stir in remaining whole beans and chopped kale. Simmer 5 mins until kale wilts.",
            "Season with salt and pepper to taste; serve hot with olive oil drizzle."
        ]
    },
    {
        "id": "avocado-pesto-pasta",
        "title": "Creamy Avocado Pesto Pasta",
        "cuisine": "Italian",
        "prep_time_minutes": 15,
        "cook_time_minutes": 10,
        "servings": 2,
        "difficulty": "Easy",
        "dietary_tags": ["vegetarian", "dairy-free"],
        "ingredients": [
            "8 oz fettuccine or penne",
            "1 ripe avocado (pitted and scooped)",
            "1 cup fresh basil leaves",
            "2 cloves garlic",
            "1/4 cup walnuts or pine nuts",
            "2 tbsp lemon juice",
            "2 tbsp extra virgin olive oil",
            "1/2 tsp salt"
        ],
        "instructions": [
            "Cook pasta in salted boiling water according to package directions; reserve 1/4 cup pasta water.",
            "In a food processor, blend avocado, basil, garlic, walnuts, lemon juice, olive oil, and salt until smooth.",
            "Drain pasta and toss immediately with avocado pesto, adding reserved pasta water as needed for consistency.",
            "Garnish with black pepper and fresh basil leaves."
        ]
    },
    {
        "id": "spicy-tofu-stir-fry",
        "title": "Crispy Tofu & Veggie Stir-Fry",
        "cuisine": "Asian",
        "prep_time_minutes": 20,
        "cook_time_minutes": 15,
        "servings": 3,
        "difficulty": "Medium",
        "dietary_tags": ["vegan", "vegetarian", "dairy-free"],
        "ingredients": [
            "14 oz extra-firm tofu (pressed and cubed)",
            "1 head broccoli (cut into florets)",
            "1 red bell pepper (sliced)",
            "2 tbsp soy sauce or tamari",
            "1 tbsp sesame oil",
            "1 tbsp sriracha or chili paste",
            "1 tbsp cornstarch",
            "1 tbsp grated fresh ginger"
        ],
        "instructions": [
            "Toss cubed tofu with cornstarch and a pinch of salt.",
            "Pan-fry tofu in sesame oil over medium-high heat until golden and crispy (8-10 mins). Remove and set aside.",
            "In the same pan, stir-fry broccoli and bell pepper for 4 minutes.",
            "Mix soy sauce, sriracha, and ginger. Pour into skillet with vegetables and return crispy tofu.",
            "Toss for 2 minutes until glossy and coated. Serve over jasmine rice or quinoa."
        ]
    }
]

def seed():
    db = firestore.Client(project=PROJECT_ID)
    print(f"Connecting to Firestore for project: {PROJECT_ID}...")
    batch = db.batch()
    for recipe in SEED_RECIPES:
        doc_ref = db.collection(COLLECTION_NAME).document(recipe["id"])
        batch.set(doc_ref, recipe)
        print(f"  Queued recipe: {recipe['title']} ({recipe['id']})")
    batch.commit()
    print(f"Successfully seeded {len(SEED_RECIPES)} recipes into '{COLLECTION_NAME}' collection!")

if __name__ == "__main__":
    seed()
