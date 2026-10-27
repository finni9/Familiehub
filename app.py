import streamlit as st
import json
import os
import random
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

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
                "kategori": gjett_kategori(item),
                "kjopt": False
            })
        elif isinstance(item, dict):
            if "id" not in item:
                item["id"] = str(uuid.uuid4())
            if "kategori" not in item:
                item["kategori"] = gjett_kategori(item.get("navn", ""))
            if "kjopt" not in item:
                item["kjopt"] = False
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
        "kategori": valgt_kat,
        "kjopt": False
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

st.set_page_config(page_title="Familiehub", page_icon="🏡", layout="centered")

# ----------------- SIDEPANEL: FORELDREKONTROLL -----------------
with st.sidebar:
    st.header("🔐 Foreldrekontroll")
    if st.session_state["foreldremodus"]:
        st.success("🔓 Foreldremodus er AKTIV")
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
        st.caption("Endringer og sletting er låst for barna.")
        tastet_pin = st.text_input("PIN for mor/far:", type="password", placeholder="Standard: 1234")
        if st.button("Lås opp", use_container_width=True):
            if tastet_pin == data.get("pin", "1234"):
                st.session_state["foreldremodus"] = True
                st.rerun()
            else:
                st.error("Feil PIN-kode!")

# ----------------- MOBILVENNLIG TOPPSTRIPE -----------------
tidssone_norge = ZoneInfo("Europe/Oslo")
naa = datetime.now(tidssone_norge)
dag_indeks = naa.weekday()
idag_navn = DAGER[dag_indeks]
dato_tekst = f"{idag_navn} {naa.day}. {MAANEDER[naa.month - 1]}"
klokke_tekst = naa.strftime("%H:%M")

