import streamlit as st
import json
import random
import uuid
import base64
import io
import time
import calendar
import pandas as pd
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo
from PIL import Image
from streamlit_gsheets import GSheetsConnection

TIDSSONE_NORGE = ZoneInfo("Europe/Oslo")

STANDARD_MIDDAGER = {
    "Taco": {
        "ingredienser": ["Kjøttdeig", "Tacokrydder", "Tortillalefser", "Rømme", "Ost", "Salsa", "Mais", "Agurk"],
        "bilde": None
    },
    "Laks med grønnsaker og poteter": {
        "ingredienser": ["Laksefilet", "Poteter", "Gulrøtter", "Rømme", "Sitron"],
        "bilde": None
    },
    "Spagetti bolognese": {
        "ingredienser": ["Spagetti", "Kjøttdeig", "Hakkede tomater", "Løk", "Hvitløk", "Parmesan"],
        "bilde": None
    },
    "Hjemmelaget pizza": {
        "ingredienser": ["Pizzadeig", "Pizzasaus", "Ost", "Skinke", "Champignon"],
        "bilde": None
    },
    "Kyllingwok": {
        "ingredienser": ["Kyllingfilet", "Wokgrønnsaker", "Woksaus", "Ris eller nudler"],
        "bilde": None
    },
    "Fiskepinner med potetmos": {
        "ingredienser": ["Fiskepinner", "Poteter", "Erter", "Smør", "Melk"],
        "bilde": None
    },
    "Kjøttkaker i brun saus": {
        "ingredienser": ["Kjøttkaker", "Brun saus", "Poteter", "Tyttebærsyltetøy", "Ertestuing"],
        "bilde": None
    },
    "Pannekaker med bacon": {
        "ingredienser": ["Hvetemel", "Egg", "Melk", "Bacon", "Blåbærsyltetøy"],
        "bilde": None
    },
    "Pølseform / Pølsegrateng": {
        "ingredienser": ["Kjøttpølser", "Makaroni", "Hvit saus", "Ost", "Brokkoli"],
        "bilde": None
    }
}

STANDARD_BASISVARER = [
    {"id": "b1", "label": "🥛 Melk", "navn": "Melk", "kategori": "🧀 Meieri & Kjølevare"},
    {"id": "b2", "label": "🍞 Brød", "navn": "Brød", "kategori": "🍞 Tørrvare, Krydder & Kolonial"},
    {"id": "b3", "label": "🧈 Smør", "navn": "Smør", "kategori": "🧀 Meieri & Kjølevare"},
    {"id": "b4", "label": "🥚 Egg", "navn": "Egg", "kategori": "🧀 Meieri & Kjølevare"},
    {"id": "b5", "label": "🍌 Bananer", "navn": "Bananer", "kategori": "🥦 Frukt & Grønt"},
    {"id": "b6", "label": "☕ Kaffe", "navn": "Kaffe", "kategori": "🍞 Tørrvare, Krydder & Kolonial"},
]

STANDARD_AKTIVITETER = [
    "🎲 Spille brettspill sammen",
    "🍿 Lage popcorn og se en god familiefilm",
    "🌲 Gå på oppdagelsestur i skogen eller fjæra",
    "🏕️ Bygge teppehytte i stua",
    "🧁 Bake boller eller muffins sammen",
    "🚲 Ta en sykkeltur eller sparkesykkel-race",
    "🎨 Tegnekonkurranse eller malebord",
    "⚽ Fotballtriks eller lek på plenen"
]

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
        "syltetøy", "brød", "rundstykke", "knekkebrød", "olje", "krydder", "kaffe"
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
DAGER_KORT = ["Man", "Tir", "Ons", "Tor", "Fre", "Lør", "Søn"]
MAANEDER = [
    "januar", "februar", "mars", "april", "mai", "juni",
    "juli", "august", "september", "oktober", "november", "desember"
]
FELLES_VALG = "Felles (Mor & Far / Den som gjør det)"

PERSON_PROFILER = [
    {"bg": "#1D4ED8", "kant": "#60A5FA", "tekst": "#FFFFFF", "badge": "#1E40AF", "ikon": "🦁"},
    {"bg": "#BE185D", "kant": "#F472B6", "tekst": "#FFFFFF", "badge": "#9D174D", "ikon": "🐰"},
    {"bg": "#B45309", "kant": "#FBBF24", "tekst": "#FFFFFF", "badge": "#92400E", "ikon": "🐻"},
    {"bg": "#047857", "kant": "#34D399", "tekst": "#FFFFFF", "badge": "#065F46", "ikon": "🦊"},
    {"bg": "#6D28D9", "kant": "#A78BFA", "tekst": "#FFFFFF", "badge": "#5B21B6", "ikon": "🐼"},
    {"bg": "#C2410C", "kant": "#FB923C", "tekst": "#FFFFFF", "badge": "#9A3412", "ikon": "🐯"},
]

def hent_profil(person, alle_medlemmer):
    if person == FELLES_VALG or person == "Felles":
        return {"bg": "#334155", "kant": "#94A3B8", "tekst": "#FFFFFF", "badge": "#1E293B", "ikon": "🤝"}
    if person in alle_medlemmer:
        idx = alle_medlemmer.index(person) % len(PERSON_PROFILER)
        return PERSON_PROFILER[idx]
    return PERSON_PROFILER[0]

st.set_page_config(page_title="Familiehub", page_icon="🏡", layout="centered")

