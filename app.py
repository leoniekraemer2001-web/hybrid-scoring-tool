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

    /* Abschnittsüberschriften */
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
    2️⃣ Die Bedeutung der Scores von 1-5 werden bei jeder Skala erläutert. Falls Sie ein Kriterium nicht beurteilen können, empfehlen wir den Score 3 (Deutscher Durchschnitt) auszuwählen. <br>
    3️⃣ Am Ende erhalten Sie eine konkrete Homeoffice-Empfehlung.<br>
    </div>
    """,
    unsafe_allow_html=True
)

# Gewichte
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

# Neue Fragen pro Kriterium
fragen = {
    "Pendelaufwand": "Wie weit pendelt Ihr Team durchschnittlich (einfache Strecke)?",
    "Büroflächenreduktion": "Wie stark ist Ihr Bereich bereits auf flexible Arbeitsplatznutzung ausgerichtet?",
    "CO₂-Einsparung": "Wie groß ist der realistische CO₂‑Einsparungseffekt pro Mitarbeitendem (durch weniger Pendeln & Büropräsenz)?",
    "Work-Life-Balance": "Wie wirkt sich hybrides/remote Arbeiten auf die Work‑Life‑Balance Ihres Teams aus?",
    "Team-/Führungskultur": "Wie reif ist Ihr Team im Umgang mit hybrider Zusammenarbeit (Vertrauen, Kommunikation, Selbstorganisation)?",
    "Mitarbeiterakzeptanz": "Wie viele Ihrer Mitarbeitenden nutzen Homeoffice regelmäßig bzw. stehen dem positiv gegenüber?",
    "Aufgaben-/Persönlichkeitsfit": "Wie gut eignen sich Aufgaben & Arbeitsweisen Ihres Teams für selbstständiges, ortsunabhängiges Arbeiten?",
    "Produktivitätseffekte": "Wie hat sich die Produktivität Ihres Teams durch hybrides/remote Arbeiten verändert?",
    "Präsenznotwendigkeit": "Wie viel Prozent der Tätigkeiten erfordern zwingend physische Anwesenheit vor Ort?",
    "IT-Infrastruktur": "Wie stabil, sicher & leistungsfähig ist die digitale Arbeitsumgebung Ihres Teams?"
}

# Self-Assessment Skalen
beschreibungen = {
    "Pendelaufwand": """
Score 1: <5 km Ø Pendelstrecke<br>
Score 2: 5–12 km Ø Pendelstrecke<br>
Score 3: 12–22 km Ø Pendelstrecke<br>
Score 4: 22–35 km Ø Pendelstrecke<br>
Score 5: >35 km Ø Pendelstrecke
""",
    "Büroflächenreduktion": """
Score 1: Einzelbüros, 100% Auslastung<br>
Score 2: Grundlegende Hybrid-Struktur (<30% Hotdesking)<br>
Score 3: Moderate Adaptivität (30–50% Hotdesking)<br>
Score 4: Hohe Adaptivität (50–70% Hotdesking, Activity-Based)<br>
Score 5: Vollständig adaptiv (>70% Hotdesking, Desk-Sharing)
""",
    "CO₂-Einsparung": """
Score 1: <10 kg CO₂e Einsparung/FTE/Tag<br>
Score 2: 10–25 kg CO₂e Einsparung/FTE/Tag<br>
Score 3: 25–40 kg CO₂e Einsparung/FTE/Tag (DE-Durchschnitt)<br>
Score 4: 40–60 kg CO₂e Einsparung/FTE/Tag<br>
Score 5: >60 kg CO₂e Einsparung/FTE/Tag
""",
    "Work-Life-Balance": """
Score 1: Deutlich schlechter, starke Grenzverwischung<br>
Score 2: Eher negativ, etwas mehr Stress<br>
Score 3: Ausgewogen oder leicht besser (typisch)<br>
Score 4: Deutlich besser, gute Zeitgewinne<br>
Score 5: Sehr hoch, flexible Zeitgestaltung
""",
    "Team-/Führungskultur": """
Score 1: Keine Remote-Erfahrung, Micromanagement<br>
Score 2: Erste Erfahrung (<1 Jahr), skeptische Manager<br>
Score 3: 1–3 Jahre Erfahrung, Video-Meetings Standard<br>
Score 4: Reife Hybrid-Kultur (>3 Jahre), asynchrone Arbeit<br>
Score 5: Remote-First Best Practice (GitLab-Style)
""",
    "Mitarbeiterakzeptanz": """
Score 1: <10% nutzen Homeoffice<br>
Score 2: 11–20% nutzen Homeoffice<br>
Score 3: 21–45% nutzen Homeoffice (DE-Durchschnitt)<br>
Score 4: 46–75% nutzen Homeoffice<br>
Score 5: >75% nutzen Homeoffice
""",
    "Aufgaben-/Persönlichkeitsfit": """
Score 1: Stark team-/ortsgebunden, geringe Selbstdisziplin<br>
Score 2: Teilweise ortsabhängig, begrenzte Selbstorganisation<br>
Score 3: Mischprofil, durchschnittlich organisiert<br>
Score 4: Autonome Aufgaben, gute Struktur<br>
Score 5: Wissensorientiert, hohe Gewissenhaftigkeit
""",
    "Produktivitätseffekte": """
Score 1: Deutlicher Rückgang (<–10%)<br>
Score 2: Leichter Rückgang (–10% bis 0%)<br>
Score 3: 0–10% (DE-Durchschnitt, neutral)<br>
Score 4: +10–20% Produktivität<br>
Score 5: >+20% Produktivität
""",
    "Präsenznotwendigkeit": """
