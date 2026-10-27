import streamlit as st
import json
import os
import random
import uuid
from datetime import datetime

DATA_FIL = "familie_data.json"

STANDARD_MIDDAGER = {
    "Taco": ["Kjøttdeig", "Tacokrydder", "Tortillalefser", "Rømme", "Ost", "Salsa", "Mais", "Agurk"],
    "Laks med grønnsaker og poteter": ["Laksefilet", "Poteter", "Gulrøtter", "Rømme", "Sitron"],
    "Spagetti bolognese": ["Spagetti", "Kjøttdeig", "Hakkede tomater", "Løk", "Hvitløk", "Parmesan"],
    "Hjemmelaget pizza": ["Pizzadeig", "Pizzasaus", "Ost", "Skinke", "Champignon"],
    "Kyllingwok": ["Kyllingfilet", "Wokgrønnsaker", "Woksaus", "Ris eller nudler"],
    "Fiskepinner med potetmos": ["Fiskepinner", "Poteter", "Erter", "Smør", "Melk"],
    "Kjøttkaker i brun saus": ["Kjøttkaker", "Brun saus", "Poteter", "Tyttebærsyltetøy", "Ertestuing"],
    "Pannekaker med bacon": ["Hvetemel", "Egg", "Melk", "Bacon", "Blåbærsyltetøy"],
    "Pølseform / Pølsegrateng": ["Kjøttpølser", "Makaroni", "Hvit saus", "Ost", "Brokkoli"]
}

KATEGORI_REGLER = {
    "🥦 Frukt & Grønt": [
        "potet", "gulrot", "løk", "hvitløk", "mais", "agurk", "tomat", "sitron", 
        "salat", "brokkoli", "eple", "banan", "paprika", "avokado", "erter", 
        "champignon", "sopp", "lime", "appelsin", "ingefær", "chili", "urter"
    ],
    "🥩 Kjøtt, Fisk & Fjærkre": [
        "kjøttdeig", "kylling", "laks", "fisk", "fiskepinner", "kjøttkake", 
        "skinke", "pølse", "bacon", "biff", "kotelett", "karbonadedeig", 
        "reker", "torsk", "sei", "and", "kalkun"
    ],
    "🧀 Meieri & Kjølevare": [
        "melk", "ost", "rømme", "smør", "fløte", "yoghurt", "egg", "kesam", 
        "parmesan", "margarin", "majones", "leverpostei", "kaviar", "cottage cheese"
    ],
    "🍞 Tørrvare, Krydder & Kolonial": [
        "tacokrydder", "tortilla", "lefse", "spagetti", "pasta", "makaroni", 
        "pizzadeig", "pizzasaus", "salsa", "woksaus", "brun saus", "hvit saus", 
        "saus", "ris", "nudler", "hvetemel", "mel", "sukker", "havregryn", 
        "syltetøy", "brød", "rundstykke", "knekkebrød", "olje", "krydder"
    ]
}

AVDELINGER = [
    "🥦 Frukt & Grønt",
    "🥩 Kjøtt, Fisk & Fjærkre",
    "🧀 Meieri & Kjølevare",
    "🍞 Tørrvare, Krydder & Kolonial",
    "📦 Annet / Diverse"
]

DAGER = ["Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag", "Lørdag", "Søndag"]
MAANEDER = [
    "januar", "februar", "mars", "april", "mai", "juni",
    "juli", "august", "september", "oktober", "november", "desember"
]
FELLES_VALG = "Felles (Mor & Far / Den som gjør det)"

def gjett_kategori(varenavn):
    tekst = varenavn.lower()
    for kat, stikkord_liste in KATEGORI_REGLER.items():
        for stikkord in stikkord_liste:
            if stikkord in tekst:
                return kat
    return "📦 Annet / Diverse"

def migrer_handleliste(gammel_liste):
    ny_liste = []
    for item in gammel_liste:
        if isinstance(item, str):
            ny_liste.append({
                "id": str(uuid.uuid4()),
                "navn": item,
                "kategori": gjett_kategori(item)
            })
        elif isinstance(item, dict):
            if "id" not in item:
                item["id"] = str(uuid.uuid4())
            if "kategori" not in item:
                item["kategori"] = gjett_kategori(item.get("navn", ""))
            ny_liste.append(item)
    return ny_liste

