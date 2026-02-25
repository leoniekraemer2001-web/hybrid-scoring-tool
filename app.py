import streamlit as st
import pandas as pd
import json
from datetime import datetime
from supabase import create_client

# --- Streamlit: Seite zuerst konfigurieren (Best Practice ganz am Anfang) ---
st.set_page_config(page_title="Hybrid-Scoring-Tool", layout="wide", initial_sidebar_state="collapsed")

# --- Supabase initialisieren ---
supabase = create_client(
    st.secrets["supabase"]["url"],
    st.secrets["supabase"]["anon_key"]
)

# -------------------------------------------------------
# CSS (responsive & theme-aware)
# -------------------------------------------------------
st.markdown(
    """
    <style>
    /* Theme-aware Farben */
    :root {
      --hs-primary: var(--primary-color);
      --hs-text: var(--text-color);
      --hs-bg: var(--background-color);
      --hs-bg-2: var(--secondary-background-color);
    }

    h1 { font-size: 2.1rem; margin-bottom: 0.3rem; }
    .subtitle { font-size: 1.05rem; color: var(--hs-text); opacity: .9; }

    /* Instruction box – theme aware + dezente Karte */
    .instruction-box {
      background-color: var(--hs-bg-2);
      color: var(--hs-text);
      padding: 16px 18px;
      border-radius: 12px;
      border-left: 6px solid var(--hs-primary);
      margin: 14px 0 22px 0;
    }

    /* Abstände & Einrückungen */
    .intro-step { margin-bottom: .7rem; line-height: 1.55; }
    .intro-sub  { margin-left: 1.25rem; margin-top: .15rem; margin-bottom: .45rem; opacity: .95; }
    .intro-section-title { font-weight: 600; margin: .3rem 0 .6rem 0; font-size: 1.05rem; }

    /* Mobile Tweaks */
    @media (max-width: 680px) {
      h1 { font-size: 1.6rem; }
      .subtitle { font-size: .95rem; }
      .instruction-box { padding: 12px 12px; border-left-width: 4px; }
      .intro-step { margin-bottom: .55rem; line-height: 1.5; font-size: .98rem; }
      .intro-sub  { margin-left: .9rem; margin-bottom: .35rem; font-size: .95rem; }
      .intro-section-title { font-size: 1rem; margin-bottom: .5rem; }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------------
# Kopfbereich
# -------------------------------------------------------
st.markdown("<h1>Hybrid-Scoring-Tool</h1>", unsafe_allow_html=True)
st.markdown(
    "<div class='subtitle'>Objektive Analyse Ihrer Rahmenbedingungen – datenbasiert und in wenigen Schritten zur passenden Homeoffice-Policy</div>",
    unsafe_allow_html=True
)

with st.expander("Kurzanleitung", expanded=True):
    st.markdown(
        """
        <div class='instruction-box'>
          <div class='intro-step'>1️⃣ <b>Start im linken Menü:</b> Wählen Sie, ob Sie die <b>Standardgewichtung</b> nutzen oder eine <b>eigene Gewichtung</b> erstellen möchten.</div>
          <div class='intro-sub'>➜ In der Gewichtungsübersicht weiter unten sehen Sie alle <b>Standardwerte</b> im Vergleich zu Ihrer <b>neuen Gewichtung</b>.</div>
          <div class='intro-sub'>➜ Wenn Sie die Standardgewichte übernehmen möchten, können Sie Schritt 2 überspringen und direkt mit der Bewertung fortfahren.</div>

          <div class='intro-step'>2️⃣ <b>Eigene Gewichtung (optional):</b> Wählen Sie im Menü links die Option "Eigene Gewichtung vergeben"</b>.</div>
          <div class='intro-sub'>➜ Vergeben Sie für jedes Kriterium eine <b>Wichtigkeit von 0–100</div>
          <div class='intro-sub'>➜ Wir freuen uns, wenn Sie Ihre Gewichtung mit uns teilen und so zur Weiterentwicklung unseres Tools beitragen.</div>

          <div class='intro-step'>3️⃣ <b>Bewertung:</b> Bewerten Sie jedes Kriterium mit einem <b>Score von 1–5</b>.</div>
          <div class='intro-sub'>➜ Die Frage und die Skalenbeschreibung helfen Ihnen bei der Einordnung.</div>

          <div class='intro-step'>4️⃣ <b>Ergebnis:</b> Sie erhalten einen <b>Gesamtscore</b> und eine <b>konkrete Homeoffice-Empfehlung</b>.</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# -------------------------------------------------------
# Startoptionen
# -------------------------------------------------------
st.sidebar.header("Startoption wählen")
startmodus = st.sidebar.radio(
    "Wie möchten Sie beginnen?",
    ["Standardgewichtung verwenden", "Eigene Gewichtung vergeben"]
)

# -------------------------------------------------------
# Standardgewichte
# -------------------------------------------------------
standardgewichte = {
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
kriterien = list(standardgewichte.keys())

# -------------------------------------------------------
# Erklärungen (Tooltips)
# -------------------------------------------------------
kriterien_beschreibungen = {
    "CO₂-Einsparung": "Reduktion von Treibhausgasen durch weniger Pendelwege und geringeren Büroenergieverbrauch.",
    "Pendelaufwand": "Zeitliche, finanzielle und organisatorische Belastung durch den täglichen Arbeitsweg.",
    "Büroflächenreduktion": "Potenzial zur Senkung von Miet-, Energie- und Flächenkosten.",
    "Präsenznotwendigkeit": "Grad der Tätigkeiten, die zwingend physische Anwesenheit erfordern.",
    "Team-/Führungskultur": "Qualität der Zusammenarbeit, Vertrauen, Kommunikation.",
    "IT-Infrastruktur": "Qualität von Hardware, Software, VPN, Netzwerk und Support.",
    "Mitarbeiterakzeptanz": "Bereitschaft und Einstellung der Mitarbeitenden zu Homeoffice.",
    "Produktivitätseffekte": "Veränderung der Leistungsfähigkeit im Homeoffice.",
    "Work-Life-Balance": "Einfluss auf die Vereinbarkeit von Arbeit und Privatleben.",
    "Aufgaben-/Persönlichkeitsfit": "Eignung von Aufgaben & individuellen Arbeitsstilen für Homeoffice."
}

# -------------------------------------------------------
# Gewichtung berechnen
# -------------------------------------------------------
if startmodus == "Eigene Gewichtung vergeben":

    st.subheader("Eigene Gewichtung festlegen")
    st.write("Passen Sie die Bedeutung der einzelnen Kriterien an Ihre individuelle Situation an.")
    st.caption("➜ Je höher der Regler steht, desto stärker fließt das Kriterium später in die Empfehlung ein. Die Summe wird automatisch auf 100% normiert.")

    slider_raw = {}
    for k in kriterien:
        slider_raw[k] = st.slider(
            f"{k} – Wichtigkeit",
            min_value=0,
            max_value=100,
            value=int(standardgewichte[k] * 100),
            step=1,
            help=kriterien_beschreibungen[k]
        )

    if sum(slider_raw.values()) == 0:
        gewichte = {k: 1 / len(kriterien) for k in kriterien}
    else:
        total = sum(slider_raw.values())
        gewichte = {k: slider_raw[k] / total for k in kriterien}

else:
    gewichte = standardgewichte.copy()

# -------------------------------------------------------
# Speicher-Funktion
# -------------------------------------------------------
def save_weights_to_supabase(weights, industry, position):
    payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "weights_json": json.dumps(weights),
        "industry": industry if industry != "keine Angabe" else None,
        "position": position if position != "keine Angabe" else None,
    }
    try:
        response = supabase.table("weights").insert(payload).execute()
        return response
    except Exception as e:
        return {"error": str(e)}

# -------------------------------------------------------
# Gewichtungsübersicht als Tabelle
# -------------------------------------------------------
st.subheader("Gewichtungsübersicht (Standard vs. Neu)")
gewicht_tabelle = pd.DataFrame({
    "Kriterium": kriterien,
    "Standardgewicht (%)": [standardgewichte[k] * 100 for k in kriterien],
    "Neue Gewichtung (%)": [gewichte[k] * 100 for k in kriterien]
})
gewicht_tabelle["Standardgewicht (%)"] = gewicht_tabelle["Standardgewicht (%)"].map(lambda x: f"{x:.1f}%")
gewicht_tabelle["Neue Gewichtung (%)"] = gewicht_tabelle["Neue Gewichtung (%)"].map(lambda x: f"{x:.1f}%")
st.dataframe(gewicht_tabelle, use_container_width=True)

# -------------------------------------------------------
# (NEU) Optionale Angaben & Speichern – nur bei "Eigene Gewichtung"
# -------------------------------------------------------
if startmodus == "Eigene Gewichtung vergeben":
    st.subheader("Weitere Angaben (anonym)")
    st.caption("➜ Wir freuen uns, wenn Sie die beiden Angaben ausfüllen und Ihre Gewichtung hier mit uns teilen.")
    industry = st.selectbox(
        "Branche",
        [
            "keine Angabe",
            "Produktion",
            "Dienstleistung",
            "Handel",
            "IT/Software",
            "Öffentlicher Sektor",
            "Sonstiges"
        ]
    )
    position = st.selectbox(
        "Position im Unternehmen",
        [
            "keine Angabe",
            "Führung / Management",
            "Kaufmännische / Administrative Rolle",
            "Operative Rolle",
            "Fachkraft",
            "Ausbildung / Studium"
        ]
    )

    st.subheader("Gewichtung anonym speichern und senden")
    st.caption("Mit Ihrer Rückmeldung helfen Sie uns, die Standardgewichtung fortlaufend zu kalibrieren. Vielen Dank!")
    if st.button("Gewichtung senden"):
        res = save_weights_to_supabase(gewichte, industry, position)
        if isinstance(res, dict) and "error" in res:
            st.error(f"Fehler beim Speichern: {res['error']}")
        else:
            st.success("Vielen Dank für Ihre Teilnahme. Ihre Gewichtung wurde erfolgreich gespeichert. Sie können nun unten mit Ihrer individuellen Einschätzung fortfahren.")

# -------------------------------------------------------
# Fragen
# -------------------------------------------------------
fragen = {
    "Pendelaufwand": "Wie weit pendelt Ihr Team durchschnittlich?",
    "Büroflächenreduktion": "Wie stark ist Ihr Bereich auf flexible Arbeitsplätze ausgerichtet?",
    "CO₂-Einsparung": "Wie groß ist die CO₂‑Reduktion durch Homeoffice?",
    "Work-Life-Balance": "Wie wirkt sich Homeoffice auf die Work-Life-Balance aus?",
    "Team-/Führungskultur": "Wie reif ist Ihr Team für hybride Zusammenarbeit?",
    "Mitarbeiterakzeptanz": "Wie viele nutzen Homeoffice regelmäßig?",
    "Aufgaben-/Persönlichkeitsfit": "Wie gut eignen sich Aufgaben für ortsunabhängiges Arbeiten?",
    "Produktivitätseffekte": "Wie hat sich die Produktivität verändert?",
    "Präsenznotwendigkeit": "Wie viele Aufgaben erfordern physische Präsenz?",
    "IT-Infrastruktur": "Wie stabil & leistungsfähig ist die IT?"
}

# -------------------------------------------------------
# Skalenbeschreibungen
# -------------------------------------------------------
beschreibungen = {
    "Pendelaufwand": """
Score 1: <5 km<br>
Score 2: 5–12 km<br>
Score 3: 12–22 km<br>
Score 4: 22–35 km<br>
Score 5: >35 km
""",
    "Büroflächenreduktion": """
Score 1: Einzelbüros<br>
Score 2: <30% Hotdesking<br>
Score 3: 30–50% Hotdesking<br>
Score 4: 50–70% Hotdesking<br>
Score 5: >70% Hotdesking
""",
    "CO₂-Einsparung": """
Score 1: <10 kg CO₂e<br>
Score 2: 10–25 kg<br>
Score 3: 25–40 kg<br>
Score 4: 40–60 kg<br>
Score 5: >60 kg
""",
    "Work-Life-Balance": """
Score 1: Deutlich schlechter<br>
Score 2: Etwas schlechter<br>
Score 3: Neutral<br>
Score 4: Besser<br>
Score 5: Sehr gut
""",
    "Team-/Führungskultur": """
Score 1: Kaum Remote-Erfahrung<br>
Score 2: Erste Schritte<br>
Score 3: 1–3 Jahre Erfahrung<br>
Score 4: Reif<br>
Score 5: Best Practice
""",
    "Mitarbeiterakzeptanz": """
Score 1: <10% nutzen HO<br>
Score 2: 11–20%<br>
Score 3: 21–45%<br>
Score 4: 46–75%<br>
Score 5: >75%
""",
    "Aufgaben-/Persönlichkeitsfit": """
Score 1: Nicht geeignet<br>
Score 2: Kaum geeignet<br>
Score 3: Bedingt geeignet<br>
Score 4: Gut geeignet<br>
Score 5: Sehr gut geeignet
""",
    "Produktivitätseffekte": """
Score 1: -10%<br>
Score 2: -10–0%<br>
Score 3: 0–10%<br>
Score 4: +10–20%<br>
Score 5: >20%
""",
    "Präsenznotwendigkeit": """
Score 1: >70% Präsenz<br>
Score 2: 50–70%<br>
Score 3: 30–50%<br>
Score 4: 10–30%<br>
Score 5: <10%
""",
    "IT-Infrastruktur": """
Score 1: Unzuverlässig<br>
Score 2: Basisniveau<br>
Score 3: Stabil<br>
Score 4: Sehr gut<br>
Score 5: Exzellent
"""
}

# -------------------------------------------------------
# Bewertung
# -------------------------------------------------------
def get_empfehlung(score):
    if score < 1.4: return "0 Tage pro Woche"
    elif score < 2.5: return "1 Tag pro Woche"
    elif score < 3.5: return "2 Tage pro Woche"
    elif score < 4.5: return "3 Tage pro Woche"
    else: return "4–5 Tage pro Woche"

st.subheader("Bewertung")
st.caption("➜ Bewerten Sie sich anhand der Kriterien von 1 bis 5. Die Beschreibung hilft Ihnen bei der Einordnung.")

scores = {}
gesamtscore = 0.0
for kriterium, gewicht in gewichte.items():
    st.markdown(f"### {kriterium}")
    st.markdown(f"**Frage:** {fragen[kriterium]}")

    col1, col2 = st.columns([1, 3])
    with col1:
        score = st.slider(" ", 1, 5, 3, key=f"{kriterium}_score")
    with col2:
        st.markdown(beschreibungen[kriterium], unsafe_allow_html=True)

    scores[kriterium] = score
    gesamtscore += score * gewicht
    st.markdown("---")

# -------------------------------------------------------
# Ergebnis
# -------------------------------------------------------
st.subheader("Ihr Ergebnis")
st.caption("➜ Ihr Gesamtscore und die empfohlene Anzahl an Homeoffice-Tagen basieren auf Ihren Bewertungen und Gewichtungen.")

col1, col2 = st.columns(2)
col1.metric("Gesamtscore", f"{gesamtscore:.2f}/5.0")
col2.metric("Homeoffice-Empfehlung", get_empfehlung(gesamtscore))

# -------------------------------------------------------
# Detailanalyse – mit neuen Gewichten
# -------------------------------------------------------
st.subheader("Detail-Analyse")
df_data = [
    {
        "Kriterium": k,
        "Score": scores[k],
        "Gewicht (%)": f"{gewichte[k] * 100:.1f}%",
        "Teilwert": f"{scores[k] * gewichte[k]:.2f}"
    }
    for k in scores
]
st.dataframe(pd.DataFrame(df_data), use_container_width=True)

with st.expander("ℹ️ Mehr erfahren – So arbeitet das Tool"):
    st.markdown("""
    **Wie werden die Gewichte berechnet?**  
    Ihre 0–100-Eingaben werden automatisch so umgerechnet, dass die Summe exakt 100 % ergibt (Normalisierung).

    **Wie entsteht die Empfehlung?**  
    Für jedes Kriterium wird der Score (1–5) mit dem Gewicht multipliziert. Die Summe aller Teilwerte ergibt den Gesamtscore, der auf eine Empfehlung (Tage/Woche) gemappt wird.

    **Kann ich später noch etwas ändern?**  
    Ja. Gewichtungen und Bewertungen können jederzeit angepasst werden – das Ergebnis aktualisiert sich automatisch.
    """)

st.markdown("---")
st.markdown("*DHBW Lörrach | P.Gizewski, L. Krämer, L. Müller | © 2026*")