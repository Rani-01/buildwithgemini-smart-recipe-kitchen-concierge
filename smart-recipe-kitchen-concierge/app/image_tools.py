# Copyright 2026 Google LLC
# Image generation tool for Smart Recipe & Kitchen Concierge

import re
import uuid
from typing import Any, Dict
from google import genai
from google.cloud import storage
from google.genai import types

# Hardcoded project and bucket identifiers
PROJECT_ID = "qwiklabs-gcp-04-5dcffec924a4"
BUCKET_NAME = "recipe-concierge-media-qwiklabs-gcp-04-5dcffec924a4"
IMAGE_MODEL = "gemini-3.1-flash-lite-image"
LOCATION = "global"


async def generate_recipe_image(
    dish_name: str,
    visual_description: str,
    tool_context: Any = None
) -> Dict[str, Any]:
    """Generate a high-quality food photography image for a dish, save it as an artifact, and upload to public Cloud Storage.

    Args:
        dish_name: Name of the dish (e.g. 'Lemon Herb Roasted Chicken', 'Avocado Pesto Pasta').
        visual_description: Detailed visual description of plating, garnish, textures, and lighting.
        tool_context: Injected ToolContext used to save the artifact in the ADK Playground.

    Returns:
        A dictionary containing the dish name, public Cloud Storage URL, and artifact filename.
    """
    # 1. Initialize GenAI client in the global region
    client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

    prompt = (
        f"Professional food photography of {dish_name}. {visual_description}. "
        "Appetizing presentation, soft natural daylight, depth of field, vibrant colors, studio culinary setting."
    )

    response = await client.aio.models.generate_content(
        model=IMAGE_MODEL,
        contents=prompt
    )

    image_bytes = None
    mime_type = "image/jpeg"
    for candidate in response.candidates:
        if candidate.content and candidate.content.parts:
            for part in candidate.content.parts:
                if part.inline_data and part.inline_data.data:
                    image_bytes = part.inline_data.data
                    mime_type = part.inline_data.mime_type or "image/jpeg"
                    break
        if image_bytes:
            break

    if not image_bytes:
        return {"error": f"Failed to generate image for {dish_name}"}

    # Generate slugified filename
    slug = re.sub(r"[^a-z0-9]+", "_", dish_name.lower()).strip("_")
    unique_suffix = uuid.uuid4().hex[:8]
    ext = "png" if "png" in mime_type else "jpg"
    filename = f"{slug}_{unique_suffix}.{ext}"

    # 2. Save artifact using tool_context (shows up in Playground Artifacts panel)
    if tool_context and hasattr(tool_context, "save_artifact"):
        try:
            artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
            await tool_context.save_artifact(
                filename=filename,
                artifact=artifact_part
            )
        except ValueError as e:
            # Handle runners where artifact_service is not initialized (e.g. standalone test scripts)
            print(f"Note: artifact service not initialized in current runner context: {e}")

    # 3. Upload bytes directly to Cloud Storage (no local file written)
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(image_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"

    return {
        "dish_name": dish_name,
        "public_url": public_url,
        "filename": filename,
        "status": "success"
    }