def last_data():
    if os.path.exists(DATA_FIL):
        try:
            with open(DATA_FIL, "r", encoding="utf-8") as f:
                d = json.load(f)
                if "pin" not in d:
                    d["pin"] = "1234"
                if "medlemmer" not in d:
                    d["medlemmer"] = ["Far", "Mor", "Barn 1", "Barn 2"]
                if "stjerne_brukere" not in d:
                    d["stjerne_brukere"] = ["Barn 1", "Barn 2", "Far", "Mor"]
                if "poeng" not in d:
                    d["poeng"] = {m: 0 for m in d["medlemmer"]}
                if "beskjeder" not in d:
                    d["beskjeder"] = [
                        {"id": str(uuid.uuid4()), "tekst": "Husk gymtøy i morgen! 🏃‍♂️", "fra": "Mor", "tid": "Kl. 08:00"}
                    ]
                if "belonninger" not in d:
                    d["belonninger"] = [
                        {"id": str(uuid.uuid4()), "tittel": "30 min ekstra skjermtid", "pris": 5},
                        {"id": str(uuid.uuid4()), "tittel": "Velge lørdagsgodt", "pris": 8},
                        {"id": str(uuid.uuid4()), "tittel": "Bestemme lørdagsfilm", "pris": 10}
                    ]
                if "oppskrifter" not in d:
                    d["oppskrifter"] = STANDARD_MIDDAGER
                if "middagsplan" not in d:
                    gamle_middager = d.get("middager", {})
                    d["middagsplan"] = {
                        dag: {"rett": gamle_middager.get(dag, ""), "kokk": "Ingen valgt", "onske": "Ingen"} 
                        for dag in DAGER
                    }
                for oppg in d.get("oppgaver", []):
                    if "id" not in oppg:
                        oppg["id"] = str(uuid.uuid4())
                    if "fullfort_av" not in oppg:
                        oppg["fullfort_av"] = None
                    if "gjentakende" not in oppg:
                        oppg["gjentakende"] = False
                d["handleliste"] = migrer_handleliste(d.get("handleliste", []))
                return d
        except Exception:
            pass

    return {
        "pin": "1234",
        "medlemmer": ["Far", "Mor", "Barn 1", "Barn 2"],
        "stjerne_brukere": ["Barn 1", "Barn 2", "Far", "Mor"],
        "poeng": {"Far": 0, "Mor": 0, "Barn 1": 0, "Barn 2": 0},
        "beskjeder": [
            {"id": str(uuid.uuid4()), "tekst": "Husk gymtøy i morgen! 🏃‍♂️", "fra": "Mor", "tid": "Kl. 08:00"}
        ],
        "belonninger": [
            {"id": str(uuid.uuid4()), "tittel": "30 min ekstra skjermtid", "pris": 5},
            {"id": str(uuid.uuid4()), "tittel": "Velge lørdagsgodt", "pris": 8},
            {"id": str(uuid.uuid4()), "tittel": "Bestemme lørdagsfilm", "pris": 10}
        ],
        "oppgaver": [
            {"id": str(uuid.uuid4()), "tekst": "Pusse tenner morgen & kveld", "hvem": "Barn 1", "ferdig": False, "stjerner": 1, "fullfort_av": None, "gjentakende": True},
            {"id": str(uuid.uuid4()), "tekst": "Pusse tenner morgen & kveld", "hvem": "Barn 2", "ferdig": False, "stjerner": 1, "fullfort_av": None, "gjentakende": True},
            {"id": str(uuid.uuid4()), "tekst": "Rydde av bordet etter middag", "hvem": FELLES_VALG, "ferdig": False, "stjerner": 1, "fullfort_av": None, "gjentakende": True},
        ],
        "oppskrifter": STANDARD_MIDDAGER,
        "middagsplan": {dag: {"rett": "", "kokk": "Ingen valgt", "onske": "Ingen"} for dag in DAGER},
        "handleliste": migrer_handleliste(["Melk", "Brød", "Smør"])
    }

