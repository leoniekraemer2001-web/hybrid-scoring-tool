import streamlit as st
import pandas as pd

st.set_page_config(page_title="Hybrid-Scoring-Tool", layout="wide")

# -------------------------------------------------------
# Kopfbereich der App (Titel, Untertitel, Anleitung, Style)
# -------------------------------------------------------

st.markdown(
    """
    <style>
    /* Titel kleiner & kompakter */
    h1 {
        font-size: 2.2rem !important;
        margin-bottom: 0.2rem;
    }

    /* Untertitel leicht grau & kleiner */
    .subtitle {
        font-size: 1.1rem;
        color: #555;
        margin-bottom: 1.5rem;
    }

    /* Abschnittsüberschriften (z. B. "Ihre Einschätzung") kleiner */
    h2 {
        font-size: 1.6rem !important;
        margin-top: 2rem !important;
        margin-bottom: 0.5rem !important;
    }

    /* Anleitungstext */
    .instruction-box {
        background-color: #f5f7fa;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        border-left: 5px solid #4a7aff;
        margin-top: 1rem;
        margin-bottom: 2rem;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Titel & Untertitel
st.markdown("<h1>Hybrid-Scoring-Tool</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Objektive Analyse Ihrer Rahmenbedingungen – datenbasiert und in wenigen Schritten zur passenden Homeoffice-Policy</div>", unsafe_allow_html=True)

# Anleitung
st.markdown(
    """
    <div class='instruction-box'>
    <b>Anleitung:</b><br>
    1️⃣ Bewerten Sie jedes Kriterium anhand Ihrer aktuellen Situation (Score 1–5).<br>
    2️⃣ Die Bedeutung der Scores von 1-5 werden bei jeder Skala erläutert. Falls Sie ein Kriterium nicht beurteilen können, empfehlen wir den Score 3 auszuwählen. <br>
    3️⃣ Am Ende erhalten Sie eine konkrete Homeoffice-Empfehlung.<br>
    </div>
    """,
    unsafe_allow_html=True
)

# Gewichte und Reihenfolge
gewichte = {
    "Pendelaufwand": 0.2,
    "Büroflächenreduktion": 0.055,
    "CO₂-Einsparung": 0.1025,
    "Work-Life-Balance": 0.1525,
    "Team-/Führungskultur": 0.1175,
    "Mitarbeiterakzeptanz": 0.1,
    "Aufgaben-/Persönlichkeitsfit": 0.04,
    "Produktivitätseffekte": 0.0975,
    "Präsenznotwendigkeit": 0.085,
    "IT-Infrastruktur": 0.05
}

# Self-Assessment Skalen
beschreibungen = {
    "Pendelaufwand": """Score 1: <5 km Ø Pendelstrecke \
 Score 2: 5-12 km Ø Pendelstrecke \
Score 3: 12-22 km Ø Pendelstrecke \
Score 4: 22-35 km Ø Pendelstrecke \
Score 5: >35 km Ø Pendelstrecke""",
    
    "Büroflächenreduktion": """Score 1: Einzelbüros, 100% Auslastung \
Score 2: Grundlegende Hybrid-Struktur (<30% Hotdesking) \
Score 3: Moderate Adaptivität (30-50% Hotdesking) \
Score 4: Hohe Adaptivität (50-70% Hotdesking, Activity-Based)\
Score 5: Vollständig adaptiv (>70% Hotdesking, Desk-Sharing)""",
    
    "CO₂-Einsparung": """Score 1: <10 kg CO₂e Einsparung/FTE/Tag \
Score 2: 10-25 kg CO₂e Einsparung/FTE/Tag \
Score 3: 25-40 kg CO₂e Einsparung/FTE/Tag (DE-Durchschnitt) \
Score 4: 40-60 kg CO₂e Einsparung/FTE/Tag \
Score 5: >60 kg CO₂e Einsparung/FTE/Tag""",
    
    "Work-Life-Balance": """Score 1: Deutlich schlechter, starke Grenzverwischung \
Score 2: Eher negativ, etwas mehr Stress \
Score 3: Ausgewogen oder leicht besser als Büro (typisch) \
Score 4: Deutlich besser, gute Zeitgewinne \
Score 5: Sehr hoch, flexible Zeitgestaltung""",
    
    "Team-/Führungskultur": """Score 1: Keine Remote-Erfahrung, Micromanagement \
Score 2: Erste Erfahrung (<1 Jahr), skeptische Manager \
Score 3: 1-3 Jahre Erfahrung, Video-Meetings Standard \
Score 4: Reife Hybrid-Kultur (>3 Jahre), asynchrone Arbeit \
Score 5: Weltklasse Remote-First (GitLab-Style)""",
    
    "Mitarbeiterakzeptanz": """Score 1: <10% Mitarbeiter nutzen HO \
Score 2: 11-20% Mitarbeiter nutzen HO \
Score 3: 21-45% Mitarbeiter nutzen HO (DE-Durchschnitt) \
Score 4: 46-75% Mitarbeiter nutzen HO \
Score 5: >75% Mitarbeiter nutzen HO""",
    
    "Aufgaben-/Persönlichkeitsfit": """Score 1: Stark team-/ortsgetrieben, niedrige Selbstdisziplin \
Score 2: Teilweise ortsabhängig, begrenzte Selbstorganisation \
Score 3: Mischprofil, durchschnittlich organisiert (typisch) \
Score 4: Autonome Aufgaben, gut strukturiert \
Score 5: Wissensorientiert, hohe Gewissenhaftigkeit""",
    
    "Produktivitätseffekte": """Score 1: Deutlicher Rückgang < -10% \
Score 2: Leichter Rückgang -10% bis 0% \
Score 3: 0-10% (DE-Durchschnitt, neutral) \
Score 4: +10-20% Produktivität \
Score 5: >+20% Produktivität""",
    
    "Präsenznotwendigkeit": """Score 1: >70% Face-to-Face oder physische Aufgaben \
Score 2: 50-70% Präsenz erforderlich \
Score 3: 30-50% Präsenz erforderlich (typisch) \
Score 4: 10-30% Präsenz erforderlich \
Score 5: <10% Präsenz erforderlich""",
    
    "IT-Infrastruktur": """Score 1: Kein VPN, schlechte Internet, keine Tools \
Score 2: Basis-VPN, Email + File-Sharing \
Score 3: Gutes VPN, MS Teams, stabiles Internet \
Score 4: Enterprise VPN, Cloud-Tools, Cybersecurity \
Score 5: Weltklasse IT (Zero-Trust, Global Load-Balancing)"""
}

# Mapping
def get_empfehlung(score):
    if score < 2.5: return "0-1 Tage (Minimal)"
    elif score < 3.5: return "2 Tage (Starter)"
    elif score < 4.2: return "3 Tage (Ausgereift)"
    else: return "4-5 Tage (Remote-First)"

# Scores
scores = {}
gesamtscore = 0

for kriterium, gewicht in gewichte.items():
    st.markdown(f"### {kriterium}")
    col1, col2 = st.columns([1, 3])
    with col1:
        score = st.slider(kriterium, 1, 5, 3, key=f"{kriterium}_score")
    with col2:
        st.markdown(f"{beschreibungen[kriterium]}")
    scores[kriterium] = score
    gesamtscore += score * gewicht
    st.markdown("---")

# Ergebnisse
st.header("**Ihr Ergebnis**")
col1, col2, col3 = st.columns(3)
col1.metric("Gesamtscore", f"{gesamtscore:.2f}/5.0")
col2.metric("Policy-Empfehlung", get_empfehlung(gesamtscore))

# Spezifische Warnungen zu IT-Infrastruktur / Präsenznotwendigkeit
it_score = scores.get("IT-Infrastruktur")
praesenz_score = scores.get("Präsenznotwendigkeit")

if it_score is not None and it_score < 3:
    st.warning(
        f"⚠️ Da Sie beim Kriterium **IT-Infrastruktur** nur einen Score von {it_score} ausgewählt haben, "
        "ist die empfohlene Anzahl an Homeoffice-Tagen nur dann sinnvoll, wenn die technische "
        "Infrastruktur (VPN, Bandbreite, Kollaborationstools, Support) zuvor ausreichend ausgebaut wird."
    )

if praesenz_score is not None and praesenz_score < 3:
    st.warning(
        f"⚠️ Da Sie beim Kriterium **Präsenznotwendigkeit** nur einen Score von {praesenz_score} ausgewählt haben, "
        "sollten Sie zunächst prüfen, inwiefern Präsenzanforderungen organisatorisch reduziert, "
        "delegiert oder digitalisiert werden können, bevor eine hohe Homeoffice-Quote umgesetzt wird."
    )

# -------------------------------------------------------
# Handlungsempfehlungen (bei Scores 1–2)
# -------------------------------------------------------

st.subheader("Handlungsempfehlungen")

# Empfehlungen
empfehlungen = {
    "Büroflächenreduktion": {
        "problem": "Kaum Hotdesking, Präsenzstruktur stark ausgeprägt.",
        "maßnahmen": [
            "Buchungssystem oder einfache Desksharing-Regeln einführen.",
            "Meetingräume flexibilisieren → Fokusräume schaffen, Doppelbelegungen reduzieren."
        ]
    },
    "CO₂-Einsparung": {
        "problem": "Geringe Nachhaltigkeitseffekte.",
        "maßnahmen": [
            "Anreize schaffen: JobRad, ÖPNV-Zuschuss, Ladeinfrastruktur.",
            "Gebäudebetrieb an Belegung koppeln (Heizung/Beleuchtung nur in genutzten Zonen)."
        ]
    },
    "Mitarbeiterakzeptanz": {
        "problem": "Geringe Nutzung oder Skepsis gegenüber Homeoffice.",
        "maßnahmen": [
            "Ursachenanalyse: anonyme Umfrage oder Workshop.",
            "Einstieg über „sanftes Hybrid“ (z. B. 1–2 freiwillige HO‑Tage).",
            "Erfolgsgeschichten kommunizieren („Best Practices aus anderen Teams“)."
        ]
    },
    "Team-/Führungskultur": {
        "problem": "Skepsis, wenig Remote-Kompetenz, Micromanagement.",
        "maßnahmen": [
            "Führungskräftetraining zum Thema „Führen auf Distanz“.",
            "Erwartungstransparenz: Output statt Präsenz messen.",
            "Team-Working-Agreements erstellen (Kommunikationsregeln, Kernzeiten, Meetingformen)."
        ]
    },
    "Aufgaben-/Persönlichkeitsfit": {
        "problem": "Tätigkeiten oder Mitarbeitende kaum remote-tauglich.",
        "maßnahmen": [
            "Schulungen in Selbstorganisation, Priorisierung.",
            "Einführung klarer täglicher Strukturen (Check-in, Tagesziele)."
        ]
    },
    "Produktivitätseffekte": {
        "problem": "Homeoffice senkt Produktivität.",
        "maßnahmen": [
            "Ursachen messen: Ablenkung? Technik? Kommunikation?",
            "Fokusphasen einführen (z. B. „No-Meeting-Wednesday“)."
        ]
    },
    "Work-Life-Balance": {
        "problem": "Mitarbeitende haben durch HO eher Nachteile.",
        "maßnahmen": [
            "Klare Regeln zur Erreichbarkeit einführen (z. B. keine Mails nach 18 Uhr).",
            "Schulung zu Selbstorganisation & Pausenmanagement anbieten.",
            "Digitale Pausen‑Reminder (Teams/Outlook)."
        ]
    }
}

# drei Kategorien werden ausgeschlossen:
kritische_kategorien_ausgeschlossen = {
    "IT-Infrastruktur",
    "Präsenznotwendigkeit",
    "Pendelaufwand"   # <--- NEU hinzugefügt
}

kritische_kriterien = [
    k for k, s in scores.items()
    if s <= 2 and k not in kritische_kategorien_ausgeschlossen
]

if len(kritische_kriterien) == 0:
    st.success("Keine kritischen Bereiche - Für alle relevanten Kriterien liegen solide oder gute Werte vor.")
else:
    for kriterium in kritische_kriterien:
        st.markdown(f"### {kriterium}")
        info = empfehlungen.get(kriterium)
        if info:
            st.markdown(f"**Problem:** {info['problem']}")
            for punkt in info["maßnahmen"]:
                st.markdown(f"- {punkt}")
        else:
            st.markdown("_Aktuell keine spezifischen Empfehlungen für dieses Kriterium hinterlegt._")
        st.markdown("---")

# Breakdown-Tabelle
st.subheader("Detail-Analyse")
df_data = [
    {
        "Kriterium": k,
        "Score": scores[k],
        "Gewicht": f"{gewichte[k]:.0%}",
        "Teilwert": f"{scores[k] * gewichte[k]:.2f}",
    }
    for k in scores
]
df = pd.DataFrame(df_data)
st.dataframe(df, use_container_width=True)

st.markdown("---")
st.markdown("*DHBW Lörrach | P.Gizewski, L. Krämer, L. Müller | © 2026*")