from prompt_builder_v2 import build_prompt
import openai
import os

# Set your OpenAI API key (or use environment variable)
import os
openai.api_key = "sk-proj..."

def rewrite_synopsis(
    movie_title: str,
    user_profile: dict,
    original_synopsis: str,
    genre: str,
    reviews: str,
    watched_title: str,
    watched_synopsis: str,
    language: str = "English"
) -> str:
    """
    Generate a personalized synopsis for a recommended movie,
    based on a user profile and their recently watched movie.
    """
    prompt = build_prompt(
        movie_title=movie_title,
        user_profile=user_profile,
        synopsis=original_synopsis,
        genre=genre,
        reviews=reviews,
        watched_title=watched_title,
        watched_synopsis=watched_synopsis,
        language=language
    )

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful and insightful movie assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=600
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"❌ Error from OpenAI: {e}")
        return "[Error generating synopsis]"