skjul_streamlit_elementer = """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden; display: none;}
    [data-testid="stToolbar"] {visibility: hidden; display: none;}
    [data-testid="stDecoration"] {visibility: hidden; display: none;}
    [data-testid="stStatusWidget"] {visibility: hidden; display: none;}
    [data-testid="manage-app-button"] {display: none !important;}
    div[class*="viewerBadge"] {display: none !important;}
</style>
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="theme-color" content="#FF6B6B">
"""
st.markdown(skjul_streamlit_elementer, unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

def bilde_til_base64(opplastet_fil):
    try:
        bilde = Image.open(opplastet_fil)
        bilde = bilde.convert("RGB")
        max_str = 400
        if max(bilde.size) > max_str:
            bilde.thumbnail((max_str, max_str), Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        bilde.save(buffer, format="JPEG", quality=60, optimize=True)
        kodet = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/jpeg;base64,{kodet}"
    except Exception:
        return None

def gjett_kategori(varenavn):
    tekst = varenavn.lower()
    for kat, stikkord_liste in KATEGORI_REGLER.items():
        for stikkord in stikkord_liste:
            if stikkord in tekst:
                return kat
    return "📦 Annet / Diverse"

def migrer_oppskrifter(gamle_oppskrifter):
    nye = {}
    for tittel, val in gamle_oppskrifter.items():
        if isinstance(val, list):
            nye[tittel] = {"ingredienser": val, "bilde": None}
        elif isinstance(val, dict):
            if "ingredienser" not in val: val["ingredienser"] = []
            if "bilde" not in val: val["bilde"] = None
            nye[tittel] = val
    return nye

def migrer_handleliste(gammel_liste):
    ny_liste = []
    for item in gammel_liste:
        if isinstance(item, str):
            ny_liste.append({
                "id": str(uuid.uuid4()),
                "navn": item,
                "mengde": "",
                "kategori": gjett_kategori(item),
                "kjopt": False
            })
        elif isinstance(item, dict):
            if "id" not in item: item["id"] = str(uuid.uuid4())
            if "mengde" not in item: item["mengde"] = ""
            if "kategori" not in item: item["kategori"] = gjett_kategori(item.get("navn", ""))
            if "kjopt" not in item: item["kjopt"] = False
            ny_liste.append(item)
    return ny_liste

def migrer_middagsplan(gammel_plan):
    ny_plan = {}
    for dag in DAGER:
        innslag = gammel_plan.get(dag, "")
        if isinstance(innslag, dict):
            ny_plan[dag] = innslag.get("rett", "")
        elif isinstance(innslag, str):
            ny_plan[dag] = innslag
        else:
            ny_plan[dag] = ""
    return ny_plan

def migrer_oppgaver(oppg_liste):
    nye = []
    for o in oppg_liste:
        if "id" not in o: o["id"] = str(uuid.uuid4())
        if "ikon" not in o: o["ikon"] = "✨"
        if "status" not in o:
            o["status"] = "godkjent" if o.get("ferdig", False) else "ugjort"
        if "gjentakende" not in o: o["gjentakende"] = True
        if "stjerner" not in o: o["stjerner"] = 1
        nye.append(o)
    return nye

def standard_data(valgt_pin="1234"):
    idag_str = datetime.now(TIDSSONE_NORGE).strftime("%Y-%m-%d")
    return {
        "pin": str(valgt_pin),
        "sist_nullstilt": idag_str,
        "uke_oppgaver_lost": 0,
        "medlemmer": ["Far", "Mor", "Barn 1", "Barn 2"],
        "stjerne_brukere": ["Barn 1", "Barn 2"],
        "poeng": {"Far": 0, "Mor": 0, "Barn 1": 0, "Barn 2": 0},
        "sparemaal": {},
        "aktiviteter": STANDARD_AKTIVITETER,
        "stjerne_logg": [],
        "fryser": [
            {"id": str(uuid.uuid4()), "navn": "Laksefilet (4 pk)"},
            {"id": str(uuid.uuid4()), "navn": "Hjemmelaget Bolognese"}
        ],
        "beskjeder": [
            {"id": str(uuid.uuid4()), "tekst": "Velkommen til Familiehuben! 🌟", "fra": "Familien", "tid": "Kl. 08:00"}
        ],
        "merkedager": [],
        "belonninger": [
            {"id": str(uuid.uuid4()), "tittel": "30 min ekstra skjermtid", "pris": 5},
            {"id": str(uuid.uuid4()), "tittel": "Velge lørdagsgodt", "pris": 8},
            {"id": str(uuid.uuid4()), "tittel": "Bestemme lørdagsfilm", "pris": 10}
        ],
        "oppgaver": [
            {"id": str(uuid.uuid4()), "ikon": "🪥", "tekst": "Pusse tenner morgen & kveld", "hvem": "Barn 1", "status": "ugjort", "stjerner": 1, "fullfort_av": None, "gjentakende": True},
            {"id": str(uuid.uuid4()), "ikon": "🪥", "tekst": "Pusse tenner morgen & kveld", "hvem": "Barn 2", "status": "ugjort", "stjerner": 1, "fullfort_av": None, "gjentakende": True},
            {"id": str(uuid.uuid4()), "ikon": "🛏️", "tekst": "Re opp sengen", "hvem": "Barn 1", "status": "ugjort", "stjerner": 1, "fullfort_av": None, "gjentakende": True},
            {"id": str(uuid.uuid4()), "ikon": "🛏️", "tekst": "Re opp sengen", "hvem": "Barn 2", "status": "ugjort", "stjerner": 1, "fullfort_av": None, "gjentakende": True},
            {"id": str(uuid.uuid4()), "ikon": "🍽️", "tekst": "Rydde av bordet etter middag", "hvem": FELLES_VALG, "status": "ugjort", "stjerner": 2, "fullfort_av": None, "gjentakende": True},
        ],
        "oppskrifter": STANDARD_MIDDAGER,
        "middagsplan": {dag: "" for dag in DAGER},
        "basisvarer": STANDARD_BASISVARER,
        "handleliste": migrer_handleliste(["Melk", "Brød", "Smør"])
    }

def hent_hele_tabellen():
    for forsok in range(3):
        try:
            df = conn.read(ttl=2)
            if df is None or df.empty:
                return pd.DataFrame(columns=["familie_kode", "data_dump"])
            if "familie_kode" not in df.columns:
                df["familie_kode"] = "hoved"
                if "data_dump" not in df.columns:
                    df["data_dump"] = "{}"
            return df[["familie_kode", "data_dump"]].dropna(subset=["familie_kode"])
        except Exception:
            if forsok < 2:
                time.sleep(0.5 * (forsok + 1))
            else:
                return pd.DataFrame(columns=["familie_kode", "data_dump"])

def hent_familie_json(familie_navn):
    if "familie_data" in st.session_state and st.session_state.get("aktiv_familie") == str(familie_navn).lower():
        return st.session_state["familie_data"]

    df = hent_hele_tabellen()
    rad = df[df["familie_kode"].astype(str).str.lower() == str(familie_navn).lower()]
    if not rad.empty:
        try:
            parsed = json.loads(str(rad["data_dump"].iloc[0]))
            st.session_state["familie_data"] = parsed
            return parsed
        except Exception:
            return None
    return None

def lagre_familie_data(familie_navn, ny_data):
    st.session_state["familie_data"] = ny_data
    for forsok in range(3):
        try:
            df = hent_hele_tabellen()
            json_tekst = json.dumps(ny_data, ensure_ascii=False)
            
            if len(json_tekst) > 48000:
                st.error("⚠️ Datamengden er for stor for regnearket.")
                return False
            
            mask = df["familie_kode"].astype(str).str.lower() == str(familie_navn).lower()
            if mask.any():
                df.loc[mask, "data_dump"] = json_tekst
            else:
                ny_rad = pd.DataFrame([{"familie_kode": str(familie_navn).strip().lower(), "data_dump": json_tekst}])
                df = pd.concat([df, ny_rad], ignore_index=True)
                
            conn.update(data=df)
            return True
        except Exception:
            if forsok < 2:
                time.sleep(0.6 * (forsok + 1))
            else:
                st.toast("⚠️ Sky-lagring er litt treg. Endringen er beholdt i minnet!")
                return False

def endre_familie_navn(gammelt_navn, nytt_navn):
    try:
        df = hent_hele_tabellen()
        nytt_renset = nytt_navn.strip().lower()
        gammelt_renset = gammelt_navn.strip().lower()
        
        if (df["familie_kode"].astype(str).str.lower() == nytt_renset).any():
            return False, "Dette familienavnet er allerede opptatt av en annen familie!"
            
        mask = df["familie_kode"].astype(str).str.lower() == gammelt_renset
        if mask.any():
            df.loc[mask, "familie_kode"] = nytt_renset
            conn.update(data=df)
            return True, "Navnet er oppdatert!"
        return False, "Fant ikke den opprinnelige familien i databasen."
    except Exception as e:
        return False, f"Feil ved oppdatering i Google Sheets: {e}"

# ----------------- INNLOGGING -----------------
url_params = st.query_params

if "aktiv_familie" not in st.session_state:
    if "fam" in url_params and "key" in url_params:
        lagret_fam = url_params["fam"].strip().lower()
        lagret_key = str(url_params["key"]).strip()
        f_data = hent_familie_json(lagret_fam)
        if f_data and str(f_data.get("pin", "")) == lagret_key:
            st.session_state["aktiv_familie"] = lagret_fam

if "aktiv_familie" not in st.session_state or not st.session_state["aktiv_familie"]:
    st.markdown(
        """
        <div style="background-color: #1E293B; border-radius: 16px; padding: 26px; text-align: center; border: 2px solid #3B82F6; margin-top: 20px;">
            <h1 style="color: #60A5FA; margin: 0; font-size: 1.9rem; font-weight: 900;">🏡 Familiehub</h1>
            <p style="color: #93C5FD; font-size: 1.05rem; margin-top: 6px; font-weight: 600;">Logg inn i familiens hjem med navn og PIN-kode</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.write("")

    valg_modus = st.radio("Velg handling:", ["Logg inn", "Opprett ny familie"], horizontal=True)

    with st.form("form_login"):
        f_navn = st.text_input("Familiens etternavn / kallenavn:", placeholder="f.eks. Hansen, Olsen").strip()
        f_pin = st.text_input("Familiens 4-sifrede PIN:", type="password", placeholder="f.eks. 1234", max_chars=8).strip()
        husk_meg = st.checkbox("Husk denne enheten (slipper å logge inn på nytt her)", value=True)
        
        knapp = st.form_submit_button("Åpne Familiehub 🚀", use_container_width=True)

        if knapp:
            if not f_navn or not f_pin:
                st.error("Vennligst fyll inn både familienavn og PIN-kode.")
            else:
                eksisterende_data = hent_familie_json(f_navn)

                if valg_modus == "Logg inn":
                    if not eksisterende_data:
                        st.error(f"Fant ingen familie med navnet '{f_navn}'. Sjekk skrivemåten eller velg 'Opprett ny familie'.")
                    else:
                        riktig_pin = str(eksisterende_data.get("pin", "1234"))
                        if f_pin == riktig_pin:
                            st.session_state["aktiv_familie"] = f_navn.lower()
                            if husk_meg:
                                st.query_params["fam"] = f_navn.lower()
                                st.query_params["key"] = f_pin
                            st.toast(f"Velkommen hjem, familie {f_navn}! 👋")
                            st.rerun()
                        else:
                            st.error("Feil PIN-kode for denne familien!")

                elif valg_modus == "Opprett ny familie":
                    if eksisterende_data:
                        st.error(f"Familienavnet '{f_navn}' er allerede opptatt! Vennligst velg et annet kallenavn.")
                    else:
                        ny_fam = standard_data(valgt_pin=f_pin)
                        if lagre_familie_data(f_navn, ny_fam):
                            st.session_state["aktiv_familie"] = f_navn.lower()
                            if husk_meg:
                                st.query_params["fam"] = f_navn.lower()
                                st.query_params["key"] = f_pin
                            st.success(f"Familien {f_navn} er opprettet! Åpner huben...")
                            st.rerun()

    st.stop()

# ----------------- HENT OG FORBERED DATA -----------------
aktiv_kode = st.session_state["aktiv_familie"]
raw_data = hent_familie_json(aktiv_kode)

if not raw_data:
    st.warning("Kobler til familiens skyhub...")
    st.stop()

if "merkedager" not in raw_data: raw_data["merkedager"] = []
if "oppskrifter" not in raw_data: raw_data["oppskrifter"] = STANDARD_MIDDAGER
else: raw_data["oppskrifter"] = migrer_oppskrifter(raw_data["oppskrifter"])
if "basisvarer" not in raw_data: raw_data["basisvarer"] = STANDARD_BASISVARER
if "sparemaal" not in raw_data: raw_data["sparemaal"] = {}
if "aktiviteter" not in raw_data: raw_data["aktiviteter"] = STANDARD_AKTIVITETER
if "fryser" not in raw_data: raw_data["fryser"] = []
if "uke_oppgaver_lost" not in raw_data: raw_data["uke_oppgaver_lost"] = 0
if "stjerne_logg" not in raw_data: raw_data["stjerne_logg"] = []

raw_data["oppgaver"] = migrer_oppgaver(raw_data.get("oppgaver", []))
raw_data["handleliste"] = migrer_handleliste(raw_data.get("handleliste", []))
raw_data["middagsplan"] = migrer_middagsplan(raw_data.get("middagsplan", {}))

data = raw_data

def lagre_naa():
    return lagre_familie_data(aktiv_kode, data)

def logg_stjerne_hendelse(person, handling_type, antall, beskrivelse):
    naa_tid = datetime.now(TIDSSONE_NORGE)
    if "stjerne_logg" not in data:
        data["stjerne_logg"] = []
    data["stjerne_logg"].append({
        "id": str(uuid.uuid4()),
        "tid": naa_tid.strftime("%Y-%m-%d %H:%M"),
        "aar_mnd": naa_tid.strftime("%Y-%m"),
        "person": person,
        "type": handling_type,
        "antall": int(antall),
        "beskrivelse": beskrivelse
    })
    # Behold de siste 250 loggførte hendelsene
    if len(data["stjerne_logg"]) > 250:
        data["stjerne_logg"] = data["stjerne_logg"][-250:]

# ----------------- MIDNATT-NULLSTILLING -----------------
idag_dato = datetime.now(TIDSSONE_NORGE).date()
idag_str = idag_dato.strftime("%Y-%m-%d")

if data.get("sist_nullstilt") != idag_str:
    for o in data["oppgaver"]:
        if o.get("gjentakende", False):
            o["status"] = "ugjort"
            o["fullfort_av"] = None
    data["merkedager"] = [
        m for m in data.get("merkedager", [])
        if datetime.strptime(m["dato"], "%Y-%m-%d").date() >= idag_dato
    ]
    data["sist_nullstilt"] = idag_str
    lagre_naa()

def legg_til_vare_i_data(varenavn, mengde="", kategori=None):
    if not varenavn.strip(): return False
    renset_navn = varenavn.strip()
    
    for v in data["handleliste"]:
        if v["navn"].lower() == renset_navn.lower():
            if v.get("kjopt", False):
                v["kjopt"] = False
                if mengde.strip():
                    v["mengde"] = mengde.strip()
                return True
            return False
    
    valgt_kat = kategori if kategori and kategori in AVDELINGER else gjett_kategori(renset_navn)
    data["handleliste"].append({
        "id": str(uuid.uuid4()),
        "navn": renset_navn,
        "mengde": mengde.strip(),
        "kategori": valgt_kat,
        "kjopt": False
    })
    return True

def cb_sett_middag(dag, rett):
    data["middagsplan"][dag] = rett
    lagre_naa()
    st.session_state[f"rett_{dag}"] = rett

def cb_auto_planlegg(oppskriftsliste):
    if not oppskriftsliste: return
    if len(oppskriftsliste) >= 7: ukens_trekk = random.sample(oppskriftsliste, 7)
    else: ukens_trekk = [random.choice(oppskriftsliste) for _ in range(7)]
    for i, dag in enumerate(DAGER):
        ny_rett = ukens_trekk[i]
        data["middagsplan"][dag] = ny_rett
        st.session_state[f"rett_{dag}"] = ny_rett
    lagre_naa()

def cb_start_ny_uke():
    data["oppgaver"] = [o for o in data["oppgaver"] if o.get("gjentakende", False) or o.get("status") != "godkjent"]
    for o in data["oppgaver"]:
        o["status"] = "ugjort"
        o["fullfort_av"] = None
    for dag in DAGER:
        data["middagsplan"][dag] = ""
        st.session_state[f"rett_{dag}"] = ""
    data["uke_oppgaver_lost"] = 0
    lagre_naa()

for dag in DAGER:
    if f"rett_{dag}" not in st.session_state:
        st.session_state[f"rett_{dag}"] = data["middagsplan"].get(dag, "")

if "foreldremodus" not in st.session_state:
    st.session_state["foreldremodus"] = False

# ----------------- MODAL FOR FORELDRE-PIN -----------------
@st.dialog("🔐 Tast foreldre-PIN")
def aapne_pin_dialog():
    st.caption("Skriv inn familiens PIN for å låse opp Admin og godkjenne oppgaver:")
    pin_input = st.text_input("PIN-kode:", type="password", max_chars=8, key="dlg_pin_input")
    c_ok, c_avbr = st.columns(2)
    if c_ok.button("Lås opp 🔓", use_container_width=True):
        if pin_input == str(data.get("pin", "1234")):
            st.session_state["foreldremodus"] = True
            st.toast("Foreldremodus aktivert! 👨‍👩‍👧‍👦")
            st.rerun()
        else:
            st.error("Feil PIN-kode!")
    if c_avbr.button("Avbryt", use_container_width=True):
        st.rerun()

# ----------------- TOPPSTRIPE (VARM SOLNEDGANG) -----------------
naa = datetime.now(TIDSSONE_NORGE)
dag_indeks = naa.weekday()
idag_navn = DAGER[dag_indeks]
dato_tekst = f"{idag_navn} {naa.day}. {MAANEDER[naa.month - 1]}"
klokke_tekst = naa.strftime("%H:%M")

col_banner, col_parent_btn = st.columns([0.76, 0.24])

with col_parent_btn:
    st.write("")
    if st.session_state["foreldremodus"]:
        if st.button("🔓 Lås foreldre", use_container_width=True, help="Slå av foreldremodus"):
            st.session_state["foreldremodus"] = False
            st.toast("Barnemodus aktivert!")
            st.rerun()
    else:
        if st.button("🔐 Foreldre", use_container_width=True, help="Tast PIN for å godkjenne stjerner og åpne Admin"):
            aapne_pin_dialog()

with col_banner:
    banner_html = f"""
    <div style="background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 50%, #FFA8A8 100%); 
                border-radius: 16px; padding: 12px 14px; text-align: left; margin-bottom: 6px; 
                box-shadow: 0 4px 15px rgba(255, 107, 107, 0.25);">
        <div style="display: inline-block; background: rgba(255, 255, 255, 0.28); 
                    padding: 2px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 800; 
                    color: #FFFFFF; text-transform: uppercase; margin-bottom: 4px;">
            ✨ Familiens Hjem
        </div>
        <h3 style="margin: 0; color: #FFFFFF; font-size: 1.4rem; font-weight: 900; letter-spacing: -0.5px; text-shadow: 0 2px 4px rgba(0,0,0,0.15);">
            🏡 Familiehub <span style="font-weight: 400; opacity: 0.95; color: #FFFFFF;">({aktiv_kode.capitalize()})</span>
        </h3>
        <div style="font-size: 0.85rem; font-weight: 600; color: #FFF3E0; margin-top: 2px;">
            📅 {dato_tekst} &nbsp;•&nbsp; ⏰ {klokke_tekst}
        </div>
    </div>
    """
    st.markdown(banner_html, unsafe_allow_html=True)

# ----------------- KALENDER MED FULLT MÅNEDSRUTENETT (MAN-SØN) -----------------
with st.expander("🗓️ **Familiens Månedskalender & Aktiviteter**", expanded=False):
    medlemmer = data.get("medlemmer", ["Far", "Mor", "Barn 1", "Barn 2"])
    merkedager = data.get("merkedager", [])

    if "vis_aar" not in st.session_state:
        st.session_state["vis_aar"] = idag_dato.year
    if "vis_mnd" not in st.session_state:
        st.session_state["vis_mnd"] = idag_dato.month

    c_prev, c_mnd_tittel, c_next = st.columns([0.2, 0.6, 0.2])
    with c_prev:
        if st.button("◀ Forrige", use_container_width=True):
            if st.session_state["vis_mnd"] == 1:
                st.session_state["vis_mnd"] = 12
                st.session_state["vis_aar"] -= 1
            else:
                st.session_state["vis_mnd"] -= 1
            st.rerun()

    vis_aar = st.session_state["vis_aar"]
    vis_mnd = st.session_state["vis_mnd"]
    mnd_navn_tekst = f"{MAANEDER[vis_mnd - 1].capitalize()} {vis_aar}"
    
    with c_mnd_tittel:
        st.markdown(
            f"<h4 style='text-align: center; margin: 4px 0; color: #60A5FA; font-weight: 900;'>{mnd_navn_tekst}</h4>",
            unsafe_allow_html=True
        )

    with c_next:
        if st.button("Neste ▶", use_container_width=True):
            if st.session_state["vis_mnd"] == 12:
                st.session_state["vis_mnd"] = 1
                st.session_state["vis_aar"] += 1
            else:
                st.session_state["vis_mnd"] += 1
            st.rerun()

    rad_dager = st.columns(7)
    for idx_d, d_navn in enumerate(DAGER_KORT):
        farge_header = "#F87171" if idx_d >= 5 else "#60A5FA"
        rad_dager[idx_d].markdown(
            f"<div style='text-align: center; font-weight: 800; font-size: 0.8rem; color: {farge_header}; padding-bottom: 4px;'>{d_navn}</div>",
            unsafe_allow_html=True
        )

    cal = calendar.Calendar(firstweekday=0)
    uker = cal.monthdayscalendar(vis_aar, vis_mnd)

    for uke in uker:
        kolonner_uke = st.columns(7)
        for dag_idx, dag_nr in enumerate(uke):
            with kolonner_uke[dag_idx]:
                if dag_nr == 0:
                    st.markdown("<div style='min-height: 64px; background-color: rgba(255,255,255,0.03); border-radius: 8px; margin-bottom: 5px; opacity: 0.3;'></div>", unsafe_allow_html=True)
                else:
                    curr_date = date(vis_aar, vis_mnd, dag_nr)
                    curr_date_str = curr_date.strftime("%Y-%m-%d")
                    er_idag = (curr_date == idag_dato)
                    
                    dagens_hendelser = [m for m in merkedager if m.get("dato") == curr_date_str]
                    
                    if er_idag:
                        kant_stil = "2.5px solid #3B82F6"
                        bg_rute = "#1E293B"
                        dag_html = "<span style='background-color: #3B82F6; color: #FFFFFF; padding: 2px 7px; border-radius: 8px; font-weight: 900; font-size: 0.85rem;'>I dag</span>"
                    else:
                        kant_stil = "1.5px solid #475569"
                        bg_rute = "#0F172A"
                        dag_html = f"<span style='color: #F8FAFC; font-weight: 900; font-size: 0.95rem;'>{dag_nr}</span>"

                    hendelser_html = ""
                    for h in dagens_hendelser:
                        h_hvem = h.get("hvem", FELLES_VALG)
                        prof = hent_profil(h_hvem, medlemmer)
                        h_ikon = h.get("ikon", "📌")
                        h_tittel = h["tittel"]
                        hendelser_html += f"""
                        <div style="background-color: {prof['bg']}; border-left: 3.5px solid {prof['kant']}; padding: 2px 4px; border-radius: 4px; font-size: 0.72rem; font-weight: 800; color: #FFFFFF; margin-top: 3px; line-height: 1.2; box-shadow: 0 1px 3px rgba(0,0,0,0.3);" title="{h_tittel} ({h_hvem})">
                            {prof['ikon']} {h_ikon} <span style="color: #FFFFFF;">{h_tittel}</span>
                        </div>
                        """

                    st.markdown(
                        f"""
                        <div style="min-height: 64px; background-color: {bg_rute}; border: {kant_stil}; border-radius: 8px; padding: 4px; margin-bottom: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.2);">
                            <div style="text-align: right; line-height: 1; margin-bottom: 3px;">
                                {dag_html}
                            </div>
                            {hendelser_html}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

    st.write("---")
    st.markdown("##### 📋 Kommende aktiviteter")
    slett_merkedag_id = None
    
    if merkedager:
        merkedager_sortert = sorted(merkedager, key=lambda x: x["dato"])
        for m in merkedager_sortert:
            m_dato = datetime.strptime(m["dato"], "%Y-%m-%d").date()
            dager_igjen = (m_dato - idag_dato).days
            
            if dager_igjen < 0:
                continue
            elif dager_igjen == 0: nedtelling = "🎉 I DAG!"
            elif dager_igjen == 1: nedtelling = "⏰ I morgen!"
            else: nedtelling = f"⏳ Om {dager_igjen} dager"

            hvem = m.get("hvem", FELLES_VALG)
            prof = hent_profil(hvem, medlemmer)

            c_info, c_slett = st.columns([0.84, 0.16])
            with c_info:
                st.markdown(
                    f"""
                    <div style="background-color: {prof['bg']}; border-left: 6px solid {prof['kant']}; border: 1.5px solid {prof['kant']}; border-left-width: 6px; padding: 8px 12px; border-radius: 8px; margin-bottom: 6px;">
                        <span style="font-size: 1.05rem; font-weight: 800; color: #FFFFFF;">{m.get('ikon', '📌')} {m['tittel']}</span>
                        <span style="background-color: {prof['badge']}; color: #FFFFFF; padding: 1px 7px; border-radius: 10px; font-size: 0.75rem; font-weight: 700; margin-left: 6px;">
                            {prof['ikon']} {hvem}
                        </span><br>
                        <span style="font-size: 0.85rem; color: #E2E8F0;">📅 {DAGER[m_dato.weekday()]} {m_dato.strftime('%d.%m.%Y')} — <b style="color: #FCD34D;">{nedtelling}</b></span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with c_slett:
                if st.button("✕", key=f"del_m_{m['id']}", help="Fjern aktivitet"):
                    slett_merkedag_id = m["id"]

        if slett_merkedag_id:
            data["merkedager"] = [m for m in data["merkedager"] if m["id"] != slett_merkedag_id]
            lagre_naa()
            st.rerun()
    else:
        st.caption("Ingen aktiviteter lagt inn.")

    st.write("---")
    with st.form("form_ny_merkedag", clear_on_submit=True):
        st.markdown("##### ➕ Legg til aktivitet eller merkedag")
        m_tittel = st.text_input("Hva skal skje?", placeholder="f.eks. Dans, Fotballtrening, Bursdag")
        col_h, col_i = st.columns([0.6, 0.4])
        m_hvem = col_h.selectbox("Hvem gjelder det?", medlemmer + [FELLES_VALG])
        m_ikon = col_i.selectbox("Type:", ["🩰 Dans", "⚽ Sport/Fotball", "🎂 Bursdag", "🏊 Svømming", "🎒 Skole/SFO", "🦷 Tannlege/Lege", "✈️ Ferie/Tur", "📌 Annet"])
        
        m_dato_valg = st.date_input("Startdato:", min_value=idag_dato, value=idag_dato)
        col_gjenta, col_uker = st.columns([0.55, 0.45])
        m_gjenta = col_gjenta.checkbox("🔄 Gjenta ukentlig", value=False)
        m_antall_uker = col_uker.number_input("Antall uker:", min_value=2, max_value=40, value=10, disabled=not m_gjenta)
        
        if st.form_submit_button("Lagre i kalenderen 🗓️", use_container_width=True) and m_tittel.strip():
            antall_ganger = int(m_antall_uker) if m_gjenta else 1
            for uke_nr in range(antall_ganger):
                ny_dato = m_dato_valg + timedelta(weeks=uke_nr)
                data["merkedager"].append({
                    "id": str(uuid.uuid4()),
                    "tittel": m_tittel.strip(),
                    "dato": ny_dato.strftime("%Y-%m-%d"),
                    "ikon": m_ikon.split()[0],
                    "hvem": m_hvem
                })
            lagre_naa()
            msg = f"Lagt til {m_tittel} i {antall_ganger} uker fremover!" if m_gjenta else f"Lagt til {m_tittel}!"
            st.toast(msg)
            st.rerun()

# ----------------- OPPSLAGSTAVLE -----------------
with st.expander("📌 **Familiens Oppslagstavle**", expanded=False):
    beskjeder = data.get("beskjeder", [])
    slett_beskjed_id = None
    if beskjeder:
        for b in beskjeder:
            c_lapp, c_del = st.columns([0.82, 0.18])
            with c_lapp:
                st.markdown(
                    f"""
                    <div style="background-color: #78350F; border-left: 4px solid #F59E0B; padding: 8px 12px; border-radius: 6px; margin-bottom: 6px;">
                        <span style="font-size: 0.95rem; font-weight: 700; color: #FEF3C7;">{b['tekst']}</span><br>
                        <span style="font-size: 0.75rem; color: #FDE68A;">— {b.get('fra', 'Familien')} ({b.get('tid', '')})</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with c_del:
                if st.button("✕", key=f"del_b_{b['id']}", help="Fjern"):
                    slett_beskjed_id = b["id"]

        if slett_beskjed_id:
            data["beskjeder"] = [b for b in data["beskjeder"] if b["id"] != slett_beskjed_id]
            lagre_naa()
            st.rerun()
    else:
        st.caption("Ingen beskjeder akkurat nå.")

    with st.form("form_ny_beskjed", clear_on_submit=True):
        ny_beskjed_tekst = st.text_input("Ny beskjed / lapp:", placeholder="f.eks. Husk gymtøy i morgen!")
        c_fra, c_knapp = st.columns([0.6, 0.4])
        hvem_fra = c_fra.selectbox("Fra:", data.get("medlemmer", ["Mor", "Far"]))
        if c_knapp.form_submit_button("Heng opp 📌", use_container_width=True) and ny_beskjed_tekst.strip():
            tidspunkt = naa.strftime("%d.%m kl. %H:%M")
            data["beskjeder"].append({
                "id": str(uuid.uuid4()),
                "tekst": ny_beskjed_tekst.strip(),
                "fra": hvem_fra,
                "tid": tidspunkt
            })
            lagre_naa()
            st.rerun()

er_forelder = st.session_state["foreldremodus"]

fane_navn = ["⭐ Oppgaver", "🎁 Butikk & Mål", "📊 Stjernelogg", "🍽️ Middag & Fryser", "🛒 Handleliste", "🎲 Aktiviteter"]
if er_forelder: fane_navn.append("👨‍👩‍👧‍👦 Admin")

faner = st.tabs(fane_navn)
fane_oppgaver, fane_butikk, fane_statistikk, fane_middag, fane_handleliste, fane_aktiviteter = faner[0], faner[1], faner[2], faner[3], faner[4], faner[5]
fane_familie = faner[6] if er_forelder else None

# ----------------- FANE 1: OPPGAVER & GODKJENNING -----------------
with fane_oppgaver:
    oppgaver_oppdatert = False
    slett_id = None
    medlemmer = data.get("medlemmer", [])
    stjerne_brukere = data.get("stjerne_brukere", [])

    # 1. FORELDREGODKJENNING MED AUTOMATISK LOGGFØRING
    oppgaver_til_godkjenning = [o for o in data["oppgaver"] if o.get("status") == "venter"]
    
    if er_forelder and oppgaver_til_godkjenning:
        st.markdown(
            f"""
            <div style="background-color: #78350F; border: 2px solid #F59E0B; border-radius: 12px; padding: 12px; margin-bottom: 14px;">
                <h4 style="margin: 0; color: #FEF3C7; font-weight: 900;">🔔 {len(oppgaver_til_godkjenning)} oppgave(r) venter på foreldregodkjenning!</h4>
                <p style="margin: 2px 0 0 0; font-size: 0.85rem; color: #FDE68A; font-weight: 600;">Sjekk jobben og trykk «Godkjenn» for å gi stjerner.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        for v_oppg in list(oppgaver_til_godkjenning):
            v_id = v_oppg["id"]
            hvem = v_oppg["hvem"]
            stjerner = v_oppg.get("stjerner", 1)
            prof = hent_profil(hvem, medlemmer)

            col_v_tekst, col_v_godkjenn, col_v_avvis = st.columns([0.60, 0.25, 0.15])
            with col_v_tekst:
                st.markdown(
                    f"""
                    <div style="font-weight: 800; font-size: 1rem; color: #FFFFFF;">
                        {v_oppg.get('ikon', '✨')} {v_oppg['tekst']}
                    </div>
                    <div style="font-size: 0.8rem; color: #CBD5E1;">
                        Utført av: <b style="color: {prof['kant']};">{prof['ikon']} {hvem}</b> (+{stjerner} ⭐)
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with col_v_godkjenn:
                if st.button("Godkjenn 👍", key=f"appr_{v_id}", use_container_width=True):
                    v_oppg["status"] = "godkjent"
                    if hvem in stjerne_brukere:
                        data["poeng"][hvem] = data["poeng"].get(hvem, 0) + stjerner
                        data["uke_oppgaver_lost"] = data.get("uke_oppgaver_lost", 0) + 1
                        logg_stjerne_hendelse(hvem, "tjent", stjerner, v_oppg["tekst"])
                    elif hvem == FELLES_VALG:
                        hjelpere = v_oppg.get("fullfort_av", [])
                        if not hjelpere: hjelpere = medlemmer
                        stjerner_hver = max(1, round(stjerner / max(1, len(hjelpere))))
                        for h in hjelpere:
                            if h in stjerne_brukere:
                                data["poeng"][h] = data["poeng"].get(h, 0) + stjerner_hver
                                logg_stjerne_hendelse(h, "tjent", stjerner_hver, f"{v_oppg['tekst']} (Felles)")
                        data["uke_oppgaver_lost"] = data.get("uke_oppgaver_lost", 0) + 1
                    
                    lagre_naa()
                    st.balloons()
                    st.toast(f"🎉 Godkjent! +{stjerner} ⭐ til {hvem}!")
                    st.rerun()

            with col_v_avvis:
                if st.button("Avvis ↩️", key=f"revert_{v_id}", use_container_width=True, help="Sett tilbake til ugjort"):
                    v_oppg["status"] = "ugjort"
                    v_oppg["fullfort_av"] = None
                    lagre_naa()
                    st.toast("Oppgaven ble satt tilbake.")
                    st.rerun()
            st.divider()

    # 2. STJERNETAVLE
    if stjerne_brukere:
        st.markdown("#### 🌟 Familiens Stjernetavle")
        kolonner = st.columns(len(stjerne_brukere))
        
        for idx, person in enumerate(stjerne_brukere):
            antall_stjerner = int(data["poeng"].get(person, 0))
            prof = hent_profil(person, medlemmer)
            
            with kolonner[idx]:
                synlige = min(antall_stjerner, 8)
                stjerne_symboler = "⭐" * synlige if synlige > 0 else "<span style='opacity: 0.3;'>☆☆☆☆</span>"
                pluss_tekst = f" <span style='font-size: 0.8rem; font-weight: 800; color: #FFFFFF;'>(+{antall_stjerner - 8})</span>" if antall_stjerner > 8 else ""

                st.markdown(
                    f"""
                    <div style="background-color: {prof['bg']}; border: 3px solid {prof['kant']}; border-radius: 14px; 
                                padding: 12px; text-align: center; margin-bottom: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.3);">
                        <div style="font-size: 2.2rem; margin-bottom: -4px;">{prof['ikon']}</div>
                        <div style="font-size: 1.15rem; font-weight: 900; color: #FFFFFF;">{person}</div>
                        <div style="font-size: 1.9rem; font-weight: 900; color: #FCD34D; margin: 2px 0;">
                            {antall_stjerner} <span style="font-size: 1.3rem;">⭐</span>
                        </div>
                        <div style="font-size: 1rem; letter-spacing: 1px;">
                            {stjerne_symboler}{pluss_tekst}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    c_dag, c_uke = st.columns(2)
    with c_dag:
        if st.button("☀️ Nullstill rutiner (Manuell)", use_container_width=True):
            for o in data["oppgaver"]:
                if o.get("gjentakende", False):
                    o["status"] = "ugjort"
                    o["fullfort_av"] = None
            lagre_naa()
            st.toast("Daglige rutiner er klare for en ny dag! ☀️")
            st.rerun()
    with c_uke:
        if er_forelder:
            st.button("🗓️ Start ny uke (Nullstill diplom)", on_click=cb_start_ny_uke, use_container_width=True)
        else:
            st.caption("🔒 Ny uke krever PIN")

    st.write("")

    # 3. OPPGAVER MED BEHOLDTE METTEDE FARGER
    for person in medlemmer:
        prof = hent_profil(person, medlemmer)
        person_oppgaver = [o for o in data["oppgaver"] if o["hvem"] == person]
        ugjorte = [o for o in person_oppgaver if o.get("status") == "ugjort"]
        ventende = [o for o in person_oppgaver if o.get("status") == "venter"]
        
        status_tekst = f"({len(ugjorte)} igjen"
        if ventende: status_tekst += f", {len(ventende)} venter på sjekk ⏳"
        status_tekst += ")"
        if not ugjorte and not ventende and person_oppgaver:
            status_tekst = "(Alt er godkjent! 🎉)"

        with st.expander(f"{prof['ikon']} **{person}** — {status_tekst}", expanded=(len(ugjorte) > 0 or len(ventende) > 0)):
            if not person_oppgaver:
                st.caption("Ingen oppgaver lagt til.")
            
            for oppg in person_oppgaver:
                oppg_id = oppg["id"]
                st_status = oppg.get("status", "ugjort")
                stjerner = oppg.get("stjerner", 1)
                ikon = oppg.get("ikon", "✨")

                if st_status == "godkjent":
                    bg_kort = "#334155"
                    kant_kort = "#64748B"
                    tekst_farge = "#94A3B8"
                    tekst_dekor = "text-decoration: line-through;"
                    status_badge = "✅ Godkjent"
                    badge_bg = "#1E293B"
                    badge_farge = "#6EE7B7"
                elif st_status == "venter":
                    bg_kort = "#78350F"
                    kant_kort = "#F59E0B"
                    tekst_farge = "#FEF3C7"
                    tekst_dekor = "font-weight: 800;"
                    status_badge = "⏳ Venter på sjekk"
                    badge_bg = "#451A03"
                    badge_farge = "#FCD34D"
                else:
                    bg_kort = prof["bg"]
                    kant_kort = prof["kant"]
                    tekst_farge = "#FFFFFF"
                    tekst_dekor = "font-weight: 800;"
                    status_badge = f"+{stjerner} ⭐"
                    badge_bg = prof["badge"]
                    badge_farge = "#FFFFFF"

                st.markdown(
                    f"""
                    <div style="background-color: {bg_kort}; border: 2px solid {kant_kort}; border-left: 8px solid {kant_kort}; border-radius: 12px; padding: 12px 14px; margin-bottom: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.25);">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 1.15rem; color: {tekst_farge}; {tekst_dekor}">
                                <span style="font-size: 1.4rem; margin-right: 6px;">{ikon}</span> {oppg['tekst']}
                            </span>
                            <span style="background-color: {badge_bg}; color: {badge_farge}; border: 1.5px solid {kant_kort}; padding: 3px 9px; border-radius: 10px; font-size: 0.8rem; font-weight: 800;">
                                {status_badge}
                            </span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                c_btn_utfør, c_btn_slett = st.columns([0.84, 0.16])
                with c_btn_utfør:
                    if st_status == "ugjort":
                        if st.button(f"Jeg har gjort dette! 🎉", key=f"btn_done_{oppg_id}", use_container_width=True):
                            oppg["status"] = "venter"
                            lagre_naa()
                            st.toast("Supert! Rop på mor eller far så de kan godkjenne! 👏")
                            st.rerun()
                    elif st_status == "venter":
                        st.caption("⏳ Oppgaven venter på at en voksen trykker godkjenn i foreldremodus.")
                    else:
                        st.caption("✨ Fullført for i dag!")

                with c_btn_slett:
                    if er_forelder:
                        if st.button("✕", key=f"del_op_{oppg_id}", help="Slett oppgave"):
                            slett_id = oppg_id

    # 4. FELLESEOPPGAVER
    felles_oppgaver = [o for o in data["oppgaver"] if o["hvem"] == FELLES_VALG]
    if felles_oppgaver:
        prof_felles = hent_profil(FELLES_VALG, medlemmer)
        with st.expander(f"🤝 **Fellesoppgaver** ({len(felles_oppgaver)})", expanded=True):
            for oppg in felles_oppgaver:
                oppg_id = oppg["id"]
                st_status = oppg.get("status", "ugjort")
                tot_stjerner = oppg.get("stjerner", 2)
                ikon = oppg.get("ikon", "🤝")

                if st_status == "godkjent":
                    bg_kort, kant_kort = "#334155", "#64748B"
                    t_farge = "#94A3B8"
                    t_dekor = "text-decoration: line-through;"
                elif st_status == "venter":
                    bg_kort, kant_kort = "#78350F", "#F59E0B"
                    t_farge = "#FEF3C7"
                    t_dekor = "font-weight: 800;"
                else:
                    bg_kort, kant_kort = prof_felles["bg"], prof_felles["kant"]
                    t_farge = "#FFFFFF"
                    t_dekor = "font-weight: 800;"

                st.markdown(
                    f"""
                    <div style="background-color: {bg_kort}; border: 2px solid {kant_kort}; border-left: 8px solid {kant_kort}; border-radius: 12px; padding: 12px 14px; margin-bottom: 8px;">
                        <span style="font-size: 1.15rem; color: {t_farge}; {t_dekor}">
                            <span style="font-size: 1.4rem; margin-right: 6px;">{ikon}</span> {oppg['tekst']}
                        </span>
                        <span style="font-size: 0.85rem; font-weight: 700; color: #FCD34D; margin-left: 8px;">
                            (+{tot_stjerner} ⭐ deles)
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if st_status == "ugjort":
                    c_f_who, c_f_btn = st.columns([0.65, 0.35])
                    valgte_hjelpere = c_f_who.multiselect(
                        "Hvem hjalp til?",
                        options=medlemmer,
                        default=[medlemmer[0]] if medlemmer else [],
                        key=f"f_who_{oppg_id}"
                    )
                    if c_f_btn.button("Meld inn! 🎉", key=f"f_done_{oppg_id}", use_container_width=True):
                        oppg["status"] = "venter"
                        oppg["fullfort_av"] = valgte_hjelpere
                        lagre_naa()
                        st.toast("Fellesoppgave meldt inn til godkjenning! 👏")
                        st.rerun()
                elif st_status == "venter":
                    hjelpere_str = ", ".join(oppg.get("fullfort_av", []))
                    st.info(f"⏳ Venter på foreldregodkjenning. (Hjelpere meldt inn: {hjelpere_str})")
                else:
                    st.caption("✨ Godkjent og stjerner er utdelt!")

                if er_forelder and st.button("Slett fellesoppgave ✕", key=f"f_del_{oppg_id}"):
                    slett_id = oppg_id

    if slett_id:
        data["oppgaver"] = [o for o in data["oppgaver"] if o["id"] != slett_id]
        lagre_naa()
        st.rerun()

    # 5. FORELDRE: LEGG TIL NY OPPGAVE
    if er_forelder:
        st.write("---")
        with st.expander("➕ **Legg til ny oppgave (for voksne)**"):
            with st.form("form_ny_oppg", clear_on_submit=True):
                col_t, col_ik = st.columns([0.75, 0.25])
                oppg_tekst = col_t.text_input("Gjøremål:", placeholder="f.eks. Pusse tenner, Re opp sengen")
                oppg_ikon = col_ik.selectbox("Ikon:", ["🪥", "🛏️", "🧸", "👟", "🍽️", "🎒", "🐶", "🧺", "📚", "🚿", "✨"])
                
                valgte = st.multiselect("Til hvem?", [FELLES_VALG] + medlemmer, default=[medlemmer[0]] if medlemmer else [])
                stjerner = st.number_input("Stjerner belønning:", min_value=1, max_value=20, value=1)
                er_daglig = st.checkbox("🔄 Daglig rutine (nullstilles hver natt)", value=True)
                
                if st.form_submit_button("Lagre oppgave", use_container_width=True) and oppg_tekst.strip() and valgte:
                    for p in valgte:
                        data["oppgaver"].append({
                            "id": str(uuid.uuid4()),
                            "ikon": oppg_ikon,
                            "tekst": oppg_tekst.strip(),
                            "hvem": p,
                            "status": "ugjort",
                            "stjerner": int(stjerner),
                            "fullfort_av": None,
                            "gjentakende": er_daglig
                        })
                    lagre_naa()
                    st.toast("Oppgave lagret!")
                    st.rerun()

# ----------------- FANE 2: BUTIKK & SPAREMÅL -----------------
with fane_butikk:
    st.subheader("🎯 Barnas Sparemål")
    stjerne_brukere = data.get("stjerne_brukere", [])

    if stjerne_brukere:
        for p in stjerne_brukere:
            saldo = data["poeng"].get(p, 0)
            maal_info = data.get("sparemaal", {}).get(p)
            prof = hent_profil(p, medlemmer)
            
            with st.container():
                if maal_info:
                    maal_tittel = maal_info.get("tittel", "Mål")
                    maal_pris = max(1, int(maal_info.get("pris", 10)))
                    framgang = min(1.0, saldo / maal_pris)
                    prosent = int(framgang * 100)
                    
                    st.markdown(f"**{prof['ikon']} {p} sparer til: {maal_tittel}** (`{saldo} / {maal_pris} ⭐` — {prosent}%)")
                    st.progress(framgang)
                    
                    c_m1, c_m2 = st.columns([0.65, 0.35])
                    with c_m1:
                        if saldo >= maal_pris:
                            st.success(f"🎉 Målet er nådd! {p} kan løse det inn!")
                        else:
                            st.caption(f"Mangler {maal_pris - saldo} ⭐ før målet nås.")
                    with c_m2:
                        if st.button("Fjern mål ✕", key=f"slett_maal_{p}"):
                            del data["sparemaal"][p]
                            lagre_naa()
                            st.rerun()
                else:
                    st.info(f"{prof['ikon']} {p} har ikke satt noe sparemål enda.")
                    with st.expander(f"➕ Sett sparemål for {p}"):
                        with st.form(f"form_maal_{p}"):
                            ny_m_tittel = st.text_input("Hva sparer du til?", placeholder="f.eks. Lego-sett, Tur til badeland")
                            ny_m_pris = st.number_input("Hvor mange stjerner koster det?", min_value=1, max_value=200, value=25)
                            if st.form_submit_button("Start sparing! 🚀") and ny_m_tittel.strip():
                                if "sparemaal" not in data: data["sparemaal"] = {}
                                data["sparemaal"][p] = {"tittel": ny_m_tittel.strip(), "pris": int(ny_m_pris)}
                                lagre_naa()
                                st.rerun()
                st.write("")

    st.write("---")
    st.subheader("🎁 Belønningsbutikk")
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
                logg_stjerne_hendelse(hvem_kjoper, "brukt", bel["pris"], bel["tittel"])
                lagre_naa()
                st.balloons()
                st.toast(f"🎉 Gratulerer {hvem_kjoper}!")
                st.rerun()

        if er_forelder and st.button("Slett premie ✕", key=f"del_bel_{bel['id']}"):
            slett_belonning_id = bel["id"]
        st.divider()

    if slett_belonning_id:
        data["belonninger"] = [b for b in data["belonninger"] if b["id"] != slett_belonning_id]
        lagre_naa()
        st.rerun()

    if er_forelder:
        with st.expander("➕ **Legg til ny premie**"):
            with st.form("form_ny_premie", clear_on_submit=True):
                b_tittel = st.text_input("Premienavn:")
                b_pris = st.number_input("Pris i stjerner:", min_value=1, max_value=100, value=5)
                if st.form_submit_button("Lagre premie", use_container_width=True) and b_tittel.strip():
                    data["belonninger"].append({"id": str(uuid.uuid4()), "tittel": b_tittel.strip(), "pris": int(b_pris)})
                    lagre_naa()
                    st.rerun()

# ----------------- FANE 3: STJERNELOGG & MÅNEDSSTATISTIKK -----------------
with fane_statistikk:
    st.subheader("📊 Månedlig Stjernelogg & Statistikk")
    st.caption("Følg med på familiens innsats og se om dere er i god flyt måned for måned!")

    logg = data.get("stjerne_logg", [])
    stjerne_brukere = data.get("stjerne_brukere", [])

    # Beregn nåværende måned og forrige måned
    denne_mnd_key = idag_dato.strftime("%Y-%m")
    
    # Finn forrige måneds nøkkel (håndterer også årsskifte)
    forste_denne_mnd = idag_dato.replace(day=1)
    siste_forrige_mnd = forste_denne_mnd - timedelta(days=1)
    forrige_mnd_key = siste_forrige_mnd.strftime("%Y-%m")

    denne_mnd_navn = MAANEDER[idag_dato.month - 1].capitalize()
    forrige_mnd_navn = MAANEDER[siste_forrige_mnd.month - 1].capitalize()

    # Beregn totaler
    tjent_denne = sum(x["antall"] for x in logg if x.get("aar_mnd") == denne_mnd_key and x.get("type") == "tjent")
    brukt_denne = sum(x["antall"] for x in logg if x.get("aar_mnd") == denne_mnd_key and x.get("type") == "brukt")

    tjent_forrige = sum(x["antall"] for x in logg if x.get("aar_mnd") == forrige_mnd_key and x.get("type") == "tjent")
    brukt_forrige = sum(x["antall"] for x in logg if x.get("aar_mnd") == forrige_mnd_key and x.get("type") == "brukt")

    # Sammenligningskort
    diff_tjent = tjent_denne - tjent_forrige
    if tjent_forrige == 0 and tjent_denne > 0:
        trend_tekst = f"🚀 Flott start på {denne_mnd_navn}! Familien har allerede tjent **{tjent_denne} ⭐**!"
        trend_farge = "#10B981"
    elif diff_tjent > 0:
        trend_tekst = f"🔥 Fantastisk innsats! Dere har tjent **+{diff_tjent} flere ⭐** i {denne_mnd_navn} enn i {forrige_mnd_navn}!"
        trend_farge = "#10B981"
    elif diff_tjent == 0:
        trend_tekst = f"⚖️ Familien holder jevnt og stødig tempo likt som i {forrige_mnd_navn}!"
        trend_farge = "#3B82F6"
    else:
        trend_tekst = f"💪 Dere ligger {abs(diff_tjent)} ⭐ bak fjorårets/forrige måneds nivå ({forrige_mnd_navn}). Klarer dere å ta det igjen?"
        trend_farge = "#F59E0B"

    st.markdown(
        f"""
        <div style="background-color: #1E293B; border-left: 6px solid {trend_farge}; border-radius: 12px; padding: 14px; margin-bottom: 16px;">
            <div style="font-size: 1.05rem; font-weight: 800; color: #FFFFFF; margin-bottom: 4px;">{trend_tekst}</div>
            <div style="font-size: 0.85rem; color: #94A3B8;">
                {denne_mnd_navn}: <b>{tjent_denne} ⭐ tjent</b> ({brukt_denne} brukt) &nbsp;|&nbsp; 
                {forrige_mnd_navn}: <b>{tjent_forrige} ⭐ tjent</b> ({brukt_forrige} brukt)
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Statistikk fordelt per barn denne måneden
    if stjerne_brukere:
        st.markdown(f"##### 👤 Barnas innsats i {denne_mnd_navn}")
        kols = st.columns(len(stjerne_brukere))
        for idx, person in enumerate(stjerne_brukere):
            prof = hent_profil(person, medlemmer)
            p_tjent = sum(x["antall"] for x in logg if x.get("aar_mnd") == denne_mnd_key and x.get("type") == "tjent" and x.get("person") == person)
            p_brukt = sum(x["antall"] for x in logg if x.get("aar_mnd") == denne_mnd_key and x.get("type") == "brukt" and x.get("person") == person)

            with kols[idx]:
                st.markdown(
                    f"""
                    <div style="background-color: {prof['bg']}; border: 2px solid {prof['kant']}; border-radius: 12px; padding: 10px; text-align: center;">
                        <div style="font-size: 1.5rem;">{prof['ikon']}</div>
                        <div style="font-size: 1.05rem; font-weight: 900; color: #FFFFFF;">{person}</div>
                        <div style="font-size: 1.3rem; font-weight: 900; color: #FCD34D; margin: 4px 0;">+{p_tjent} ⭐</div>
                        <div style="font-size: 0.75rem; color: #E2E8F0;">Brukt: {p_brukt} ⭐</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    st.write("---")

    # Siste hendelser i loggen
    st.markdown("##### 📜 Siste stjerneaktiviteter")
    if logg:
        siste_hendelser = list(reversed(logg))[:15]
        for h in siste_hendelser:
            h_person = h.get("person", "Familien")
            prof = hent_profil(h_person, medlemmer)
            h_type = h.get("type", "tjent")
            h_antall = h.get("antall", 1)
            h_tekst = h.get("beskrivelse", "Gjøremål")
            h_tid = h.get("tid", "")

            if h_type == "tjent":
                symbol = f"+{h_antall} ⭐"
                farge_txt = "#34D399"
                badge_t = "TJENT"
            else:
                symbol = f"-{h_antall} ⭐"
                farge_txt = "#F87171"
                badge_t = "BRUKT"

            st.markdown(
                f"""
                <div style="display: flex; justify-content: space-between; align-items: center; background-color: #0F172A; border-left: 4px solid {prof['kant']}; border-radius: 8px; padding: 8px 12px; margin-bottom: 6px;">
                    <div>
                        <span style="font-weight: 800; color: #FFFFFF; font-size: 0.95rem;">{prof['ikon']} {h_person}:</span> 
                        <span style="color: #CBD5E1; font-size: 0.9rem;">{h_tekst}</span>
                        <div style="font-size: 0.7rem; color: #64748B;">🕒 {h_tid}</div>
                    </div>
                    <div style="text-align: right;">
                        <span style="font-size: 1.1rem; font-weight: 900; color: {farge_txt};">{symbol}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.info("Ingen stjerneaktiviteter er loggført enda. Når du godkjenner oppgaver eller barna løser inn premier, dukker loggen opp her! 🌟")

# ----------------- FANE 4: MIDDAG & FRYSER -----------------
with fane_middag:
    with st.expander("🧊 **Familiens Fryser & Matskap (Kutt matsvinn)**", expanded=False):
        fryser_varer = data.get("fryser", [])
        slett_f_id = None
        
        if fryser_varer:
            for fv in fryser_varer:
                c_fn, c_fknapp, c_fslett = st.columns([0.55, 0.30, 0.15])
                c_fn.markdown(f"📦 **{fv['navn']}**")
                
                if c_fknapp.button("Til middagsplan", key=f"fryser_bruk_{fv['id']}"):
                    data["middagsplan"][idag_navn] = fv["navn"]
                    st.session_state[f"rett_{idag_navn}"] = fv["navn"]
                    lagre_naa()
                    st.toast(f"Satt {fv['navn']} som middag i dag! 🍽️")
                    st.rerun()

                if c_fslett.button("✕", key=f"fryser_del_{fv['id']}"):
                    slett_f_id = fv["id"]

            if slett_f_id:
                data["fryser"] = [x for x in data["fryser"] if x["id"] != slett_f_id]
                lagre_naa()
                st.rerun()
        else:
            st.caption("Ingen varer registrert i fryseren.")

        st.write("---")
        with st.form("form_ny_fryser_vare", clear_on_submit=True):
            ny_f_tekst = st.text_input("Vare i fryser/matskap:", placeholder="f.eks. Kjøttkaker 2 pk, Laks 500g")
            if st.form_submit_button("Legg i fryseren 🧊", use_container_width=True) and ny_f_tekst.strip():
                data["fryser"].append({"id": str(uuid.uuid4()), "navn": ny_f_tekst.strip()})
                lagre_naa()
                st.rerun()

    st.write("---")
    oppskrifter = data.get("oppskrifter", STANDARD_MIDDAGER)
    oppskriftsliste = sorted(list(oppskrifter.keys()))

    c_m1, c_m2 = st.columns(2)
    with c_m1: st.button("✨ Auto-planlegg uken", on_click=cb_auto_planlegg, args=(oppskriftsliste,), use_container_width=True)
    with c_m2:
        if st.button("🛒 Middager til handleliste", use_container_width=True):
            lagt = 0
            for d in DAGER:
                rett = st.session_state.get(f"rett_{d}", "").strip()
                if rett in oppskrifter:
                    for i_navn in oppskrifter[rett].get("ingredienser", []):
                        if legg_til_vare_i_data(i_navn): lagt += 1
            lagre_naa()
            st.toast(f"{lagt} ingredienser lagt i handlelisten! 🛒")

    st.write("---")
    plan_oppdatert = False

    for dag in DAGER:
        er_idag = (dag == idag_navn)
        valgt_rett = st.session_state.get(f"rett_{dag}", "")
        tittel_dag = f"👉 **{dag} (I dag)**" if er_idag else f"📅 **{dag}**"
        
        with st.container():
            st.markdown(f"#### {tittel_dag}")
            if valgt_rett in oppskrifter and oppskrifter[valgt_rett].get("bilde"):
                st.image(oppskrifter[valgt_rett]["bilde"], use_container_width=True)
            
            c_r1, c_r2 = st.columns([0.82, 0.18])
            ny_rett = c_r1.text_input(
                f"Rett {dag}", 
                value=valgt_rett, 
                key=f"rett_{dag}", 
                placeholder="Hva skal dere spise?", 
                label_visibility="collapsed"
            )
            
            if ny_rett in oppskrifter and c_r2.button("🛒", key=f"kjop_dag_{dag}", help=f"Kjøp til {ny_rett}"):
                for i_navn in oppskrifter[ny_rett].get("ingredienser", []): legg_til_vare_i_data(i_navn)
                lagre_naa()
                st.toast(f"Ingredienser til {ny_rett} lagt til!")

            if ny_rett != data["middagsplan"].get(dag, ""):
                data["middagsplan"][dag] = ny_rett
                plan_oppdatert = True
            
            st.divider()

    if plan_oppdatert: lagre_naa()

    with st.expander("📖 **Familiens Bildekokebok (Velg middag)**", expanded=False):
        slett_oppskrift = None
        for tittel, info in sorted(oppskrifter.items()):
            ingr_liste = info.get("ingredienser", [])
            bilde_url = info.get("bilde")
            
            st.markdown(f"### 🍽️ {tittel}")
            if bilde_url: st.image(bilde_url, use_container_width=True)
            else: st.info("📷 Ingen bilde lagt til enda.")

            st.caption(f"Ingredienser: {', '.join(ingr_liste)}" if ingr_liste else "Ingen ingredienser lagt inn")
            
            c_d, c_s = st.columns([0.55, 0.45])
            valgt_dag = c_d.selectbox(f"Dag for {tittel}", DAGER, key=f"v_dag_{tittel}", label_visibility="collapsed")
            c_s.button("Sett på meny 📅", key=f"s_meny_{tittel}", on_click=cb_sett_middag, args=(valgt_dag, tittel), use_container_width=True)
            
            with st.expander(f"📸 Endre / Legg til bilde for {tittel}"):
                nytt_bilde_fil = st.file_uploader(f"Last opp eller knips bilde av {tittel}:", type=["png", "jpg", "jpeg"], key=f"file_{tittel}")
                if st.button("Lagre bilde 💾", key=f"btn_bilde_{tittel}") and nytt_bilde_fil:
                    b64 = bilde_til_base64(nytt_bilde_fil)
                    if b64:
                        oppskrifter[tittel]["bilde"] = b64
                        if lagre_naa():
                            st.toast(f"Bilde lagret for {tittel}!")
                            st.rerun()

            if er_forelder and st.button("Slett oppskrift ✕", key=f"del_op_{tittel}"):
                slett_oppskrift = tittel
            st.divider()

        if slett_oppskrift:
            del data["oppskrifter"][slett_oppskrift]
            lagre_naa()
            st.rerun()

        if er_forelder:
            with st.form("form_ny_oppskrift", clear_on_submit=True):
                st.markdown("##### ➕ Legg til en ny rett")
                ny_r = st.text_input("Navn på retten:")
                ny_i = st.text_area("Ingredienser (komma mellom hver):", placeholder="Laksefilet, Poteter, Gulrøtter")
                nytt_opp_bilde = st.file_uploader("Bilde av retten (valgfritt):", type=["png", "jpg", "jpeg"])
                
                if st.form_submit_button("Lagre oppgave", use_container_width=True) and ny_r.strip():
                    ingr_liste_ren = [x.strip() for x in ny_i.split(",") if x.strip()]
                    b64_str = bilde_til_base64(nytt_opp_bilde) if nytt_opp_bilde else None
                    data["oppskrifter"][ny_r.strip()] = {"ingredienser": ingr_liste_ren, "bilde": b64_str}
                    if lagre_naa():
                        st.toast(f"{ny_r.strip()} er lagt til!")
                        st.rerun()

# ----------------- FANE 5: HANDLELISTE -----------------
with fane_handleliste:
    st.subheader("🛒 Handleliste")

    basisvarer = data.get("basisvarer", STANDARD_BASISVARER)
    if basisvarer:
        st.caption("⚡ **Hurtigknapper for basisvarer:**")
        kol_per_rad = 3
        for start_idx in range(0, len(basisvarer), kol_per_rad):
            rad_varer = basisvarer[start_idx:start_idx + kol_per_rad]
            cols = st.columns(len(rad_varer))
            for c_idx, b_item in enumerate(rad_varer):
                b_label = b_item.get("label", b_item.get("navn", "Vare"))
                b_navn = b_item.get("navn", b_label)
                b_kat = b_item.get("kategori", gjett_kategori(b_navn))
                b_id = b_item.get("id", str(uuid.uuid4()))
                
                if cols[c_idx].button(f"+ {b_label}", key=f"quick_btn_{b_id}", use_container_width=True):
                    if legg_til_vare_i_data(b_navn, "", b_kat):
                        lagre_naa()
                        st.toast(f"Lagt til {b_navn}!")
                        st.rerun()
                    else:
                        st.toast(f"{b_navn} ligger allerede klar i listen! 👍")

    st.write("")

    with st.form("form_ny_vare", clear_on_submit=True):
        col_v, col_m = st.columns([0.65, 0.35])
        ny_v = col_v.text_input("Vare:", placeholder="f.eks. Kjøttdeig, Epler")
        ny_mengde = col_m.text_input("Mengde:", placeholder="f.eks. 2 pk, 1L")
        ny_kat = st.selectbox("Avdeling:", ["✨ Automatisk"] + AVDELINGER)
        
        if st.form_submit_button("Legg til vare", use_container_width=True) and ny_v.strip():
            k = None if ny_kat == "✨ Automatisk" else ny_kat
            if legg_til_vare_i_data(ny_v, ny_mengde, k):
                lagre_naa()
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
                varer_sortert = sorted(varer_i_avd, key=lambda x: 1 if x.get("kjopt", False) else 0)
                
                for v in varer_sortert:
                    v_id = v["id"]
                    er_kjopt = v.get("kjopt", False)
                    mengde_tekst = f" `({v['mengde']})`" if v.get("mengde") else ""
                    visningstekst = f"~~{v['navn']}{mengde_tekst}~~" if er_kjopt else f"**{v['navn']}**{mengde_tekst}"

                    ny_status = st.checkbox(visningstekst, value=er_kjopt, key=f"hl_chk_{v_id}")
                    if ny_status != er_kjopt:
                        v["kjopt"] = ny_status
                        handleliste_oppdatert = True

                st.write("")

        if handleliste_oppdatert:
            lagre_naa()
            st.rerun()

        st.divider()
        antall_kjopte = len([v for v in data["handleliste"] if v.get("kjopt", False)])
        if antall_kjopte > 0 and st.button(f"🧹 Fjern {antall_kjopte} avkryssede varer", use_container_width=True):
            data["handleliste"] = [v for v in data["handleliste"] if not v.get("kjopt", False)]
            lagre_naa()
            st.toast("Avkryssede varer er fjernet!")
            st.rerun()

        if st.button("🗑️ Tøm hele listen", use_container_width=True):
            data["handleliste"] = []
            lagre_naa()
            st.rerun()

# ----------------- FANE 6: AKTIVITETER -----------------
with fane_aktiviteter:
    st.subheader("🎲 Hva skal vi finne på?")
    st.caption("Trykk på knappen for å trekke en morsom idé til hva familien kan gjøre sammen!")

    aktiviteter = data.get("aktiviteter", STANDARD_AKTIVITETER)
    
    if st.button("🎰 Trekk en tilfeldig aktivitet!", use_container_width=True):
        if aktiviteter:
            valgt_akt = random.choice(aktiviteter)
            st.session_state["trukket_aktivitet"] = valgt_akt
            st.balloons()
        else:
            st.warning("Ingen aktiviteter på listen!")

    if "trukket_aktivitet" in st.session_state:
        st.markdown(
            f"""
            <div style="background-color: #064E3B; border: 2px solid #10B981; border-radius: 12px; padding: 18px; text-align: center; margin: 14px 0;">
                <div style="font-size: 1.1rem; color: #A7F3D0; font-weight: 800;">Dagens utvalgte aktivitet:</div>
                <div style="font-size: 1.45rem; font-weight: 900; color: #FFFFFF; margin-top: 6px;">
                    {st.session_state['trukket_aktivitet']}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("---")
    with st.expander("📝 Se og rediger aktivitetslisten"):
        slett_akt = None
        for a_tekst in aktiviteter:
            c_at, c_adel = st.columns([0.85, 0.15])
            c_at.write(a_tekst)
            if c_adel.button("✕", key=f"del_akt_{a_tekst}"):
                slett_akt = a_tekst
        
        if slett_akt:
            data["aktiviteter"].remove(slett_akt)
            lagre_naa()
            st.rerun()

        with st.form("form_ny_akt", clear_on_submit=True):
            ny_akt = st.text_input("Legg til en ny aktivitet:", placeholder="f.eks. Dra i svømmehallen")
            if st.form_submit_button("Legg til aktivitet", use_container_width=True) and ny_akt.strip():
                if ny_akt.strip() not in data["aktiviteter"]:
                    data["aktiviteter"].append(ny_akt.strip())
                    lagre_naa()
                    st.rerun()

# ----------------- FANE 7: ADMIN -----------------
if er_forelder and fane_familie:
    with fane_familie:
        st.subheader("👨‍👩‍👧‍👦 Familieadministrasjon")

        with st.expander("🏷️ **Endre navnet på Familiehuben**", expanded=False):
            with st.form("form_endre_fam_navn"):
                nytt_hub_navn = st.text_input("Nytt navn på huben:", value=aktiv_kode.capitalize())
                if st.form_submit_button("Lagre nytt familienavn", use_container_width=True):
                    if nytt_hub_navn.strip() and nytt_hub_navn.strip().lower() != aktiv_kode.lower():
                        suksess, melding = endre_familie_navn(aktiv_kode, nytt_hub_navn.strip())
                        if suksess:
                            ny_kode = nytt_hub_navn.strip().lower()
                            st.session_state["aktiv_familie"] = ny_kode
                            if "fam" in st.query_params:
                                st.query_params["fam"] = ny_kode
                            st.toast("Familienavnet er endret! 🎉")
                            st.rerun()
                        else:
                            st.error(melding)

        st.divider()

        st.markdown("#### 👤 Familiemedlemmer")
        for i, person in enumerate(list(data["medlemmer"])):
            prof = hent_profil(person, data["medlemmer"])
            st.markdown(f"**Person {i+1}: {prof['ikon']} {person}**")
            nytt_navn = st.text_input(f"Navn", value=person, key=f"adm_navn_{i}")
            er_stjernesamler = person in data.get("stjerne_brukere", [])
            skal_ha = st.checkbox("Samler stjerner ⭐", value=er_stjernesamler, key=f"adm_stj_{i}")

            if nytt_navn.strip() and nytt_navn.strip() != person:
                gammelt = person
                nytt = nytt_navn.strip()
                data["medlemmer"][i] = nytt
                if gammelt in data.get("stjerne_brukere", []): data["stjerne_brukere"] = [nytt if x == gammelt else x for x in data["stjerne_brukere"]]
                if gammelt in data.get("poeng", {}): data["poeng"][nytt] = data["poeng"].pop(gammelt)
                for o in data.get("oppgaver", []):
                    if o["hvem"] == gammelt: o["hvem"] = nytt
                lagre_naa()
                st.rerun()

            if skal_ha != er_stjernesamler:
                if skal_ha:
                    if person not in data["stjerne_brukere"]: data["stjerne_brukere"].append(person)
                    if person not in data["poeng"]: data["poeng"][person] = 0
                else:
                    if person in data["stjerne_brukere"]: data["stjerne_brukere"].remove(person)
                lagre_naa()
                st.rerun()

            if st.button(f"Fjern {person} ✕", key=f"adm_del_{i}") and len(data["medlemmer"]) > 1:
                data["medlemmer"].remove(person)
                if person in data.get("stjerne_brukere", []): data["stjerne_brukere"].remove(person)
                if person in data.get("poeng", {}): data["poeng"].pop(person)
                lagre_naa()
                st.rerun()
            st.write("")

        with st.form("form_nytt_medlem", clear_on_submit=True):
            f_n = st.text_input("Ny person:")
            f_s = st.checkbox("Samle stjerner?", value=True)
            if st.form_submit_button("Legg til person", use_container_width=True) and f_n.strip():
                if f_n.strip() not in data["medlemmer"]:
                    data["medlemmer"].append(f_n.strip())
                    if f_s:
                        data["stjerne_brukere"].append(f_n.strip())
                        data["poeng"][f_n.strip()] = 0
                    lagre_naa()
                    st.rerun()

        st.divider()

        st.markdown("#### ⚡ Administrer Hurtigknapper for basisvarer")
        basisvarer = data.get("basisvarer", STANDARD_BASISVARER)
        slett_b_id = None
        for b in basisvarer:
            c_b_navn, c_b_kat, c_b_slett = st.columns([0.45, 0.40, 0.15])
            c_b_navn.markdown(f"**{b.get('label', b.get('navn'))}**")
            c_b_kat.caption(f"{b.get('kategori')}")
            if c_b_slett.button("✕", key=f"del_b_{b['id']}", help=f"Slett {b.get('navn')}"):
                slett_b_id = b["id"]

        if slett_b_id:
            data["basisvarer"] = [x for x in data["basisvarer"] if x["id"] != slett_b_id]
            lagre_naa()
            st.toast("Hurtigknapp slettet!")
            st.rerun()

        st.write("")
        with st.expander("➕ **Legg til ny hurtigknapp**"):
            with st.form("form_ny_basisvare", clear_on_submit=True):
                col_i, col_n = st.columns([0.3, 0.7])
                ny_ikon = col_i.text_input("Ikon / Emoji:", value="🍎")
                ny_b_navn = col_n.text_input("Varenavn:", placeholder="f.eks. Epler, Juice, Havregrøt")
                ny_b_kat = st.selectbox("Avdeling:", ["✨ Automatisk"] + AVDELINGER)
                
                if st.form_submit_button("Lagre hurtigknapp", use_container_width=True) and ny_b_navn.strip():
                    renset_navn = ny_b_navn.strip()
                    valgt_kat = gjett_kategori(renset_navn) if ny_b_kat == "✨ Automatisk" else ny_b_kat
                    label_tekst = f"{ny_ikon.strip()} {renset_navn}" if ny_ikon.strip() else renset_navn
                    
                    if "basisvarer" not in data: data["basisvarer"] = list(STANDARD_BASISVARER)
                    data["basisvarer"].append({
                        "id": str(uuid.uuid4()), "label": label_tekst, "navn": renset_navn, "kategori": valgt_kat
                    })
                    lagre_naa()
                    st.toast(f"Lagt til hurtigknapp for {renset_navn}!")
                    st.rerun()

# ----------------- BUNN: SYSTEM / UTENFOR FORELDREMODUS -----------------
st.write("---")
c_b1, c_b2 = st.columns(2)
with c_b1:
    if st.session_state["foreldremodus"]:
        with st.expander("🔑 Endre familiens PIN-kode"):
            ny_pin = st.text_input("Ny 4-sifret PIN:", type="password", max_chars=8)
            if st.button("Lagre ny PIN") and ny_pin.strip():
                data["pin"] = ny_pin.strip()
                lagre_naa()
                if "key" in st.query_params:
                    st.query_params["key"] = ny_pin.strip()
                st.toast("PIN-kode er oppdatert! 🎉")
with c_b2:
    if st.button("🚪 Logg ut av familie", use_container_width=True):
        st.session_state["aktiv_familie"] = ""
        st.session_state["foreldremodus"] = False
        st.query_params.clear()
        st.rerun()