def lagre_data(data):
    with open(DATA_FIL, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = last_data()

def legg_til_vare_i_data(varenavn, kategori=None):
    if not varenavn.strip():
        return False
    renset_navn = varenavn.strip()
    eksisterende = [v["navn"].lower() for v in data["handleliste"]]
    if renset_navn.lower() in eksisterende:
        return False
    
    valgt_kat = kategori if kategori and kategori in AVDELINGER else gjett_kategori(renset_navn)
    data["handleliste"].append({
        "id": str(uuid.uuid4()),
        "navn": renset_navn,
        "kategori": valgt_kat
    })
    return True

# Callbacks
def cb_sett_middag(dag, rett):
    data["middagsplan"][dag]["rett"] = rett
    lagre_data(data)
    st.session_state[f"rett_{dag}"] = rett

def cb_auto_planlegg(oppskriftsliste):
    if not oppskriftsliste:
        return
    if len(oppskriftsliste) >= 7:
        ukens_trekk = random.sample(oppskriftsliste, 7)
    else:
        ukens_trekk = [random.choice(oppskriftsliste) for _ in range(7)]
    for i, dag in enumerate(DAGER):
        ny_rett = ukens_trekk[i]
        data["middagsplan"][dag]["rett"] = ny_rett
        st.session_state[f"rett_{dag}"] = ny_rett
    lagre_data(data)

def cb_start_ny_uke():
    data["oppgaver"] = [
        o for o in data["oppgaver"] 
        if o.get("gjentakende", False) or not o["ferdig"]
    ]
    for o in data["oppgaver"]:
        o["ferdig"] = False
        o["fullfort_av"] = None
    for dag in DAGER:
        data["middagsplan"][dag] = {"rett": "", "kokk": "Ingen valgt", "onske": "Ingen"}
        st.session_state[f"rett_{dag}"] = ""
        st.session_state[f"onske_{dag}"] = "Ingen"
        st.session_state[f"kokk_{dag}"] = "Ingen valgt"
    lagre_data(data)

for dag in DAGER:
    if f"rett_{dag}" not in st.session_state:
        st.session_state[f"rett_{dag}"] = data["middagsplan"].get(dag, {}).get("rett", "")

if "foreldremodus" not in st.session_state:
    st.session_state["foreldremodus"] = False

st.set_page_config(page_title="Familiehub", page_icon="🏡", layout="wide")

# ----------------- SIDEPANEL: FORELDREKONTROLL -----------------
with st.sidebar:
    st.header("🔐 Foreldrekontroll")
    
    if st.session_state["foreldremodus"]:
        st.success("🔓 Foreldremodus er AKTIV")
        st.caption("Du kan nå legge til og slette oppgaver, belønninger og administrere familien.")
        if st.button("🔒 Lås (Barnemodus)", use_container_width=True):
            st.session_state["foreldremodus"] = False
            st.rerun()

        st.write("---")
        with st.expander("🔑 Endre PIN-kode"):
            ny_pin = st.text_input("Ny 4-sifret PIN:", type="password", max_chars=8)
            if st.button("Lagre ny PIN") and ny_pin.strip():
                data["pin"] = ny_pin.strip()
                lagre_data(data)
                st.toast("PIN-kode er oppdatert!")
    else:
        st.info("🔒 Barnemodus aktiv")
        st.caption("Oppretting og sletting av oppgaver er låst for barna.")
        tastet_pin = st.text_input("Tast PIN for mor/far:", type="password", placeholder="Standard: 1234")
        if st.button("Lås opp", use_container_width=True):
            if tastet_pin == data.get("pin", "1234"):
                st.session_state["foreldremodus"] = True
                st.rerun()
            else:
                st.error("Feil PIN-kode!")

# ----------------- DATO & KLOKKESLETT -----------------
naa = datetime.now()
dag_indeks = naa.weekday()
idag_navn = DAGER[dag_indeks]
dato_tekst = f"{idag_navn} {naa.day}. {MAANEDER[naa.month - 1]} {naa.year}"
klokke_tekst = naa.strftime("%H:%M")

topp_kol1, topp_kol2 = st.columns([0.65, 0.35])
with topp_kol1:
    st.title("🏡 Familiens Ukeplan & Hverdagshub")
    if st.session_state["foreldremodus"]:
        st.caption("🔓 **Foreldremodus aktiv:** Full tilgang til å opprette og slette.")
with topp_kol2:
    st.markdown(
        f"""
        <div style="text-align: right; padding-top: 10px;">
            <span style="font-size: 1.4rem; font-weight: 700; color: #1E3A8A;">📅 {dato_tekst}</span><br>
            <span style="font-size: 1.8rem; font-weight: 800; color: #D97706;">⏰ kl. {klokke_tekst}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

# ----------------- FAMILIETAVLE / PÅMINNELSER -----------------
with st.expander("📌 Familiens Oppslagstavle & Påminnelser", expanded=True):
    beskjeder = data.get("beskjeder", [])
    slett_beskjed_id = None
    
    if beskjeder:
        # Vis opptil 3 lapper i bredden
        antall_kolonner = min(3, len(beskjeder))
        kolonner_tavle = st.columns(antall_kolonner)
        
        for i, b in enumerate(beskjeder):
            col_idx = i % antall_kolonner
            with kolonner_tavle[col_idx]:
                st.markdown(
                    f"""
                    <div style="background-color: #FEF3C7; border-left: 5px solid #F59E0B; padding: 12px; border-radius: 8px; margin-bottom: 8px;">
                        <span style="font-size: 1.1rem; font-weight: 600; color: #92400E;">{b['tekst']}</span><br>
                        <span style="font-size: 0.85rem; color: #B45309;">— Hilsen {b.get('fra', 'Familien')} ({b.get('tid', '')})</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                if st.button("Ferdig / Fjern ✕", key=f"del_b_{b['id']}"):
                    slett_beskjed_id = b["id"]

        if slett_beskjed_id:
            data["beskjeder"] = [b for b in data["beskjeder"] if b["id"] != slett_beskjed_id]
            lagre_data(data)
            st.rerun()
    else:
        st.caption("Ingen aktive beskjeder akkurat nå. Skriv en lapp under hvis det er noe viktig!")

    # Skjema for å legge inn ny lapp
    st.write("")
    with st.form("form_ny_beskjed", clear_on_submit=True):
        c_tekst, c_fra, c_knapp = st.columns([0.65, 0.20, 0.15])
        ny_beskjed_tekst = c_tekst.text_input("Ny beskjed / påminnelse:", placeholder="f.eks. Husk fotballtrening kl. 17:30!")
        hvem_fra = c_fra.selectbox("Fra:", data.get("medlemmer", ["Mor", "Far"]), label_visibility="collapsed")
        post_knapp = c_knapp.form_submit_button("Heng opp 📌")

        if post_knapp and ny_beskjed_tekst.strip():
            tidspunkt = datetime.now().strftime("%d.%m kl. %H:%M")
            data["beskjeder"].append({
                "id": str(uuid.uuid4()),
                "tekst": ny_beskjed_tekst.strip(),
                "fra": hvem_fra,
                "tid": tidspunkt
            })
            lagre_data(data)
            st.toast("Ny beskjed er hengt opp på tavlen! 📌")
            st.rerun()

st.write("")

er_forelder = st.session_state["foreldremodus"]

fane_navn = [
    "⭐ Oppgaver & Rutiner", 
    "🎁 Belønningsbutikk", 
    "🍽️ Middagsplan & Oppskrifter", 
    "🛒 Handleliste"
]
if er_forelder:
    fane_navn.append("👨‍👩‍👧‍👦 Familiemedlemmer (Admin)")

faner = st.tabs(fane_navn)
fane_oppgaver = faner[0]
fane_butikk = faner[1]
fane_middag = faner[2]
fane_handleliste = faner[3]
fane_familie = faner[4] if er_forelder else None

# ----------------- FANE 1: OPPGAVER & STJERNER -----------------
with fane_oppgaver:
    oppgaver_oppdatert = False
    slett_id = None

    medlemmer = data.get("medlemmer", [])
    stjerne_brukere = data.get("stjerne_brukere", [])

    col_tittel, col_null_dag, col_null_uke = st.columns([0.5, 0.25, 0.25])
    with col_tittel:
        st.subheader("Oversikt per person")
    with col_null_dag:
        if st.button("☀️ Ny dag (Nullstill rutiner)"):
            for o in data["oppgaver"]:
                if o.get("gjentakende", False):
                    o["ferdig"] = False
                    o["fullfort_av"] = None
            lagre_data(data)
            st.toast("Daglige rutiner er nullstilt og klare for en ny dag! ☀️")
            st.rerun()
    with col_null_uke:
        if er_forelder:
            st.button("🗓️ Start ny uke", on_click=cb_start_ny_uke)
        else:
            st.caption("🔒 Start ny uke krever PIN")

    if medlemmer:
        kolonner = st.columns(len(medlemmer))

        for idx, person in enumerate(medlemmer):
            with kolonner[idx]:
                if person in stjerne_brukere:
                    antall = data["poeng"].get(person, 0)
                    st.metric(label=f"👤 {person}", value=f"{antall} ⭐")
                else:
                    st.subheader(f"👤 {person}")

                st.write("---")

                person_oppgaver = [o for o in data["oppgaver"] if o["hvem"] == person]
                if not person_oppgaver:
                    st.caption("Ingen oppgaver akkurat nå 🎉")

                for oppg in person_oppgaver:
                    oppg_id = oppg["id"]
                    merke = "🔄 " if oppg.get("gjentakende") else ""
                    tekst_visning = f"{merke}{oppg['tekst']}"
                    if oppg.get("stjerner", 0) > 0:
                        tekst_visning += f" *(+{oppg['stjerner']} ⭐)*"

                    if er_forelder:
                        c_chk, c_del = st.columns([0.8, 0.2])
                        er_ferdig = c_chk.checkbox(tekst_visning, value=oppg["ferdig"], key=f"chk_{oppg_id}")
                        if c_del.button("✕", key=f"del_{oppg_id}", help="Slett oppgave (kun foreldre)"):
                            slett_id = oppg_id
                    else:
                        er_ferdig = st.checkbox(tekst_visning, value=oppg["ferdig"], key=f"chk_{oppg_id}")

                    if er_ferdig != oppg["ferdig"]:
                        oppg["ferdig"] = er_ferdig
                        stjerner = oppg.get("stjerner", 0)
                        if er_ferdig:
                            if person in stjerne_brukere:
                                data["poeng"][person] = data["poeng"].get(person, 0) + stjerner
                                st.balloons()
                        else:
                            if person in stjerne_brukere:
                                data["poeng"][person] = max(0, data["poeng"].get(person, 0) - stjerner)
                        oppgaver_oppdatert = True

    # Fellesoppgaver
    felles_oppgaver = [o for o in data["oppgaver"] if o["hvem"] == FELLES_VALG]
    if felles_oppgaver:
        st.write("---")
        st.subheader("🤝 Fellesoppgaver (Førstemann til mølla)")
        
        for oppg in felles_oppgaver:
            oppg_id = oppg["id"]
            if er_forelder:
                c_felles_chk, c_felles_who, c_felles_del = st.columns([0.5, 0.35, 0.15])
            else:
                c_felles_chk, c_felles_who = st.columns([0.6, 0.4])

            merke = "🔄 " if oppg.get("gjentakende") else ""
            tekst_visning = f"{merke}{oppg['tekst']}"
            if oppg.get("stjerner", 0) > 0:
                tekst_visning += f" *(+{oppg['stjerner']} ⭐)*"
            if oppg["ferdig"] and oppg.get("fullfort_av"):
                tekst_visning += f" — *(Fullført av: {oppg['fullfort_av']})*"

            er_ferdig = c_felles_chk.checkbox(tekst_visning, value=oppg["ferdig"], key=f"felles_chk_{oppg_id}")

            if not oppg["ferdig"]:
                hvem_valg = c_felles_who.selectbox(
                    "Hvem gjør den?", medlemmer, key=f"felles_who_{oppg_id}", label_visibility="collapsed"
                )
            else:
                c_felles_who.write("")
                hvem_valg = oppg.get("fullfort_av", medlemmer[0] if medlemmer else "")

            if er_forelder:
                if c_felles_del.button("✕", key=f"felles_del_{oppg_id}", help="Slett"):
                    slett_id = oppg_id

            if er_ferdig != oppg["ferdig"]:
                oppg["ferdig"] = er_ferdig
                stjerner = oppg.get("stjerner", 0)
                if er_ferdig:
                    oppg["fullfort_av"] = hvem_valg
                    if hvem_valg in stjerne_brukere:
                        data["poeng"][hvem_valg] = data["poeng"].get(hvem_valg, 0) + stjerner
                        st.balloons()
                else:
                    gammel_mottaker = oppg.get("fullfort_av")
                    if gammel_mottaker in stjerne_brukere:
                        data["poeng"][gammel_mottaker] = max(0, data["poeng"].get(gammel_mottaker, 0) - stjerner)
                    oppg["fullfort_av"] = None
                oppgaver_oppdatert = True

    if slett_id:
        data["oppgaver"] = [o for o in data["oppgaver"] if o["id"] != slett_id]
        lagre_data(data)
        st.rerun()

    if oppgaver_oppdatert:
        lagre_data(data)
        st.rerun()

    st.write("---")
    if er_forelder:
        st.subheader("➕ Legg til oppgave(r)")
        with st.form("ny_oppgave_form", clear_on_submit=True):
            oppg_tekst = st.text_input("Hva skal gjøres? (f.eks. Pusse tenner, Rydde rommet, Gå ut med søppel)")
            valgalternativer = [FELLES_VALG] + medlemmer
            valgte_personer = st.multiselect(
                "Hvem skal ha oppgaven? (Velg én eller flere):",
                options=valgalternativer,
                default=[medlemmer[0]] if medlemmer else []
            )
            kol_b, kol_c = st.columns(2)
            stjerner = kol_b.number_input("Stjerner (belønning per person):", min_value=0, max_value=20, value=1)
            er_daglig = kol_c.checkbox("🔄 Daglig rutine (fornyes hver dag)", value=True)
            
            sendt = st.form_submit_button("Legg til oppgave")
            if sendt:
                if not oppg_tekst.strip():
                    st.warning("Vennligst skriv inn hva oppgaven går ut på.")
                elif not valgte_personer:
                    st.warning("Vennligst velg minst én person eller Felles.")
                else:
                    for person in valgte_personer:
                        data["oppgaver"].append({
                            "id": str(uuid.uuid4()),
                            "tekst": oppg_tekst.strip(),
                            "hvem": person,
                            "ferdig": False,
                            "stjerner": int(stjerner),
                            "fullfort_av": None,
                            "gjentakende": er_daglig
                        })
                    lagre_data(data)
                    st.success(f"Oppgave lagt til for: {', '.join(valgte_personer)}!")
                    st.rerun()
    else:
        st.info("🔒 **Legge til eller slette oppgaver?** Lås opp foreldrekontroll i sidepanelet til venstre med PIN.")

# ----------------- FANE 2: BELØNNINGSBUTIKK -----------------
with fane_butikk:
    st.header("🎁 Belønningsbutikk")
    st.caption("Her kan barna bruke sine oppsparte stjerner!")

    stjerne_brukere = data.get("stjerne_brukere", [])
    if stjerne_brukere:
        cols_b = st.columns(len(stjerne_brukere))
        for idx, person in enumerate(stjerne_brukere):
            antall = data["poeng"].get(person, 0)
            cols_b[idx].metric(label=f"Konto: {person}", value=f"{antall} ⭐")

    st.write("---")
    st.subheader("Tilgjengelige premier")

    slett_belonning_id = None
    for bel in data.get("belonninger", []):
        if er_forelder:
            col_t, col_p, col_kjop, col_del = st.columns([0.45, 0.15, 0.3, 0.1])
        else:
            col_t, col_p, col_kjop = st.columns([0.5, 0.2, 0.3])

        col_t.markdown(f"### {bel['tittel']}")
        col_p.metric("Pris", f"{bel['pris']} ⭐")

        with col_kjop:
            hvem_kjoper = st.selectbox("Kjøper:", stjerne_brukere, key=f"kjop_who_{bel['id']}", label_visibility="collapsed")
            har_rad = data["poeng"].get(hvem_kjoper, 0) >= bel["pris"]
            if st.button(f"Løs inn for {hvem_kjoper}", key=f"btn_kjop_{bel['id']}", disabled=not har_rad):
                data["poeng"][hvem_kjoper] -= bel["pris"]
                lagre_data(data)
                st.balloons()
                st.toast(f"🎉 Gratulerer {hvem_kjoper}! Du løste inn: {bel['tittel']}!")
                st.rerun()

        if er_forelder:
            if col_del.button("✕", key=f"del_bel_{bel['id']}", help="Slett belønning"):
                slett_belonning_id = bel["id"]

        st.write("---")

    if slett_belonning_id:
        data["belonninger"] = [b for b in data["belonninger"] if b["id"] != slett_belonning_id]
        lagre_data(data)
        st.rerun()

    if er_forelder:
        st.subheader("➕ Legg til ny belønning i butikken")
        with st.form("ny_belonning_form", clear_on_submit=True):
            b_tittel = st.text_input("Hva er premien? (f.eks. Kinotur, 1 time gaming, Velge lørdagsgodt)")
            b_pris = st.number_input("Pris i stjerner:", min_value=1, max_value=100, value=5)
            b_sendt = st.form_submit_button("Legg til premie")
            if b_sendt and b_tittel.strip():
                data["belonninger"].append({
                    "id": str(uuid.uuid4()),
                    "tittel": b_tittel.strip(),
                    "pris": int(b_pris)
                })
                lagre_data(data)
                st.success("Ny premie lagt til i butikken!")
                st.rerun()

# ----------------- FANE 3: MIDDAGSPLAN & OPPSKRIFTER -----------------
with fane_middag:
    st.header("🍽️ Familiens Middagsplan & Oppskriftsbok")

    oppskrifter = data.get("oppskrifter", STANDARD_MIDDAGER)
    oppskriftsliste = sorted(list(oppskrifter.keys()))

    c_btn1, c_btn2, c_btn3 = st.columns([0.33, 0.34, 0.33])

    with c_btn1:
        if st.button("🎲 Enkelt middagstips!"):
            if oppskriftsliste:
                valgt = random.choice(oppskriftsliste)
                st.info(f"Hva med **{valgt}**?")
                st.caption(f"Ingredienser: {', '.join(oppskrifter[valgt])}")

    with c_btn2:
        st.button(
            "✨ Planlegg hele uken automatisk!", 
            on_click=cb_auto_planlegg, 
            args=(oppskriftsliste,)
        )

    with c_btn3:
        if st.button("🛒 Send alle ukens middager til handlelisten"):
            varer_lagt_til = 0
            for dag in DAGER:
                rett = st.session_state.get(f"rett_{dag}", "").strip()
                if rett in oppskrifter:
                    for ingr in oppskrifter[rett]:
                        if legg_til_vare_i_data(ingr):
                            varer_lagt_til += 1
            lagre_data(data)
            st.toast(f"Ferdig! {varer_lagt_til} nye ingredienser sortert og lagt i handlelisten! 🛒")

    st.write("---")
    st.subheader("📅 Ukens Middager")

    kokk_alternativer = ["Ingen valgt"] + data["medlemmer"]
    onske_alternativer = ["Ingen"] + data["medlemmer"]

    plan_oppdatert = False

    for dag in DAGER:
        dag_data = data["middagsplan"].get(dag, {"rett": "", "kokk": "Ingen valgt", "onske": "Ingen"})

        c_dag, c_rett, c_onske, c_kokk, c_knapp = st.columns([0.18, 0.32, 0.20, 0.20, 0.10])
        
        er_idag = (dag == idag_navn)
        if er_idag:
            c_dag.markdown(f"**👉 {dag} (I dag)**")
        else:
            c_dag.markdown(f"**{dag}**")
        
        valgt_rett = c_rett.text_input(
            f"Rett for {dag}", 
            key=f"rett_{dag}",
            label_visibility="collapsed",
            placeholder="Skriv eller velg fra oppskrifter..."
        )

        valgt_onske = c_onske.selectbox(
            f"Ønske {dag}",
            onske_alternativer,
            index=onske_alternativer.index(dag_data.get("onske", "Ingen")) if dag_data.get("onske", "Ingen") in onske_alternativer else 0,
            key=f"onske_{dag}",
            label_visibility="collapsed",
            help="Hvem sitt ønske er denne middagen?"
        )

        valgt_kokk = c_kokk.selectbox(
            f"Kokk {dag}",
            kokk_alternativer,
            index=kokk_alternativer.index(dag_data.get("kokk", "Ingen valgt")) if dag_data.get("kokk", "Ingen valgt") in kokk_alternativer else 0,
            key=f"kokk_{dag}",
            label_visibility="collapsed",
            help="Hvem lager eller hjelper til?"
        )

        if valgt_rett in oppskrifter:
            if c_knapp.button("🛒", key=f"kjop_dag_{dag}", help=f"Legg ingredienser for {valgt_rett} i handlelisten"):
                lagt_til = 0
                for ingr in oppskrifter[valgt_rett]:
                    if legg_til_vare_i_data(ingr):
                        lagt_til += 1
                lagre_data(data)
                st.toast(f"{lagt_til} ingredienser til {valgt_rett} lagt inn!")

        if (valgt_rett != dag_data.get("rett", "") or 
            valgt_onske != dag_data.get("onske", "Ingen") or 
            valgt_kokk != dag_data.get("kokk", "Ingen valgt")):
            data["middagsplan"][dag] = {
                "rett": valgt_rett,
                "onske": valgt_onske,
                "kokk": valgt_kokk
            }
            plan_oppdatert = True

    if plan_oppdatert:
        lagre_data(data)

    st.write("---")
    
    with st.expander("📖 Familiens Oppskriftsbok (Bla i oppskrifter og velg dag)", expanded=True):
        st.subheader("Favorittretter")
        st.caption("Finn en rett du liker, velg ønsket ukedag og trykk på knappen for å legge den på menyen!")
        
        slett_oppskrift = None
        for tittel, ingr_liste in sorted(oppskrifter.items()):
            if er_forelder:
                col_tittel, col_dag_velg, col_sett_knapp, col_slett_opp = st.columns([0.35, 0.25, 0.32, 0.08])
            else:
                col_tittel, col_dag_velg, col_sett_knapp = st.columns([0.4, 0.28, 0.32])
            
            with col_tittel:
                st.markdown(f"**{tittel}**")
                st.caption(", ".join(ingr_liste) if ingr_liste else "Ingen ingredienser lagt inn")
            
            with col_dag_velg:
                dag_valg = st.selectbox(
                    f"Dag for {tittel}",
                    DAGER,
                    key=f"velg_dag_{tittel}",
                    label_visibility="collapsed"
                )

            with col_sett_knapp:
                st.button(
                    "Sett på menyen 📅",
                    key=f"sett_meny_{tittel}",
                    on_click=cb_sett_middag,
                    args=(dag_valg, tittel)
                )

            if er_forelder:
                with col_slett_opp:
                    if st.button("✕", key=f"del_oppskrift_{tittel}", help="Slett retten fra kokeboken"):
                        slett_oppskrift = tittel

            st.divider()

        if slett_oppskrift:
            del data["oppskrifter"][slett_oppskrift]
            lagre_data(data)
            st.rerun()

        if er_forelder:
            st.write("#### ➕ Legg til en ny familieoppskrift")
            with st.form("ny_oppgave_form_op", clear_on_submit=True):
                ny_rett_tittel = st.text_input("Navn på retten (f.eks. Kjøttdeig og spagetti, Fiskegrateng):")
                ny_rett_ingr = st.text_area(
                    "Ingredienser (skriv med komma mellom hver vare):", 
                    placeholder="Fiskegrateng, Poteter, Gulrøtter, Smør"
                )
                lagre_oppskrift_btn = st.form_submit_button("Lagre oppskrift")
                if lagre_oppskrift_btn and ny_rett_tittel.strip():
                    ingr_renset = [i.strip() for i in ny_rett_ingr.split(",") if i.strip()]
                    data["oppskrifter"][ny_rett_tittel.strip()] = ingr_renset
                    lagre_data(data)
                    st.success(f"{ny_rett_tittel.strip()} er lagret i oppskriftsboken!")
                    st.rerun()

# ----------------- FANE 4: HANDLELISTE -----------------
with fane_handleliste:
    st.header("🛒 Smart Handleliste")
    st.caption("Sortert automatisk etter butikkavdelinger så dere handler raskere!")

    with st.form("form_legg_til_vare", clear_on_submit=True):
        col_vare, col_kat, col_knapp = st.columns([0.55, 0.30, 0.15])
        ny_vare = col_vare.text_input("Vare:", placeholder="f.eks. Melk, Kjøttdeig, Epler")
        kat_valg = col_kat.selectbox("Avdeling:", ["✨ Automatisk avdeling"] + AVDELINGER, index=0)
        legg_til_klikk = col_knapp.form_submit_button("Legg til")
        
        if legg_til_klikk and ny_vare.strip():
            kategori_for_vare = None if kat_valg == "✨ Automatisk avdeling" else kat_valg
            if legg_til_vare_i_data(ny_vare, kategori_for_vare):
                lagre_data(data)
                st.toast(f"Lagt til: {ny_vare.strip()}!")
                st.rerun()
            else:
                st.warning("Varen finnes allerede i listen.")

    st.write("---")

    slett_vare_id = None
    varer_totalt = len(data["handleliste"])

    if varer_totalt == 0:
        st.info("Handlelisten er tom! 🛒")
    else:
        for avdeling in AVDELINGER:
            varer_i_avdeling = [v for v in data["handleliste"] if v.get("kategori") == avdeling]
            if varer_i_avdeling:
                st.subheader(f"{avdeling} ({len(varer_i_avdeling)})")
                for vare_obj in varer_i_avdeling:
                    v_id = vare_obj["id"]
                    v_navn = vare_obj["navn"]
                    c_tekst, c_del = st.columns([0.85, 0.15])
                    c_tekst.write(f"• **{v_navn}**")
                    if c_del.button("Kjøpt ✕", key=f"del_v_{v_id}"):
                        slett_vare_id = v_id
                st.write("")

        if slett_vare_id:
            data["handleliste"] = [v for v in data["handleliste"] if v["id"] != slett_vare_id]
            lagre_data(data)
            st.rerun()

        st.divider()
        if st.button("🗑️ Tøm hele handlelisten", key="btn_tom_liste"):
            data["handleliste"] = []
            lagre_data(data)
            st.toast("Handlelisten er tømt!")
            st.rerun()

# ----------------- FANE 5: FAMILIEMEDLEMMER (KUN FOR FORELDRE) -----------------
if er_forelder and fane_familie:
    with fane_familie:
        st.header("👨‍👩‍👧‍👦 Administrer Familiemedlemmer")
        st.caption("Her kan dere endre navn, legge til personer, og velge hvem som skal samle stjerner.")

        st.subheader("Eksisterende personer")
        for i, person in enumerate(list(data["medlemmer"])):
            col_navn, col_stjerne, col_slett = st.columns([0.5, 0.35, 0.15])
            
            nytt_navn = col_navn.text_input(f"Navn for {person}", value=person, key=f"medlem_{i}")
            er_stjernesamler = person in data.get("stjerne_brukere", [])
            skal_ha_stjerner = col_stjerne.checkbox("Samler stjerner ⭐", value=er_stjernesamler, key=f"stjerne_chk_{i}")

            if nytt_navn.strip() and nytt_navn.strip() != person:
                gammelt_navn = person
                oppdatert_navn = nytt_navn.strip()
                
                data["medlemmer"][i] = oppdatert_navn
                if gammelt_navn in data.get("stjerne_brukere", []):
                    data["stjerne_brukere"] = [oppdatert_navn if x == gammelt_navn else x for x in data["stjerne_brukere"]]
                if gammelt_navn in data.get("poeng", {}):
                    data["poeng"][oppdatert_navn] = data["poeng"].pop(gammelt_navn)

                for oppg in data.get("oppgaver", []):
                    if oppg["hvem"] == gammelt_navn:
                        oppg["hvem"] = oppdatert_navn
                    if oppg.get("fullfort_av") == gammelt_navn:
                        oppg["fullfort_av"] = oppdatert_navn
                
                for dag in DAGER:
                    if data["middagsplan"][dag].get("kokk") == gammelt_navn:
                        data["middagsplan"][dag]["kokk"] = oppdatert_navn
                    if data["middagsplan"][dag].get("onske") == gammelt_navn:
                        data["middagsplan"][dag]["onske"] = oppdatert_navn

                lagre_data(data)
                st.rerun()

            if skal_ha_stjerner != er_stjernesamler:
                if skal_ha_stjerner:
                    if person not in data["stjerne_brukere"]:
                        data["stjerne_brukere"].append(person)
                    if person not in data["poeng"]:
                        data["poeng"][person] = 0
                else:
                    if person in data["stjerne_brukere"]:
                        data["stjerne_brukere"].remove(person)
                lagre_data(data)
                st.rerun()

            if col_slett.button("Fjern", key=f"slett_medlem_{i}"):
                if len(data["medlemmer"]) > 1:
                    data["medlemmer"].remove(person)
                    if person in data.get("stjerne_brukere", []):
                        data["stjerne_brukere"].remove(person)
                    if person in data.get("poeng", {}):
                        data["poeng"].pop(person)
                    lagre_data(data)
                    st.rerun()
                else:
                    st.warning("Det må være minst én person i familien.")

        st.write("---")
        st.subheader("➕ Legg til ny person")
        with st.form("ny_person_form", clear_on_submit=True):
            f_navn = st.text_input("Navn på ny person:")
            f_stjerner = st.checkbox("Skal denne personen samle stjerner for oppgaver?", value=True)
            legg_til = st.form_submit_button("Legg til")
            
            if legg_til and f_navn.strip():
                navn_rent = f_navn.strip()
                if navn_rent not in data["medlemmer"]:
                    data["medlemmer"].append(navn_rent)
                    if f_stjerner:
                        data["stjerne_brukere"].append(navn_rent)
                        data["poeng"][navn_rent] = 0
                    lagre_data(data)
                    st.success(f"{navn_rent} er lagt til!")
                    st.rerun()
                else:
                    st.error("Dette navnet finnes allerede.")
                    