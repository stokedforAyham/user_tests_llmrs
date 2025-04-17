import streamlit as st
import pandas as pd
import uuid
import json
from datetime import datetime

import sys
from pathlib import Path

# Add root to sys.path if needed
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from recommend_function import get_similar_movies
from rewrite_synopsis_v2 import rewrite_synopsis

st.markdown("""
    <style>
        /* Make the main content area wider */
        .main .block-container {
            max-width: 90%;
            padding-left: 3rem;
            padding-right: 3rem;
        }

        /* Increase base font size */
        html, body, div, p, label {
            font-size: 18px;
        }

        /* Slightly larger slider labels and form text */
        .stSlider label, .stRadio label, .stTextArea label {
            font-size: 18px !important;
        }
    </style>
""", unsafe_allow_html=True)

# === Load Dataset (cached) ===
@st.cache_data
def load_dataset():
    df = pd.read_csv("v8_ready_to_combine_vector.csv")
    df['title'] = df['title'].astype(str).str.strip()
    return df

df_full = load_dataset()
movie_titles = df_full['title'].dropna().unique().tolist()

# === Streamlit UI ===
st.title("🎬 Personalized Movie Synopsis Generator")

st.markdown("""
This app recommends a movie based on what you recently watched and rewrites its synopsis to see how well it matches your personal taste. 
Select a movie, define your preferences, and discover how the film is reframed just for you.
""")

# Language toggle
language = st.radio("Language / Sprache", ["English", "Deutsch"])
st.session_state.setdefault("session_id", str(uuid.uuid4()))

st.session_state.setdefault("run_count", 0)
st.session_state.setdefault("feedback_submitted", False)
if "consent_given" not in st.session_state:
    st.session_state.consent_given = False


if not st.session_state.consent_given:
    st.header("📝 Welcome to the Study" if language == "English" else "📝 Willkommen zur Studie")
    st.markdown(
        """
        In this short study, you are asked to test the app using **at least 3 movies** you have previously watched.
        For each one, you'll receive a personalized recommendation and rewritten synopsis.

        After each synopsis, you'll rate how well it matches your taste and whether you'd consider watching it.
        This will take **10–15 minutes**. Your input is anonymous and will be used for research purposes only.
        """ if language == "English" else
        """
        In dieser kurzen Studie wirst du gebeten, die App mit **mindestens 3 Filmen** zu testen, die du bereits gesehen hast.
        Für jeden erhältst du eine personalisierte Empfehlung und eine umgeschriebene Zusammenfassung.

        Danach wirst du bewerten, wie gut die Zusammenfassung deinen Vorlieben entspricht und ob du den Film sehen würdest.
        Das dauert etwa **10–15 Minuten**. Deine Daten sind anonym und werden ausschließlich für Forschungszwecke verwendet.
        """
    )

    if st.checkbox("I agree to participate and understand how my data will be used." if language == "English" else "Ich stimme zu und verstehe, wie meine Daten verwendet werden."):
        st.session_state.consent_given = True
        st.rerun()
    st.stop()


# === Form for inputs ===
with st.form("user_preferences_form"):
    st.markdown("**🎬 A Movie You Have Watched**" if language == "English" else "**🎬 Ein Film, den du gesehen hast**")
    watched_movie = st.selectbox(
        "Select a movie you have watched:" if language == "English" else "Wähle einen Film, den du gesehen hast:", 
        movie_titles
    )

    st.markdown("---")
    st.markdown("**🧭 Your Preferences**" if language == "English" else "**🧭 Deine Präferenzen**")

    tone = st.text_input(
        "Preferred emotional tone" if language == "English" else "Bevorzugter Ton",
        help="e.g., uplifting, dark, bittersweet" if language == "English" else "z.B. aufmunternd, düster, bittersüß"
    )
    style = st.text_input(
        "Preferred narrative style" if language == "English" else "Bevorzugter Erzählstil",
        help="e.g., fast-paced, minimalist, nonlinear" if language == "English" else "z.B. schnell, minimalistisch, nicht-linear"
    )

    genre_set = set()
    df_full['genre'].dropna().apply(lambda x: genre_set.update([g.strip() for g in x.split(',')]))
    genre_options = sorted(list(genre_set))

    genre_prefs = st.multiselect(
        "Preferred genres" if language == "English" else "Bevorzugte Genres", 
        options=genre_options,
        help="Select one or more genres you prefer" if language == "English" else "Wähle ein oder mehrere bevorzugte Genres"
    )

    likes = st.text_area(
        "Themes or elements you enjoy" if language == "English" else "Themen oder Elemente, die du magst",
        help="e.g., strong characters, unexpected twists" if language == "English" else "z.B. starke Charaktere, unerwartete Wendungen"
    )
    avoid = st.text_area(
        "Elements you'd prefer to avoid" if language == "English" else "Inhalte, die du vermeiden möchtest",
        help="e.g., violence, slow pacing" if language == "English" else "z.B. Gewalt, langsames Tempo"
    )

    submitted = st.form_submit_button("Generate Personalized Synopsis" if language == "English" else "Personalisierte Zusammenfassung generieren")