Score 1: >70% Face-to-Face oder physische Aufgaben<br>
Score 2: 50–70% Präsenz nötig<br>
Score 3: 30–50% Präsenz nötig (typisch)<br>
Score 4: 10–30% Präsenz nötig<br>
Score 5: <10% Präsenz nötig
""",
    "IT-Infrastruktur": """
Score 1: Kein VPN, instabiles Internet, kaum Tools<br>
Score 2: Basis-VPN, E-Mail & File-Sharing<br>
Score 3: Stabiles VPN, MS Teams, gutes Internet<br>
Score 4: Enterprise VPN, Cloud-Tools, gute Security<br>
Score 5: Zero-Trust, Enterprise Security, Global Load-Balancing
"""
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
    st.markdown(f"**Frage:** {fragen[kriterium]}")

    col1, col2 = st.columns([1, 3])
    with col1:
        # Label entfernen → nur Slider ohne erneute Kriteriumsüberschrift
        score = st.slider(
            label=" ", 
            min_value=1, 
            max_value=5, 
            value=3, 
            key=f"{kriterium}_score"
        )
    with col2:
        st.markdown(beschreibungen[kriterium], unsafe_allow_html=True)

    scores[kriterium] = score
    gesamtscore += score * gewicht
    st.markdown("---")

# Ergebnisse
st.header("**Ihr Ergebnis**")
col1, col2, col3 = st.columns(3)
col1.metric("Gesamtscore", f"{gesamtscore:.2f}/5.0")
col2.metric("Policy-Empfehlung", get_empfehlung(gesamtscore))

# Spezifische Warnungen
it_score = scores.get("IT-Infrastruktur")
praesenz_score = scores.get("Präsenznotwendigkeit")

if it_score is not None and it_score < 3:
    st.warning(
        f"⚠️ Da Sie beim Kriterium **IT-Infrastruktur** nur einen Score von {it_score} ausgewählt haben, "
        "ist die empfohlene Anzahl an Homeoffice-Tagen nur dann sinnvoll, wenn die technische "
        "Infrastruktur ausreichend ausgebaut wird."
    )

if praesenz_score is not None and praesenz_score < 3:
    st.warning(
        f"⚠️ Da Sie beim Kriterium **Präsenznotwendigkeit** nur einen Score von {praesenz_score} ausgewählt haben, "
        "sollten Sie prüfen, ob Präsenzanforderungen reduziert oder digitalisiert werden können."
    )

# Handlungsempfehlungen
st.subheader("Handlungsempfehlungen")

empfehlungen = {
    "Büroflächenreduktion": {
        "problem": "Kaum Hotdesking, Präsenzstruktur stark ausgeprägt.",
        "maßnahmen": [
            "Buchungssystem oder einfache Desksharing-Regeln einführen.",
            "Meetingräume flexibilisieren → Fokusräume schaffen."
        ]
    },
    "CO₂-Einsparung": {
        "problem": "Geringe Nachhaltigkeitseffekte.",
        "maßnahmen": [
            "JobRad, ÖPNV-Zuschuss oder Ladeinfrastruktur anbieten.",
            "Gebäudebetrieb an Belegung koppeln."
        ]
    },
    "Mitarbeiterakzeptanz": {
        "problem": "Geringe Nutzung oder Skepsis gegenüber Homeoffice.",
        "maßnahmen": [
            "Ursachenanalyse (Umfrage/Workshop).",
            "Sanftes Hybridmodell einführen.",
            "Best Practices aus Teams teilen."
        ]
    },
    "Team-/Führungskultur": {
        "problem": "Skepsis, wenig Remote-Kompetenz.",
        "maßnahmen": [
            "Training für Führen auf Distanz.",
            "Output statt Präsenz messen.",
            "Team-Working-Agreements definieren."
        ]
    },
    "Aufgaben-/Persönlichkeitsfit": {
        "problem": "Aufgaben wenig remote-tauglich.",
        "maßnahmen": [
            "Schulungen in Selbstorganisation.",
            "Tägliche Struktur (Check-in, Tagesziele)."
        ]
    },
    "Produktivitätseffekte": {
        "problem": "Homeoffice senkt Produktivität.",
        "maßnahmen": [
            "Ursachenanalyse (Ablenkung, Technik, Kommunikation).",
            "Fokusphasen wie 'No-Meeting-Wednesday'."
        ]
    },
    "Work-Life-Balance": {
        "problem": "Homeoffice wirkt negativ.",
        "maßnahmen": [
            "Regeln zur Erreichbarkeit.",
            "Schulung zu Pausenmanagement.",
            "Digitale Pausenreminder."
        ]
    }
}

kritische_kategorien_ausgeschlossen = {"IT-Infrastruktur", "Präsenznotwendigkeit", "Pendelaufwand"}

kritische_kriterien = [
    k for k, s in scores.items()
    if s <= 2 and k not in kritische_kategorien_ausgeschlossen
]

if len(kritische_kriterien) == 0:
    st.success("Keine kritischen Bereiche - Für alle relevanten Kriterien liegen solide oder gute Werte vor.")
else:
    for kriterium in kritische_kriterien:
        st.markdown(f"### {kriterium}")
        info = empfehlungen.get(kriterium, None)
        if info:
            st.markdown(f"**Problem:** {info['problem']}")
            for punkt in info["maßnahmen"]:
                st.markdown(f"- {punkt}")
        else:
            st.markdown("_Aktuell keine spezifischen Empfehlungen hinterlegt._")
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