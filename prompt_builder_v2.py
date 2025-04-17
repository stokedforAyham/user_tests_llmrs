def build_prompt(
    movie_title: str,
    user_profile: dict,
    synopsis: str,
    genre: str,
    reviews: str,
    watched_title: str = None,
    watched_synopsis: str = None,
    language: str = "English"
) -> str:
    """
    Build a personalized prompt for rewriting a movie synopsis.
    """
    prompt = f"You are a movie recommendation assistant. A user has recently watched the film \"{watched_title}\"."

    if watched_synopsis:
        prompt += f" Here is a short summary of that movie: {watched_synopsis.strip()}"

    prompt += f" Now you want to recommend the movie \"{movie_title}\"."

    if synopsis:
        prompt += f" Here is its original synopsis: {synopsis.strip()}"

    if genre:
        prompt += f" The genre(s) of this movie are: {genre}."

    if reviews:
        prompt += f" Here are some viewer opinions: {reviews.strip()}"

    if any(user_profile.values()):
        prompt += "\n\nThe user's preferences are as follows:"
        if user_profile.get("tone"):
            prompt += f"\n- Preferred tone: {user_profile['tone']}"
        if user_profile.get("style"):
            prompt += f"\n- Preferred narrative style: {user_profile['style']}"
        if user_profile.get("genre_preferences"):
            genres = ", ".join(user_profile['genre_preferences'])
            prompt += f"\n- Enjoyed genres: {genres}"
        if user_profile.get("likes"):
            prompt += f"\n- Enjoyed themes or elements: {user_profile['likes']}"
        if user_profile.get("avoid"):
            prompt += f"\n- Disliked themes or things to avoid: {user_profile['avoid']}"

    prompt += (
        "\n\nRewrite the synopsis of the recommended movie in a way that highlights the aspects of it that may be interesting or emotionally resonant to the user, "
        "based on their past viewing and preferences. Do not make up facts. Maintain the core plot but emphasize connections.\n\n"
        "Always prioritize the information explicitly given in the synopsis, genre, and reviews. "
        "Only use your own external knowledge about the recommended movie if the provided materials are insufficient to support a meaningful personalized rewrite.\n"
        "If you must use external knowledge, apply the same principles: \n"
        "- Do not fabricate events, scenes, or character arcs.\n"
        "- Do not invent thematic depth that is not implied or supported.\n"
        "- Only highlight elements that genuinely align with the user's preferences.\n\n"
        "If even external knowledge is not sufficient to personalize meaningfully, say so clearly instead of guessing or exaggerating."
    )

    if language == "Deutsch":
        prompt += "\n\nPlease write the final personalized synopsis in German."

    return prompt
