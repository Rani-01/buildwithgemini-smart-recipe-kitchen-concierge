# Copyright 2026 Google LLC
# Firestore read/write tools for Smart Recipe & Kitchen Concierge

from typing import Any, Dict, List, Optional
from google.cloud import firestore

# Project ID hardcoded as a string so it does not resolve to the numeric project ID on Agent Platform
PROJECT_ID = "qwiklabs-gcp-04-5dcffec924a4"
COLLECTION_NAME = "recipes"


def get_firestore_client() -> firestore.Client:
    """Returns a Firestore client initialized with the hardcoded GCP project ID."""
    return firestore.Client(project=PROJECT_ID)


def list_recipes(cuisine: Optional[str] = None, dietary_tag: Optional[str] = None) -> List[Dict[str, Any]]:
    """List and filter recipes from the kitchen catalog in Firestore.

    Args:
        cuisine: Optional filter by cuisine style (e.g. 'Mediterranean', 'Italian', 'Asian').
        dietary_tag: Optional filter by dietary tag (e.g. 'vegan', 'vegetarian', 'gluten-free', 'dairy-free').

    Returns:
        A list of matching recipe summaries containing id, title, cuisine, cook time, and dietary tags.
    """
    db = get_firestore_client()
    query = db.collection(COLLECTION_NAME)

    results = []
    for doc in query.stream():
        data = doc.to_dict()
        data["id"] = doc.id
        
        # In-memory filter for flexible matching
        if cuisine and cuisine.lower() not in data.get("cuisine", "").lower():
            continue
        if dietary_tag:
            tags = [t.lower() for t in data.get("dietary_tags", [])]
            if dietary_tag.lower() not in tags:
                continue

        results.append({
            "id": data["id"],
            "title": data.get("title"),
            "cuisine": data.get("cuisine"),
            "prep_time_minutes": data.get("prep_time_minutes"),
            "cook_time_minutes": data.get("cook_time_minutes"),
            "servings": data.get("servings"),
            "difficulty": data.get("difficulty"),
            "dietary_tags": data.get("dietary_tags", [])
        })
    return results


def get_recipe_details(recipe_id: str) -> Dict[str, Any]:
    """Retrieve full details for a specific recipe including ingredients and cooking instructions.

    Args:
        recipe_id: The unique identifier of the recipe (e.g. 'lemon-herb-roast-chicken').

    Returns:
        A dictionary containing the recipe title, ingredients, instructions, and cooking times, or an error dict if not found.
    """
    db = get_firestore_client()
    doc = db.collection(COLLECTION_NAME).document(recipe_id).get()
    if not doc.exists:
        return {"error": f"Recipe '{recipe_id}' not found in catalog."}
    
    data = doc.to_dict()
    data["id"] = doc.id
    return data


def add_or_update_recipe(
    recipe_id: str,
    title: str,
    cuisine: str,
    ingredients: List[str],
    instructions: List[str],
    prep_time_minutes: int = 15,
    cook_time_minutes: int = 30,
    servings: int = 4,
    difficulty: str = "Easy",
    dietary_tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Add a new recipe or update an existing one in the Firestore collection.

    Args:
        recipe_id: Unique slug/ID for the recipe (e.g. 'spicy-garlic-shrimp').
        title: Display title of the dish.
        cuisine: Cuisine style (e.g. 'Mexican', 'Italian', 'Thai').
        ingredients: List of ingredients with measurements.
        instructions: Step-by-step preparation instructions.
        prep_time_minutes: Preparation time in minutes.
        cook_time_minutes: Cooking time in minutes.
        servings: Number of servings this recipe yields.
        difficulty: Complexity level (e.g. 'Easy', 'Medium', 'Hard').
        dietary_tags: Optional list of dietary tags (e.g. ['gluten-free', 'dairy-free']).

    Returns:
        A confirmation dictionary indicating success and saved recipe details.
    """
    db = get_firestore_client()
    recipe_data = {
        "id": recipe_id,
        "title": title,
        "cuisine": cuisine,
        "ingredients": ingredients,
        "instructions": instructions,
        "prep_time_minutes": prep_time_minutes,
        "cook_time_minutes": cook_time_minutes,
        "servings": servings,
        "difficulty": difficulty,
        "dietary_tags": dietary_tags or []
    }
    db.collection(COLLECTION_NAME).document(recipe_id).set(recipe_data)
    return {"status": "success", "message": f"Recipe '{title}' saved successfully.", "recipe_id": recipe_id}
