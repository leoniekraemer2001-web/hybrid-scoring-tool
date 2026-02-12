import streamlit as st
import pandas as pd

st.set_page_config(page_title="Hybrid-Scoring-Tool", layout="wide")

st.title("🏢 **Hybrid-Scoring-Tool**")
st.markdown("**Evidenzbasierte Homeoffice-Policy in 2 Minuten** – NWA-Methodik")

# Gewichte und Reihenfolge (unverändert)
gewichte = {
    "Pendelaufwand": 0.17,
    "Büroflächenreduktion": 0.12,
    "CO₂-Einsparung": 0.11,
    "Work-Life-Balance": 0.13,
    "Team-/Führungskultur": 0.11,
    "Mitarbeiterakzeptanz": 0.08,
    "Aufgaben-/Persönlichkeitsfit": 0.03,
    "Produktivitätseffekte": 0.12,
    "Präsenznotwendigkeit": 0.08,
    "IT-Infrastruktur": 0.04
}

# Self-Assessment Skalen
beschreibungen = {
    "Pendelaufwand": """Score 1: <5 km Ø Pendelstrecke
Score 2: 5-12 km Ø
Score 3: 12-22 km Ø
Score 4: 22-35 km Ø
Score 5: >35 km Ø""",
    
    "Büroflächenreduktion": """Score 1: Einzelbüros, 100% Auslastung
Score 2: Grundlegende Hybrid-Struktur (<30% Hotdesking)
Score 3: Moderate Adaptivität (30-50% Hotdesking)
Score 4: Hohe Adaptivität (50-70% Hotdesking, Activity-Based)
Score 5: Vollständig adaptiv (>70% Hotdesking, Desk-Sharing)""",
    
    "CO₂-Einsparung": """Score 1: <10 kg CO₂e Einsparung/FTE/Tag
Score 2: 10-25 kg CO₂e Einsparung
Score 3: 25-40 kg CO₂e Einsparung (DE-Durchschnitt)
Score 4: 40-60 kg CO₂e Einsparung
Score 5: >60 kg CO₂e Einsparung""",
    
    "Work-Life-Balance": """Score 1: Deutlich schlechter, starke Grenzverwischung
Score 2: Eher negativ, etwas mehr Stress
Score 3: Ausgewogen oder leicht besser als Büro (typisch)
Score 4: Deutlich besser, gute Zeitgewinne
Score 5: Sehr hoch, flexible Zeitgestaltung""",
    
    "Team-/Führungskultur": """Score 1: Keine Remote-Erfahrung, Micromanagement
Score 2: Erste Erfahrung (<1 Jahr), skeptische Manager
Score 3: 1-3 Jahre Erfahrung, Video-Meetings Standard
Score 4: Reife Hybrid-Kultur (>3 Jahre), asynchrone Arbeit
Score 5: Weltklasse Remote-First (GitLab-Style)""",
    
    "Mitarbeiterakzeptanz": """Score 1: <10% Mitarbeiter nutzen HO
Score 2: 11-20% nutzen HO
Score 3: 21-45% nutzen HO (DE-Durchschnitt)
Score 4: 46-75% nutzen HO
Score 5: >75% nutzen HO""",
    
    "Aufgaben-/Persönlichkeitsfit": """Score 1: Stark team-/ortsgetrieben, niedrige Selbstdisziplin
Score 2: Teilweise ortsabhängig, begrenzte Selbstorganisation
Score 3: Mischprofil, durchschnittlich organisiert (typisch)
Score 4: Autonome Aufgaben, gut strukturiert
Score 5: Wissensorientiert, hohe Gewissenhaftigkeit""",
    
    "Produktivitätseffekte": """Score 1: Deutlicher Rückgang < -10%
Score 2: Leichter Rückgang -10% bis 0%
Score 3: 0-10% (DE-Durchschnitt, neutral)
Score 4: +10-20% Produktivität
Score 5: >+20% Produktivität""",
    
    "Präsenznotwendigkeit": """Score 1: >70% Face-to-Face oder physische Aufgaben
Score 2: 50-70% Präsenz erforderlich
Score 3: 30-50% Präsenz erforderlich (typisch)
Score 4: 10-30% Präsenz erforderlich
Score 5: <10% Präsenz erforderlich""",
    
    "IT-Infrastruktur": """Score 1: Kein VPN, schlechte Internet, keine Tools
Score 2: Basis-VPN, Email + File-Sharing
Score 3: Gutes VPN, MS Teams, stabiles Internet
Score 4: Enterprise VPN, Cloud-Tools, Cybersecurity
Score 5: Weltklasse IT (Zero-Trust, Global Load-Balancing)"""
}

# Mapping
def get_empfehlung(score):
    if score < 2.5: return "0-1 Tage\\n(Minimal)"
    elif score < 3.5: return "2 Tage\\n(Starter)"
    elif score < 4.2: return "3 Tage\\n(Ausgereift)"
    else: return "4-5 Tage\\n(Remote-First)"

# Sidebar
st.sidebar.header("⚙️ Einstellungen")
gewicht_anpassen = st.sidebar.checkbox("Gewichte ändern", False)
if gewicht_anpassen:
    for k in gewichte:
        gewichte[k] = st.sidebar.slider(k[:15], 0.0, 0.5, gewichte[k], 0.01)

# Scores: VERTIKAL untereinander (Slider + Skala nebeneinander)
st.header("📊 Ihre Einschätzung (Score 1-5)")
st.markdown("*Skala immer sichtbar neben Slider*")
scores = {}
gesamtscore = 0

for kriterium, gewicht in gewichte.items():
    st.markdown(f"### {kriterium} ({gewicht:.0%})")
    col1, col2 = st.columns([1, 3])
    with col1:
        score = st.slider(kriterium, 1, 5, 3, key=f"{kriterium}_score")
    with col2:
        st.markdown(f"{beschreibungen[kriterium]}")
    scores[kriterium] = score
    gesamtscore += score * gewicht
    st.markdown("---")  # Trennlinie untereinander

# Ergebnisse
st.header("🎯 **Ihr Ergebnis**")
col1, col2, col3 = st.columns(3)
col1.metric("Gesamtscore", f"{gesamtscore:.2f}/5.0")
col2.metric("Policy-Empfehlung", get_empfehlung(gesamtscore))
col3.metric("vs. DE-Durchschnitt", "3.0", f"{gesamtscore-3.0:+.1f}")

# Breakdown-Tabelle
st.subheader("📈 Detail-Analyse")
df_data = [{"Kriterium": k, "Score": scores[k], "Gewicht": f"{gewichte[k]:.0%}", "Teilwert": f"{scores[k]*gewichte[k]:.2f}"} for k in scores]
df = pd.DataFrame(df_data)
st.dataframe(df, use_container_width=True)

st.markdown("---")
st.markdown("*DHBW-Projekt | NWA-basiert | © 2026*")