st.markdown(
    f"""
    <div style="background-color: #EFF6FF; border-radius: 12px; padding: 12px; text-align: center; margin-bottom: 15px; border: 1px solid #BFDBFE;">
        <h2 style="margin: 0; color: #1E3A8A; font-size: 1.5rem;">🏡 Familiehub</h2>
        <div style="margin-top: 4px; font-size: 1.05rem; font-weight: 600; color: #1E40AF;">
            📅 {dato_tekst} &nbsp;•&nbsp; ⏰ kl. {klokke_tekst}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ----------------- PÅMINNELSER (MOBILVENNLIG) -----------------
with st.expander("📌 Familiens Oppslagstavle", expanded=False):
    beskjeder = data.get("beskjeder", [])
    slett_beskjed_id = None
    if beskjeder:
        for b in beskjeder:
            c_lapp, c_del = st.columns([0.82, 0.18])
            with c_lapp:
                st.markdown(
                    f"""
                    <div style="background-color: #FEF3C7; border-left: 4px solid #F59E0B; padding: 8px 12px; border-radius: 6px; margin-bottom: 6px;">
                        <span style="font-size: 0.95rem; font-weight: 600; color: #92400E;">{b['tekst']}</span><br>
                        <span style="font-size: 0.75rem; color: #B45309;">— {b.get('fra', 'Familien')} ({b.get('tid', '')})</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with c_del:
                if st.button("✕", key=f"del_b_{b['id']}", help="Fjern"):
                    slett_beskjed_id = b["id"]

        if slett_beskjed_id:
            data["beskjeder"] = [b for b in data["beskjeder"] if b["id"] != slett_beskjed_id]
            lagre_data(data)
            st.rerun()
    else:
        st.caption("Ingen beskjeder akkurat nå.")

    with st.form("form_ny_beskjed", clear_on_submit=True):
        ny_beskjed_tekst = st.text_input("Ny beskjed / lapp:", placeholder="f.eks. Husk gymtøy i morgen!")
        c_fra, c_knapp = st.columns([0.6, 0.4])
        hvem_fra = c_fra.selectbox("Fra:", data.get("medlemmer", ["Mor", "Far"]))
        post_knapp = c_knapp.form_submit_button("Heng opp 📌", use_container_width=True)

        if post_knapp and ny_beskjed_tekst.strip():
            tidspunkt = naa.strftime("%d.%m kl. %H:%M")
            data["beskjeder"].append({
                "id": str(uuid.uuid4()),
                "tekst": ny_beskjed_tekst.strip(),
                "fra": hvem_fra,
                "tid": tidspunkt
            })
            lagre_data(data)
            st.rerun()

er_forelder = st.session_state["foreldremodus"]

fane_navn = [
    "⭐ Oppgaver", 
    "🎁 Butikk", 
    "🍽️ Middag", 
    "🛒 Handleliste"
]
if er_forelder:
    fane_navn.append("👨‍👩‍👧‍👦 Admin")

faner = st.tabs(fane_navn)
fane_oppgaver = faner[0]
fane_butikk = faner[1]
fane_middag = faner[2]
fane_handleliste = faner[3]
fane_familie = faner[4] if er_forelder else None

# ----------------- FANE 1: OPPGAVER & RUTINER -----------------
with fane_oppgaver:
    oppgaver_oppdatert = False
    slett_id = None
    medlemmer = data.get("medlemmer", [])
    stjerne_brukere = data.get("stjerne_brukere", [])

    c_dag, c_uke = st.columns(2)
    with c_dag:
        if st.button("☀️ Ny dag (Nullstill)", use_container_width=True):
            for o in data["oppgaver"]:
                if o.get("gjentakende", False):
                    o["ferdig"] = False
                    o["fullfort_av"] = None
            lagre_data(data)
            st.toast("Daglige rutiner er nullstilt! ☀️")
            st.rerun()
    with c_uke:
        if er_forelder:
            st.button("🗓️ Start ny uke", on_click=cb_start_ny_uke, use_container_width=True)
        else:
            st.caption("🔒 Ny uke krever PIN")

    st.write("")

    for person in medlemmer:
        er_samler = person in stjerne_brukere
        poeng_tekst = f" • {data['poeng'].get(person, 0)} ⭐" if er_samler else ""
        person_oppgaver = [o for o in data["oppgaver"] if o["hvem"] == person]
        gjenstaende = len([o for o in person_oppgaver if not o["ferdig"]])
        status_tekst = f"({gjenstaende} igjen)" if gjenstaende > 0 else "(Alt fullført! 🎉)"

        with st.expander(f"👤 **{person}**{poeng_tekst} {status_tekst}", expanded=(gjenstaende > 0)):
            if not person_oppgaver:
                st.caption("Ingen oppgaver akkurat nå 🎉")

            for oppg in person_oppgaver:
                oppg_id = oppg["id"]
                merke = "🔄 " if oppg.get("gjentakende") else ""
                tekst_visning = f"{merke}{oppg['tekst']}"
                if oppg.get("stjerner", 0) > 0:
                    tekst_visning += f" *(+{oppg['stjerner']} ⭐)*"

                if er_forelder:
                    c_chk, c_del = st.columns([0.85, 0.15])
                    er_ferdig = c_chk.checkbox(tekst_visning, value=oppg["ferdig"], key=f"chk_{oppg_id}")
                    if c_del.button("✕", key=f"del_{oppg_id}", help="Slett"):
                        slett_id = oppg_id
                else:
                    er_ferdig = st.checkbox(tekst_visning, value=oppg["ferdig"], key=f"chk_{oppg_id}")

                if er_ferdig != oppg["ferdig"]:
                    oppg["ferdig"] = er_ferdig
                    stjerner = oppg.get("stjerner", 0)
                    if er_ferdig:
                        if er_samler:
                            data["poeng"][person] = data["poeng"].get(person, 0) + stjerner
                            st.balloons()
                    else:
                        if er_samler:
                            data["poeng"][person] = max(0, data["poeng"].get(person, 0) - stjerner)
                    oppgaver_oppdatert = True

    # Fellesoppgaver
    felles_oppgaver = [o for o in data["oppgaver"] if o["hvem"] == FELLES_VALG]
    if felles_oppgaver:
        with st.expander(f"🤝 **Fellesoppgaver** ({len(felles_oppgaver)})", expanded=True):
            for oppg in felles_oppgaver:
                oppg_id = oppg["id"]
                merke = "🔄 " if oppg.get("gjentakende") else ""
                tekst_visning = f"{merke}{oppg['tekst']}"
                if oppg.get("stjerner", 0) > 0:
                    tekst_visning += f" *(+{oppg['stjerner']} ⭐)*"
                if oppg["ferdig"] and oppg.get("fullfort_av"):
                    tekst_visning += f" — *({oppg['fullfort_av']})*"

                c_f_chk, c_f_who = st.columns([0.65, 0.35])
                er_ferdig = c_f_chk.checkbox(tekst_visning, value=oppg["ferdig"], key=f"f_chk_{oppg_id}")
                
                if not oppg["ferdig"]:
                    hvem_valg = c_f_who.selectbox(
                        "Hvem?", medlemmer, key=f"f_who_{oppg_id}", label_visibility="collapsed"
                    )
                else:
                    c_f_who.write("")
                    hvem_valg = oppg.get("fullfort_av", medlemmer[0] if medlemmer else "")

                if er_forelder:
                    if st.button("Slett denne fellesoppgaven ✕", key=f"f_del_{oppg_id}"):
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
                        gammel = oppg.get("fullfort_av")
                        if gammel in stjerne_brukere:
                            data["poeng"][gammel] = max(0, data["poeng"].get(gammel, 0) - stjerner)
                        oppg["fullfort_av"] = None
                    oppgaver_oppdatert = True

    if slett_id:
        data["oppgaver"] = [o for o in data["oppgaver"] if o["id"] != slett_id]
        lagre_data(data)
        st.rerun()

    if oppgaver_oppdatert:
        lagre_data(data)
        st.rerun()

    if er_forelder:
        st.write("---")
        with st.expander("➕ **Legg til ny oppgave**"):
            with st.form("form_ny_oppg", clear_on_submit=True):
                oppg_tekst = st.text_input("Gjøremål:")
                valgte = st.multiselect("Til hvem?", [FELLES_VALG] + medlemmer, default=[medlemmer[0]] if medlemmer else [])
                stjerner = st.number_input("Stjerner:", min_value=0, max_value=20, value=1)
                er_daglig = st.checkbox("🔄 Daglig rutine", value=True)
                if st.form_submit_button("Lagre oppgave", use_container_width=True):
                    if oppg_tekst.strip() and valgte:
                        for p in valgte:
                            data["oppgaver"].append({
                                "id": str(uuid.uuid4()),
                                "tekst": oppg_tekst.strip(),
                                "hvem": p,
                                "ferdig": False,
                                "stjerner": int(stjerner),
                                "fullfort_av": None,
                                "gjentakende": er_daglig
                            })
                        lagre_data(data)
                        st.toast("Oppgave lagt til!")
                        st.rerun()

# ----------------- FANE 2: BELØNNINGSBUTIKK -----------------
with fane_butikk:
    st.subheader("🎁 Belønningsbutikk")
    
    stjerne_brukere = data.get("stjerne_brukere", [])
    if stjerne_brukere:
        saldo_tekst = " | ".join([f"**{p}:** {data['poeng'].get(p, 0)} ⭐" for p in stjerne_brukere])
        st.info(f"💳 {saldo_tekst}")

    slett_belonning_id = None
    for bel in data.get("belonninger", []):
        st.markdown(f"### {bel['tittel']} — `{bel['pris']} ⭐`")
        c_k1, c_k2 = st.columns([0.65, 0.35])
        with c_k1:
            hvem_kjoper = st.selectbox("Kjøper:", stjerne_brukere, key=f"b_who_{bel['id']}", label_visibility="collapsed")
        with c_k2:
            har_rad = data["poeng"].get(hvem_kjoper, 0) >= bel["pris"]
            if st.button("Løs inn 🎉", key=f"btn_kjop_{bel['id']}", disabled=not har_rad, use_container_width=True):
                data["poeng"][hvem_kjoper] -= bel["pris"]
                lagre_data(data)
                st.balloons()
                st.toast(f"🎉 Gratulerer {hvem_kjoper}!")
                st.rerun()

        if er_forelder:
            if st.button("Slett premie ✕", key=f"del_bel_{bel['id']}"):
                slett_belonning_id = bel["id"]
        st.divider()

    if slett_belonning_id:
        data["belonninger"] = [b for b in data["belonninger"] if b["id"] != slett_belonning_id]
        lagre_data(data)
        st.rerun()

    if er_forelder:
        with st.expander("➕ **Legg til ny premie**"):
            with st.form("form_ny_premie", clear_on_submit=True):
                b_tittel = st.text_input("Premienavn:")
                b_pris = st.number_input("Pris i stjerner:", min_value=1, max_value=100, value=5)
                if st.form_submit_button("Lagre premie", use_container_width=True) and b_tittel.strip():
                    data["belonninger"].append({
                        "id": str(uuid.uuid4()),
                        "tittel": b_tittel.strip(),
                        "pris": int(b_pris)
                    })
                    lagre_data(data)
                    st.rerun()

# ----------------- FANE 3: MIDDAGSPLAN -----------------
with fane_middag:
    oppskrifter = data.get("oppskrifter", STANDARD_MIDDAGER)
    oppskriftsliste = sorted(list(oppskrifter.keys()))

    c_m1, c_m2 = st.columns(2)
    with c_m1:
        st.button("✨ Auto-planlegg uken", on_click=cb_auto_planlegg, args=(oppskriftsliste,), use_container_width=True)
    with c_m2:
        if st.button("🛒 Middager til handleliste", use_container_width=True):
            lagt = 0
            for d in DAGER:
                rett = st.session_state.get(f"rett_{d}", "").strip()
                if rett in oppskrifter:
                    for ing in oppskrifter[rett]:
                        if legg_til_vare_i_data(ing):
                            lagt += 1
            lagre_data(data)
            st.toast(f"{lagt} ingredienser lagt i handlelisten! 🛒")

    st.write("---")
    kokk_alternativer = ["Ingen valgt"] + data["medlemmer"]
    onske_alternativer = ["Ingen"] + data["medlemmer"]
    plan_oppdatert = False

    for dag in DAGER:
        er_idag = (dag == idag_navn)
        dag_data = data["middagsplan"].get(dag, {"rett": "", "kokk": "Ingen valgt", "onske": "Ingen"})
        dagens_rett = st.session_state.get(f"rett_{dag}", "")
        
        tittel_dag = f"👉 **{dag} (I dag)**" if er_idag else f"📅 **{dag}**"
        
        with st.container():
            st.markdown(f"#### {tittel_dag}")
            
            c_r1, c_r2 = st.columns([0.82, 0.18])
            valgt_rett = c_r1.text_input(
                f"Rett {dag}", 
                key=f"rett_{dag}", 
                placeholder="Hva skal dere spise?", 
                label_visibility="collapsed"
            )
            
            if valgt_rett in oppskrifter:
                if c_r2.button("🛒", key=f"kjop_dag_{dag}", help=f"Kjøp til {valgt_rett}"):
                    for ing in oppskrifter[valgt_rett]:
                        legg_til_vare_i_data(ing)
                    lagre_data(data)
                    st.toast(f"Ingredienser til {valgt_rett} lagt til!")
            else:
                c_r2.write("")

            c_o, c_k = st.columns(2)
            valgt_onske = c_o.selectbox(
                f"Ønske {dag}:", 
                onske_alternativer,
                index=onske_alternativer.index(dag_data.get("onske", "Ingen")) if dag_data.get("onske", "Ingen") in onske_alternativer else 0,
                key=f"onske_{dag}"
            )
            valgt_kokk = c_k.selectbox(
                f"Kokk {dag}:", 
                kokk_alternativer,
                index=kokk_alternativer.index(dag_data.get("kokk", "Ingen valgt")) if dag_data.get("kokk", "Ingen valgt") in kokk_alternativer else 0,
                key=f"kokk_{dag}"
            )

            if (valgt_rett != dag_data.get("rett", "") or 
                valgt_onske != dag_data.get("onske", "Ingen") or 
                valgt_kokk != dag_data.get("kokk", "Ingen valgt")):
                data["middagsplan"][dag] = {
                    "rett": valgt_rett,
                    "onske": valgt_onske,
                    "kokk": valgt_kokk
                }
                plan_oppdatert = True
            
            st.divider()

    if plan_oppdatert:
        lagre_data(data)

    with st.expander("📖 **Familiens Kokebok & Retter**", expanded=False):
        slett_oppskrift = None
        for tittel, ingr_liste in sorted(oppskrifter.items()):
            st.markdown(f"**{tittel}**")
            st.caption(", ".join(ingr_liste) if ingr_liste else "Ingen ingredienser lagt inn")
            
            c_d, c_s = st.columns([0.55, 0.45])
            valgt_dag = c_d.selectbox(f"Dag for {tittel}", DAGER, key=f"v_dag_{tittel}", label_visibility="collapsed")
            c_s.button("Sett på meny 📅", key=f"s_meny_{tittel}", on_click=cb_sett_middag, args=(valgt_dag, tittel), use_container_width=True)
            
            if er_forelder:
                if st.button("Slett oppskrift ✕", key=f"del_op_{tittel}"):
                    slett_oppskrift = tittel
            st.write("---")

        if slett_oppskrift:
            del data["oppskrifter"][slett_oppskrift]
            lagre_data(data)
            st.rerun()

        if er_forelder:
            with st.form("form_ny_oppskrift", clear_on_submit=True):
                ny_r = st.text_input("Rett:")
                ny_i = st.text_area("Ingredienser (komma mellom):")
                if st.form_submit_button("Lagre oppskrift", use_container_width=True) and ny_r.strip():
                    data["oppskrifter"][ny_r.strip()] = [x.strip() for x in ny_i.split(",") if x.strip()]
                    lagre_data(data)
                    st.rerun()

# ----------------- FANE 4: HANDLELISTE (KUN AVKRYSSING, INGEN EKSTRA SLETTEKNAPP) -----------------
with fane_handleliste:
    st.subheader("🛒 Handleliste")

    with st.form("form_ny_vare", clear_on_submit=True):
        ny_v = st.text_input("Ny vare:", placeholder="f.eks. Melk, Kjøttdeig")
        ny_kat = st.selectbox("Avdeling:", ["✨ Automatisk"] + AVDELINGER)
        if st.form_submit_button("Legg til vare", use_container_width=True) and ny_v.strip():
            k = None if ny_kat == "✨ Automatisk" else ny_kat
            if legg_til_vare_i_data(ny_v, k):
                lagre_data(data)
                st.rerun()

    st.write("---")
    handleliste_oppdatert = False

    if not data["handleliste"]:
        st.info("Handlelisten er tom! 🎉")
    else:
        for avd in AVDELINGER:
            varer_i_avd = [v for v in data["handleliste"] if v.get("kategori") == avd]
            if varer_i_avd:
                st.markdown(f"##### {avd} ({len(varer_i_avd)})")
                for v in varer_i_avd:
                    v_id = v["id"]
                    er_kjopt = v.get("kjopt", False)

                    visningstekst = f"~~{v['navn']}~~" if er_kjopt else f"**{v['navn']}**"

                    ny_status = st.checkbox(
                        visningstekst, 
                        value=er_kjopt, 
                        key=f"hl_chk_{v_id}"
                    )
                    if ny_status != er_kjopt:
                        v["kjopt"] = ny_status
                        handleliste_oppdatert = True

                st.write("")

        if handleliste_oppdatert:
            lagre_data(data)
            st.rerun()

        st.divider()

        antall_kjopte = len([v for v in data["handleliste"] if v.get("kjopt", False)])
        if antall_kjopte > 0:
            if st.button(f"🧹 Fjern {antall_kjopte} avkryssede varer", use_container_width=True):
                data["handleliste"] = [v for v in data["handleliste"] if not v.get("kjopt", False)]
                lagre_data(data)
                st.toast("Avkryssede varer er fjernet!")
                st.rerun()

        if st.button("🗑️ Tøm hele listen", use_container_width=True):
            data["handleliste"] = []
            lagre_data(data)
            st.rerun()

# ----------------- FANE 5: FAMILIEADMIN -----------------
if er_forelder and fane_familie:
    with fane_familie:
        st.subheader("👨‍👩‍👧‍👦 Familieadministrasjon")
        
        for i, person in enumerate(list(data["medlemmer"])):
            st.markdown(f"**Person {i+1}: {person}**")
            nytt_navn = st.text_input(f"Navn", value=person, key=f"adm_navn_{i}")
            er_stjernesamler = person in data.get("stjerne_brukere", [])
            skal_ha = st.checkbox("Samler stjerner ⭐", value=er_stjernesamler, key=f"adm_stj_{i}")

            if nytt_navn.strip() and nytt_navn.strip() != person:
                gammelt = person
                nytt = nytt_navn.strip()
                data["medlemmer"][i] = nytt
                if gammelt in data.get("stjerne_brukere", []):
                    data["stjerne_brukere"] = [nytt if x == gammelt else x for x in data["stjerne_brukere"]]
                if gammelt in data.get("poeng", {}):
                    data["poeng"][nytt] = data["poeng"].pop(gammelt)
                for o in data.get("oppgaver", []):
                    if o["hvem"] == gammelt: o["hvem"] = nytt
                    if o.get("fullfort_av") == gammelt: o["fullfort_av"] = nytt
                for d in DAGER:
                    if data["middagsplan"][d].get("kokk") == gammelt: data["middagsplan"][d]["kokk"] = nytt
                    if data["middagsplan"][d].get("onske") == gammelt: data["middagsplan"][d]["onske"] = nytt
                lagre_data(data)
                st.rerun()

            if skal_ha != er_stjernesamler:
                if skal_ha:
                    if person not in data["stjerne_brukere"]: data["stjerne_brukere"].append(person)
                    if person not in data["poeng"]: data["poeng"][person] = 0
                else:
                    if person in data["stjerne_brukere"]: data["stjerne_brukere"].remove(person)
                lagre_data(data)
                st.rerun()

            if st.button(f"Fjern {person} ✕", key=f"adm_del_{i}"):
                if len(data["medlemmer"]) > 1:
                    data["medlemmer"].remove(person)
                    if person in data.get("stjerne_brukere", []): data["stjerne_brukere"].remove(person)
                    if person in data.get("poeng", {}): data["poeng"].pop(person)
                    lagre_data(data)
                    st.rerun()
            st.divider()

        with st.form("form_nytt_medlem", clear_on_submit=True):
            f_n = st.text_input("Ny person:")
            f_s = st.checkbox("Samle stjerner?", value=True)
            if st.form_submit_button("Legg til person", use_container_width=True) and f_n.strip():
                if f_n.strip() not in data["medlemmer"]:
                    data["medlemmer"].append(f_n.strip())
                    if f_s:
                        data["stjerne_brukere"].append(f_n.strip())
                        data["poeng"][f_n.strip()] = 0
                    lagre_data(data)
                    st.rerun()