if submitted:
    user_profile = {
        "tone": tone.strip(),
        "style": style.strip(),
        "genre_preferences": genre_prefs,
        "likes": likes.strip(),
        "avoid": avoid.strip()
    }
    skipped_fields = [k for k, v in user_profile.items() if not v]

    watched_row = df_full[df_full['title'] == watched_movie].iloc[0]
    watched_synopsis = watched_row['synopsis']

    recommendations = get_similar_movies(watched_movie, top_n=5)
    top_rec = recommendations[0]
    recommended_title = top_rec['title']
    rec_row = df_full[df_full['title'] == recommended_title].iloc[0]
    rec_synopsis = rec_row['synopsis']
    rec_genre = rec_row.get('genre', '')
    rec_reviews = rec_row.get('review_text', '')

    personalized = rewrite_synopsis(
        recommended_title,
        user_profile,
        rec_synopsis,
        rec_genre,
        rec_reviews,
        watched_title=watched_movie,
        watched_synopsis=watched_synopsis,
        language=language
    )

    st.session_state.personalized = personalized
    st.session_state.recommended_title = recommended_title
    st.session_state.rec_genre = rec_genre
    st.session_state.recommended_synopsis = rec_synopsis
    st.session_state.recommendations = recommendations
    st.session_state.watched_movie = watched_movie
    st.session_state.watched_synopsis = watched_synopsis
    st.session_state.user_profile = user_profile
    st.session_state.skipped_fields = skipped_fields


if st.session_state.run_count >= 3:
    st.success("🎉 You've completed all 3 test runs. Thank you for participating!")
    
    final_feedback = st.text_area("Any final feedback or reflections?" if language == "English" else "Abschließendes Feedback oder Gedanken?", key="final_feedback")
    final_log = {
        "timestamp": datetime.now().isoformat(),
        "session_id": st.session_state.session_id,
        "final_feedback": final_feedback
    }
    try:
        with open("interaction_logs.jsonl", "a") as f:
            f.write(json.dumps(final_log) + "\n")
    except Exception as e:
        st.error(f"Failed to save final feedback. Error: {e}")
    st.stop()
    
st.markdown(f"**Run {st.session_state.run_count + 1} of 3**" if language == "English" else f"**Durchlauf {st.session_state.run_count + 1} von mindestens 3**")

if "personalized" in st.session_state:
    st.subheader("Recommended Movie" if language == "English" else "Empfohlener Film")
    st.markdown(f"**{st.session_state.recommended_title}** — *{st.session_state.rec_genre}*")

    st.subheader("Personalized Synopsis" if language == "English" else "Personalisierte Zusammenfassung")
    st.write(st.session_state.personalized)

    st.subheader("Other Recommendations" if language == "English" else "Weitere Empfehlungen")
    with st.expander("See other recommendations" if language == "English" else "Weitere Empfehlungen anzeigen"):
        for rec in st.session_state.recommendations[1:]:
            st.markdown(f"**{rec['title']}** — *{rec['genre']}*")

if st.session_state.get("feedback_submitted", False):
    st.session_state.feedback_submitted = False
    
with st.form("feedback_form"):
    st.subheader("📝 Feedback on This Recommendation" if language == "English" else "📝 Rückmeldung zu dieser Empfehlung")
    rating_alignment = st.slider(
        "How well did the synopsis match your preferences?" if language == "English" else "Wie gut entsprach die Zusammenfassung deinen Vorlieben?",
        1, 5, 3, key="rating_alignment"
    )
    rating_engagement = st.slider(
        "How compelling or appealing did this synopsis feel to you?" if language == "English" else "Wie überzeugend oder ansprechend fandest du diese Zusammenfassung?",
        1, 5, 3, key="rating_engagement"
    )
    would_watch = st.radio("Would you watch this movie based on this synopsis?" if language == "English" else "Würdest du diesen Film basierend auf dieser Zusammenfassung ansehen?", ["Yes" if language == "English" else "Ja", "No" if language == "English" else "Nein"])
    comment = st.text_area("Any thoughts or suggestions?" if language == "English" else "Gedanken oder Anmerkungen?")

    submit_feedback = st.form_submit_button("Submit Feedback", disabled=st.session_state.get("feedback_submitted", False))


    
if submit_feedback:
    st.session_state.feedback_submitted = True
    st.session_state.run_count += 1

    log_data = {
        "timestamp": datetime.now().isoformat(),
        "session_id": st.session_state.session_id,
        "language": language,
        "movie_watched": st.session_state.watched_movie,
        "user_profile": st.session_state.user_profile,
        "skipped_fields": st.session_state.skipped_fields,
        "watched_synopsis": st.session_state.watched_synopsis,
        "recommended_movie": st.session_state.recommended_title,
        "recommended_synopsis": st.session_state.recommended_synopsis,
        "personalized_synopsis": st.session_state.personalized,
        "top_n_recommendations": st.session_state.recommendations,
        "rating_match": rating_alignment,
        "rating_engagement": rating_engagement,
        "would_watch": would_watch,
        "user_feedback_text": comment,
        "run_number": st.session_state.run_count
    }

    try:
        with open("interaction_logs.jsonl", "a") as f:
            f.write(json.dumps(log_data) + "\n")
        st.success("✅ Feedback submitted. You may now try another movie." if language == "English" else "✅ Feedback übermittelt. Du kannst nun einen weiteren Film ausprobieren." if st.session_state.run_count < 3 else "✅ Feedback submitted. Study complete!" if language == "English" else "✅ Feedback übermittelt. Die Studie ist abgeschlossen!")
        if st.session_state.run_count < 3:
            if st.button("Try another movie"):
                st.session_state.pop("personalized", None)
                st.session_state.feedback_submitted = False
                st.rerun()
    except Exception as e:
        st.error("Failed to save feedback. Please try again." if language == "English" else "Feedback konnte nicht gespeichert werden. Bitte versuche es erneut.")


