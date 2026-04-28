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

    st.info(
        "Im ersten Schritt prüfen wir, ob Homeoffice grundsätzlich sinnvoll umsetzbar ist. "
        "Bitte beantworten Sie die folgenden beiden Fragen aus Sicht Ihres Unternehmens."
    )

    col1, col2 = st.columns(2)

    # -----------------------------
    # Präsenznotwendigkeit
    # -----------------------------
    with col1:
        praesenz = st.slider(
            "Präsenznotwendigkeit der Tätigkeiten",
            1, 5, 3
        )

        st.markdown(
            """
            <b>Score 1:</b> &gt;70% Face-to-Face oder physische Aufgaben<br>
            <b>Score 2:</b> 50–70% Präsenz erforderlich<br>
            <b>Score 3:</b> 30–50% Präsenz erforderlich (typisch)<br>
            <b>Score 4:</b> 10–30% Präsenz erforderlich<br>
            <b>Score 5:</b> &lt;10 Präsenz erforderlich
            """,
            unsafe_allow_html=True
        )

    # -----------------------------
    # IT-Infrastruktur
    # -----------------------------
    with col2:
        it = st.slider(
            "IT-Ausstattung & digitale Arbeitsfähigkeit",
            1, 5, 3
        )

        st.markdown(
            """
            <b>Score 1:</b> Kein VPN, schlechtes Internet, keine Tools<br>
            <b>Score 2:</b> Basis-VPN, E-Mail + File-Sharing<br>
            <b>Score 3:</b> Gutes VPN, MS Teams, stabiles Internet<br>
            <b>Score 4:</b> Enterprise-VPN, Cloud-Tools, Cybersecurity<br>
            <b>Score 5:</b> Weltklasse-IT (Zero-Trust, globale Skalierung)
            """,
            unsafe_allow_html=True
        )

    # -----------------------------
    # Prüfung & Weiter
    # -----------------------------
    if st.button("✅ Voraussetzungen prüfen"):
        if praesenz >= 3 and it >= 3:
            st.session_state.step = 2
            st.rerun()
        else:
            st.error(
                "Homeoffice ist unter den angegebenen Bedingungen aktuell nur eingeschränkt sinnvoll. "
                "Bitte prüfen Sie zunächst organisatorische oder technische Verbesserungen."
            )

# =======================================================
# SCHRITT 2 – GEWICHTUNG
# =======================================================
elif st.session_state.step == 2:

    st.header("Schritt 2: Gewichtung der Kriterien")

    st.markdown(
        """
        In diesem Schritt legen Sie fest, **wie wichtig die einzelnen Kriterien**
        für Ihre Homeoffice‑Entscheidung sind.

        Die Gewichtung dient dazu, persönliche oder organisationale **Prioritäten**
        abzubilden – unabhängig davon, wie gut oder schlecht die Rahmenbedingungen aktuell ausgeprägt sind.

        **Hinweise zur Gewichtung:**
        - 1 = geringe Bedeutung für die Entscheidung
        - 10 = sehr hohe Bedeutung
        - Die Werte werden automatisch auf **100 % normiert**
        
        Wenn für Sie alle Kriterien gleich relevant sind, können Sie die voreingestellten Werte
        unverändert lassen und direkt mit der Bewertung fortfahren.
        """
    )

    st.markdown("---")

    raw_weights = {}

    # ---------------------------------------------------
    # Wohlbefinden
    # ---------------------------------------------------
    st.markdown("### Wohlbefinden, Gesundheit & Work‑Life‑Balance")
    st.markdown(
        "Bewertet wird die Bedeutung von Homeoffice im Hinblick auf Gesundheit, "
        "Zufriedenheit sowie die Vereinbarkeit von Beruf und Privatleben."
    )
    raw_weights[kriterien[0]] = st.slider(
        "Wichtigkeit für die Entscheidung",
        1, 10, 5,
        key="gewicht_wellbeing"
    )

    st.markdown("---")

    # ---------------------------------------------------
    # Autonomie & Motivation
    # ---------------------------------------------------
    st.markdown("### Autonomie, Zeitsouveränität, Motivation & Engagement")
    st.markdown(
        "Dieses Kriterium beschreibt, wie relevant selbstbestimmtes Arbeiten, "
        "Eigenverantwortung, Motivation und Engagement für Ihre Organisation sind."
    )
    raw_weights[kriterien[1]] = st.slider(
        "Wichtigkeit für die Entscheidung",
        1, 10, 5,
        key="gewicht_autonomie"
    )

    st.markdown("---")

    # ---------------------------------------------------
    # Soziale Einbindung
    # ---------------------------------------------------
    st.markdown("### Soziale Einbindung & Teamkontakt")
    st.markdown(
        "Hier geht es um die Bedeutung von persönlichem Austausch, Teamgefühl "
        "und Zusammenarbeit – sowohl im Büro als auch virtuell."
    )
    raw_weights[kriterien[2]] = st.slider(
        "Wichtigkeit für die Entscheidung",
        1, 10, 5,
        key="gewicht_team"
    )

    st.markdown("---")

    # ---------------------------------------------------
    # Führung & Kultur
    # ---------------------------------------------------
    st.markdown("### Führungsstil & Kultur")
    st.markdown(
        "Beschreibt, wie wichtig Führung, Vertrauen und Unternehmenskultur "
        "für das Gelingen hybrider Arbeitsmodelle sind."
    )
    raw_weights[kriterien[3]] = st.slider(
        "Wichtigkeit für die Entscheidung",
        1, 10, 5,
        key="gewicht_fuehrung"
    )

    st.markdown("---")

    # ---------------------------------------------------
    # Pendelaufwand
    # ---------------------------------------------------
    st.markdown("### Pendeldauer & Mobilitätsaufwand")
    st.markdown(
        "Dieses Kriterium bildet ab, welche Rolle Arbeitswege, Pendelzeiten "
        "und daraus resultierende Entlastungseffekte für Ihre Entscheidung spielen."
    )
    raw_weights[kriterien[4]] = st.slider(
        "Wichtigkeit für die Entscheidung",
        1, 10, 5,
        key="gewicht_pendeln"
    )

    st.markdown("---")

    if st.button("➡️ Gewichtung bestätigen"):
        total = sum(raw_weights.values())
        st.session_state.gewichte = {
            k: raw_weights[k] / total for k in kriterien
        }
        st.session_state.step = 3
        st.rerun()

