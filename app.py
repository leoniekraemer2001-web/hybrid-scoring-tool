import streamlit as st
import pandas as pd

# -------------------------------------------------------
# Seiteneinstellungen
# -------------------------------------------------------
st.set_page_config(
    page_title="Hybrid-Scoring-Tool",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------
# Kopfbereich
# -------------------------------------------------------
st.title("Hybrid-Scoring-Tool")
st.caption(
    "Objektive Einschätzung der Eignung von Homeoffice- und Hybridarbeit "
    "auf Basis zentraler organisationaler Faktoren."
)

# -------------------------------------------------------
# GLOBALE BASISDATEN (WICHTIG!)
# -------------------------------------------------------

kriterien = [
    "Wohlbefinden, Gesundheit & Work-Life-Balance",
    "Autonomie, Zeitsouveränität, Motivation & Engagement",
    "Soziale Einbindung & Teamkontakt",
    "Führungsstil & Kultur",
    "Pendeldauer & Mobilitätsaufwand"
]

fragen = {
    "Wohlbefinden, Gesundheit & Work-Life-Balance":
        "Wie wirkt sich ein höherer Homeoffice-Anteil auf Wohlbefinden und Work-Life-Balance aus?",

    "Autonomie, Zeitsouveränität, Motivation & Engagement":
        "Wie schätzen Sie Motivation und Engagement im Homeoffice ein?",

    "Soziale Einbindung & Teamkontakt":
        "Wie stark sind Austausch und Teamkontakt ausgeprägt?",

    "Führungsstil & Kultur":
        "Wie gut ist die Führung auf hybrides Arbeiten eingestellt?",

    "Pendeldauer & Mobilitätsaufwand":
        "Wie hoch ist der durchschnittliche Pendelaufwand?"
}

beschreibungen = {
    "Wohlbefinden, Gesundheit & Work-Life-Balance": """
    <b>1:</b> klar nachteilig<br>
    <b>3:</b> gemischtes Bild<br>
    <b>5:</b> klar vorteilhaft
    """,

    "Autonomie, Zeitsouveränität, Motivation & Engagement": """
    <b>1:</b> deutlich schlechter<br>
    <b>3:</b> vergleichbar<br>
    <b>5:</b> deutlich besser
    """,

    "Soziale Einbindung & Teamkontakt": """
    <b>1:</b> sehr gering<br>
    <b>3:</b> durchschnittlich<br>
    <b>5:</b> sehr stark
    """,

    "Führungsstil & Kultur": """
    <b>1:</b> kontrollorientiert<br>
    <b>3:</b> gemischt<br>
    <b>5:</b> vertrauensbasiert
    """,

    "Pendeldauer & Mobilitätsaufwand": """
    <b>1:</b> < 5 km<br>
    <b>3:</b> 12–22 km<br>
    <b>5:</b> > 35 km
    """
}

# -------------------------------------------------------
# Wizard-State
# -------------------------------------------------------
if "step" not in st.session_state:
    st.session_state.step = 1

# =======================================================
# SCHRITT 1 – GRUNDVORAUSSETZUNGEN
# =======================================================
if st.session_state.step == 1:

    st.header("Schritt 1: Grundvoraussetzungen")

    col1, col2 = st.columns(2)

    with col1:
        praesenz = st.slider(
            "Präsenznotwendigkeit der Tätigkeiten",
            1, 5, 3
        )

    with col2:
        it = st.slider(
            "IT-Ausstattung & digitale Arbeitsfähigkeit",
            1, 5, 3
        )

    if st.button("✅ Voraussetzungen prüfen"):
        if praesenz >= 3 and it >= 3:
            st.session_state.step = 2
            st.rerun()
        else:
            st.error("Homeoffice ist unter diesen Bedingungen aktuell nur eingeschränkt sinnvoll.")

# =======================================================
# SCHRITT 2 – GEWICHTUNG
# =======================================================
elif st.session_state.step == 2:

    st.header("Schritt 2: Gewichtung")

    raw_weights = {}
    for k in kriterien:
        raw_weights[k] = st.slider(
            k, 1, 10, 5
        )

    if st.button("➡️ Gewichtung bestätigen"):
        total = sum(raw_weights.values())
        st.session_state.gewichte = {k: raw_weights[k] / total for k in kriterien}
        st.session_state.step = 3
        st.rerun()

# =======================================================
# SCHRITT 3 – BEWERTUNG & ERGEBNIS
# =======================================================
elif st.session_state.step == 3:

    st.header("Schritt 3: Bewertung")

    gesamtscore = 0.0
    for k in kriterien:
        st.markdown(f"### {k}")
        score = st.slider("Score", 1, 5, 3, key=f"{k}_score")
        st.markdown(beschreibungen[k], unsafe_allow_html=True)

        gesamtscore += score * st.session_state.gewichte[k]

    st.subheader("Ergebnis")
    st.metric("Gesamtscore", f"{gesamtscore:.2f} / 5.0")

    if st.button("🔄 Neu starten"):
        st.session_state.step = 1
        st.rerun()