# =======================================================
# SCHRITT 3 – BEWERTUNG & ERGEBNIS
# =======================================================
elif st.session_state.step == 3:

    st.header("Schritt 3: Bewertung der Rahmenbedingungen")

    st.markdown(
        """
        Bitte bewerten Sie die folgenden Kriterien aus Sicht Ihres Unternehmens.

        Beurteilen Sie dabei den **aktuellen durchschnittlichen Zustand** im Unternehmen –
        nicht einzelne Ausnahmen oder persönliche Einzelmeinungen.

        Niedrige Werte stehen für Rahmenbedingungen, unter denen **weniger Homeoffice‑Tage sinnvoll**
        sind. Hohe Werte stehen für Rahmenbedingungen, unter denen **mehr Homeoffice‑Tage gut
        umsetzbar** sind.
        """
    )

    gesamtscore = 0.0
    scores = {}

    # ---------------------------------------------------
    # Wohlbefinden
    # ---------------------------------------------------
    st.markdown("### Wohlbefinden, Gesundheit & Work‑Life‑Balance")
    st.markdown(
        "**Frage:** Wie wirkt sich ein höherer Homeoffice‑Anteil auf Wohlbefinden, "
        "Work‑Life‑Balance und die Präferenzen der Mitarbeitenden in Ihrem Unternehmen aus?"
    )

    score = st.slider("Bewertung", 1, 5, 3, key="score_wellbeing")

    st.markdown(
        """
        - **Score 1 – mehr Homeoffice verschlechtert Wohlbefinden:**  
          Überwiegend höhere Belastung (z.B. Isolation, Entgrenzung); Präsenz wird bevorzugt.
        - **Score 2 – gemischte, eher negative Effekte:**  
          Einzelne profitieren, insgesamt überwiegen Nachteile.
        - **Score 3 – gemischtes Bild (typisch):**  
          Bessere Vereinbarkeit für viele, gleichzeitig Stressfaktoren; Präferenz 1–2 HO‑Tage.
        - **Score 4 – überwiegend positiv:**  
          Spürbare Verbesserung der Work‑Life‑Balance; Wunsch nach 2–3 HO‑Tagen.
        - **Score 5 – klar vorteilhaft:**  
          Stark positives Wohlbefinden; breite Präferenz für viel Homeoffice.
        """
    )

    scores["Wohlbefinden, Gesundheit & Work-Life-Balance"] = score
    gesamtscore += score * st.session_state.gewichte["Wohlbefinden, Gesundheit & Work-Life-Balance"]

    st.markdown("---")

    # ---------------------------------------------------
    # Autonomie & Motivation
    # ---------------------------------------------------
    st.markdown("### Autonomie, Zeitsouveränität, Motivation & Engagement")
    st.markdown(
        "**Frage:** Wie schätzen Sie Autonomie, Motivation und Engagement "
        "im Homeoffice im Vergleich zur Büroarbeit ein?"
    )

    score = st.slider("Bewertung", 1, 5, 3, key="score_autonomie")

    st.markdown(
        """
        - **Score 1 – deutlich weniger produktiv:** Leistung und Qualität sinken klar.
        - **Score 2 – eher weniger produktiv:** Einzelne Vorteile, insgesamt Nachteile.
        - **Score 3 – vergleichbare Produktivität:** Homeoffice und Büro etwa gleichwertig.
        - **Score 4 – eher produktiver:** Fokussierteres Arbeiten ohne große Abstimmungsverluste.
        - **Score 5 – deutlich produktiver:** Klare Vorteile gegenüber Büroarbeit.
        """
    )

    scores["Autonomie, Zeitsouveränität, Motivation & Engagement"] = score
    gesamtscore += score * st.session_state.gewichte["Autonomie, Zeitsouveränität, Motivation & Engagement"]

    st.markdown("---")

    # ---------------------------------------------------
    # Soziale Einbindung
    # ---------------------------------------------------
    st.markdown("### Soziale Einbindung & Teamkontakt")
    st.markdown(
        "**Frage:** Wie stark sind soziale Einbindung, persönlicher Austausch "
        "und Teamkontakt im Arbeitsalltag ausgeprägt?"
    )

    score = st.slider("Bewertung", 1, 5, 3, key="score_team")

    st.markdown(
        """
        - **Score 1 – deutlich unter Durchschnitt:** Kaum Austausch, Isolation.
        - **Score 2 – etwas unter Durchschnitt:** Eingeschränkter Teamkontakt.
        - **Score 3 – durchschnittlich:** Fachlicher Austausch vorhanden.
        - **Score 4 – überdurchschnittlich:** Guter Zusammenhalt, bewusster sozialer Austausch.
        - **Score 5 – deutlich über Durchschnitt:** Sehr starke Teamkultur.
        """
    )

    scores["Soziale Einbindung & Teamkontakt"] = score
    gesamtscore += score * st.session_state.gewichte["Soziale Einbindung & Teamkontakt"]

    st.markdown("---")

    # ---------------------------------------------------
    # Führung & Kultur
    # ---------------------------------------------------
    st.markdown("### Führungsstil & Kultur")
    st.markdown(
        "**Frage:** Wie gut sind Führung und Organisationskultur darauf ausgerichtet, "
        "Homeoffice und hybride Arbeit vertrauensbasiert und ergebnisorientiert zu steuern?"
    )

    score = st.slider("Bewertung", 1, 5, 3, key="score_fuehrung")

    st.markdown(
        """
        - **Score 1 – stark kontrollorientiert:** Präsenzdenken dominiert.
        - **Score 2 – begrenzte Reife:** Uneinheitliche Führung, fehlende Routinen.
        - **Score 3 – gemischte Reife:** Unterschiedliche Führungsstile.
        - **Score 4 – gut entwickelte Hybridführung:** Klare Regeln und Vertrauen.
        - **Score 5 – sehr hohe Reife:** Homeoffice selbstverständlich integriert.
        """
    )

    scores["Führungsstil & Kultur"] = score
    gesamtscore += score * st.session_state.gewichte["Führungsstil & Kultur"]

    st.markdown("---")

    # ---------------------------------------------------
    # Pendelaufwand
    # ---------------------------------------------------
    st.markdown("### Pendeldauer & Mobilitätsaufwand")
    st.markdown(
        "**Frage:** Wie hoch ist der durchschnittliche Pendelaufwand der Mitarbeitenden?"
    )

    score = st.slider("Bewertung", 1, 5, 3, key="score_pendeln")

    st.markdown(
        """
        - **Score 1:** &lt; 5km Ø Pendelstrecke
        - **Score 2:** 5–12km
        - **Score 3:** 12–22km
        - **Score 4:** 22–35km
        - **Score 5:** &gt; 35km
        """
    )

    scores["Pendeldauer & Mobilitätsaufwand"] = score
    gesamtscore += score * st.session_state.gewichte["Pendeldauer & Mobilitätsaufwand"]

    # -------------------------------------------------------
    # Ergebnis
    # -------------------------------------------------------
    def get_empfehlung(score: float) -> str:
        if score < 1.8:
            return "0 Tage Homeoffice / Woche"
        elif score < 2.6:
            return "1 Tag Homeoffice / Woche"
        elif score < 3.4:
            return "2 Tage Homeoffice / Woche"
        elif score < 4.2:
            return "3 Tage Homeoffice / Woche"
        else:
            return "4–5 Tage Homeoffice / Woche"

    st.subheader("Ihr Ergebnis")

    col1, col2 = st.columns(2)
    col1.metric("Gesamtscore", f"{gesamtscore:.2f} / 5.0")
    col2.metric("Homeoffice‑Empfehlung", get_empfehlung(gesamtscore))

    # -------------------------------------------------------
    # Handlungsempfehlungen
    # -------------------------------------------------------
    st.subheader("Handlungsempfehlungen")

    empfehlungen = {
        "Wohlbefinden, Gesundheit & Work-Life-Balance": {
          "problem": "Homeoffice wirkt sich aktuell eher negativ auf Wohlbefinden und Balance aus.",
         "maßnahmen": [
             "Klare Regeln zur Erreichbarkeit definieren.",
             "Führungskräfte zu gesundem Hybrid‑Arbeiten sensibilisieren.",
              "Pausen‑ und Belastungsmanagement fördern."
        ]
      },
      "Autonomie, Zeitsouveränität, Motivation & Engagement": {
          "problem": "Motivation und Produktivität profitieren aktuell kaum vom Homeoffice.",
          "maßnahmen": [
                "Ziel‑ und ergebnisorientierte Arbeitsweisen stärken.",
             "Eigenverantwortung systematisch fördern.",
              "Arbeitsprozesse und Erwartungen klarer kommunizieren."
         ]
     },
       "Soziale Einbindung & Teamkontakt": {
         "problem": "Soziale Einbindung und Teamkontakt sind unzureichend ausgeprägt.",
          "maßnahmen": [
              "Regelmäßige Team‑Touchpoints etablieren.",
              "Hybride Teamrituale und Austauschformate einführen.",
              "Bewusste Anwesenheitstage für Zusammenarbeit definieren."
         ]
     },
     "Führungsstil & Kultur": {
         "problem": "Führung und Kultur sind nur bedingt auf hybride Arbeit ausgerichtet.",
            "maßnahmen": [
              "Führungskräfte in ergebnisorientierter Führung schulen.",
             "Vertrauensbasierte Zusammenarbeit stärken.",
              "Klare Regeln für hybride Arbeit festlegen."
            ]
      },
      "Pendeldauer & Mobilitätsaufwand": {
         "problem": "hoher Pendelaufwand belastet Mitarbeitende zeitlich, finanziell und gesundheitlich.",
            "maßnahmen": [
                "Einführung oder Ausbau eines Shuttle‑Services für Hauptpendelstrecken oder Standorte.",
                "Bereitstellung von Jobtickets (ÖPNV‑Zuschuss) zur Reduktion von Kosten und Stress.",
                "Förderung nachhaltiger Mobilität durch JobBike‑ oder Fahrrad‑Leasing‑Modelle.",
                "Unterstützung von Fahrgemeinschaften (z. B. über interne Plattformen oder Anreizsysteme)."
             ]
        }
      }



    kritische_kriterien = []

    for k, s in scores.items():
        if k != "Pendeldauer & Mobilitätsaufwand" and s <= 2:
            kritische_kriterien.append(k)

        if k == "Pendeldauer & Mobilitätsaufwand" and s >= 4:
            kritische_kriterien.append(k)

    # ✅ AUSGABE NUR EINMAL
    if not kritische_kriterien:
        st.success(
            "✅ Keine kritischen Handlungsfelder identifiziert. "
            "Die wesentlichen Rahmenbedingungen unterstützen hybrides Arbeiten."
        )
    else:
        for kriterium in kritische_kriterien:
            info = empfehlungen[kriterium]
            st.markdown(f"### {kriterium}")
            st.markdown(f"**Problem:** {info['problem']}")
            for m in info["maßnahmen"]:
                st.markdown(f"- {m}")
            st.markdown("---")





    # -------------------------------------------------------
    # Detailanalyse
    # -------------------------------------------------------
    st.subheader("Detail‑Analyse")


    df_data = [
        {
            "Kriterium": k,
            "Score": scores[k],
            "Gewicht (%)": f"{st.session_state.gewichte[k] * 100:.1f} %",
            "Teilwert": f"{scores[k] * st.session_state.gewichte[k]:.2f}"
        }
        for k in scores
    ]

    st.dataframe(pd.DataFrame(df_data), use_container_width=True)

    # -------------------------------------------------------
    # Methodik‑Hinweis
    # -------------------------------------------------------
    with st.expander("ℹ️ Mehr erfahren – So arbeitet das Tool"):
        st.markdown(
            """
            **Wie entsteht der Gesamtscore?**  
            Für jedes Kriterium wird die Bewertung (1–5) mit der individuellen Gewichtung multipliziert.  
            Die Summe aller Teilwerte ergibt den Gesamtscore (0–5).

            **Wie wird die Empfehlung abgeleitet?**  
            Der Gesamtscore wird auf eine empfohlene Anzahl an Homeoffice‑Tagen pro Woche gemappt.
            """
        )

st.markdown("---")
st.markdown("*DHBW Lörrach | P. Gizewski, L. Krämer, L. Müller | © 2026*")
