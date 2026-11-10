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
    {"id": "b7", "label": "🥤 Pepsi Max", "navn": "Pepsi Max", "kategori": "🥤 Drikkevarer"},
    {"id": "b8", "label": "🧃 Juice", "navn": "Juice", "kategori": "🥤 Drikkevarer"},
    {"id": "b9", "label": "🍫 Melkesjokolade", "navn": "Melkesjokolade", "kategori": "🍬 Godteri & Lørdagsgodt"},
    {"id": "b10", "label": "🍿 Popcorn", "navn": "Popcorn", "kategori": "🍬 Godteri & Lørdagsgodt"},
]

STANDARD_PAKKEMALER = {
    "🌲 Skogs- og fjæretur": [
        {"ikon": "🥾", "tekst": "Gode sko / støvler"},
        {"ikon": "🌧️", "tekst": "Vindtett jakke / regntøy"},
        {"ikon": "🧦", "tekst": "Ekstra sokker"},
        {"ikon": "🪵", "tekst": "Sitteunderlag"},
        {"ikon": "🍶", "tekst": "Vannflaske / termos med kakao"},
        {"ikon": "🥪", "tekst": "Matpakke & tur-snacks"}
    ],
    "🏊 Badeland / Svømming": [
        {"ikon": "🩲", "tekst": "Badetøy"},
        {"ikon": "🧖", "tekst": "Stort håndkle"},
        {"ikon": "🥽", "tekst": "Svømmebriller / armringer"},
        {"ikon": "🧼", "tekst": "Dusjsåpe & sjampo"},
        {"ikon": "🩴", "tekst": "Badesandaler"},
        {"ikon": "🧴", "tekst": "Bodylotion"}
    ],
    "🏕️ Helgetur / Hytte": [
        {"ikon": "🪥", "tekst": "Tannbørste & tannkrem"},
        {"ikon": "🧸", "tekst": "Kosebamse & favorittleke"},
        {"ikon": "👕", "tekst": "Skiftetøy (2 sett)"},
        {"ikon": "🧦", "tekst": "Ullsokker & undertøy"},
        {"ikon": "🌙", "tekst": "Pysjamas"},
        {"ikon": "🔌", "tekst": "Ladere & hodetelefoner"}
    ]
}

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
    "🥤 Drikkevarer": [
        "brus", "pepsi", "cola", "solo", "fanta", "sprite", "juice", "saft", 
        "farris", "bonaqua", "iste", "energidrikk", "redbull", "vann", "sjokolademelk", 
        "eplejuice", "appelsinjuice", "smoothie", "øl", "cider"
    ],
    "🍬 Godteri & Lørdagsgodt": [
        "godteri", "godt", "smågodt", "snop", "sjokolade", "chips", "potetgull", 
        "popcorn", "kjeks", "drops", "lakris", "seigmenn", "vingummi", "cheez doodle", 
        "sjokoladepose", "bamsemums", "freia", "nidar", "pastiller", "tyggegummi"
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
    "🥤 Drikkevarer",
    "🍬 Godteri & Lørdagsgodt",
    "📦 Annet / Diverse"
]

DAGER = ["Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag", "Lørdag", "Søndag"]
DAGER_KORT = ["Man", "Tir", "Ons", "Tor", "Fre", "Lør", "Søn"]
MAANEDER = [
    "januar", "februar", "mars", "april", "mai", "juni",
    "juli", "august", "september", "oktober", "november", "desember"
]
FELLES_VALG = "Felles (Mor & Far / Den som gjør det)"

FARGE_TEMALISTE = {
    "Blå": {"bg": "#1D4ED8", "kant": "#60A5FA", "badge": "#1E40AF"},
    "Rosa": {"bg": "#BE185D", "kant": "#F472B6", "badge": "#9D174D"},
    "Gul/Brun": {"bg": "#B45309", "kant": "#FBBF24", "badge": "#92400E"},
    "Grønn": {"bg": "#047857", "kant": "#34D399", "badge": "#065F46"},
    "Lilla": {"bg": "#6D28D9", "kant": "#A78BFA", "badge": "#5B21B6"},
    "Oransje": {"bg": "#C2410C", "kant": "#FB923C", "badge": "#9A3412"},
    "Grå": {"bg": "#334155", "kant": "#94A3B8", "badge": "#1E293B"}
}

MULIGE_FIGURER = [
    "🦁 Løve", "🐰 Kanin", "🐻 Bjørn", "🦊 Rev", "🐼 Panda", "🐯 Tiger",
    "🦄 Enhjørning", "🦖 Dinosaur", "🐶 Hund", "🐱 Katt", "🐵 Ape", "🐧 Pingvin",
    "🐉 Drage", "🦉 Ugle", "👨 Far", "👩 Mor", "🦸 Superhelt", "👑 Prinsesse",
    "🥷 Ninja", "🧙 Trollmann", "🧑‍🚀 Astronaut", "🏴‍☠️ Sjørøver", "⚽ Fotball",
    "🩰 Dans", "🎮 Gamer", "🎨 Kunstner", "🎸 Musiker"
]

def hent_profil(person, data_ref):
    if person == FELLES_VALG or person == "Felles":
        return {"bg": "#334155", "kant": "#94A3B8", "tekst": "#FFFFFF", "badge": "#1E293B", "ikon": "🤝"}
    
    person_innst = data_ref.get("person_profiler", {}).get(person, {})
    valgt_ikon = person_innst.get("ikon", "🦁")
    valgt_farge_navn = person_innst.get("farge", "Blå")
    farge_data = FARGE_TEMALISTE.get(valgt_farge_navn, FARGE_TEMALISTE["Blå"])
    
    return {
        "bg": farge_data["bg"],
        "kant": farge_data["kant"],
        "badge": farge_data["badge"],
        "tekst": "#FFFFFF",
        "ikon": valgt_ikon
    }

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
        bilde.save(buffer, format="JPEG", quality=65, optimize=True)
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

def migrer_fryser(gammel_liste):
    ny_liste = []
    for item in gammel_liste:
        if isinstance(item, dict):
            if "plassering" not in item:
                item["plassering"] = "fryser"
            ny_liste.append(item)
        elif isinstance(item, str):
            ny_liste.append({"id": str(uuid.uuid4()), "navn": item, "plassering": "fryser"})
    return ny_liste

def migrer_pakkeliste(gammel_pakkeliste):
    if not isinstance(gammel_pakkeliste, list):
        return []
    ny_liste = []
    for p in gammel_pakkeliste:
        if isinstance(p, dict):
            if "id" not in p: p["id"] = str(uuid.uuid4())
            if "ikon" not in p: p["ikon"] = "🎒"
            if "pakket" not in p: p["pakket"] = False
            if "til" not in p: p["til"] = "Felles"
            ny_liste.append(p)
    return ny_liste

STANDARD_MODULER = {
    "oppgaver": True,
    "butikk": True,
    "statistikk": True,
    "middag": True,
    "handleliste": True,
    "pakkeliste": True,
    "garderobe": True,
    "aktiviteter": True
}

def standard_data(valgt_pin="1234"):
    idag_str = datetime.now(TIDSSONE_NORGE).strftime("%Y-%m-%d")
    return {
        "pin": str(valgt_pin),
        "sist_nullstilt": idag_str,
        "uke_oppgaver_lost": 0,
        "medlemmer": ["Far", "Mor", "Barn 1", "Barn 2"],
        "stjerne_brukere": ["Barn 1", "Barn 2"],
        "person_profiler": {
            "Far": {"ikon": "👨", "farge": "Blå"},
            "Mor": {"ikon": "👩", "farge": "Rosa"},
            "Barn 1": {"ikon": "🦁", "farge": "Grønn"},
            "Barn 2": {"ikon": "🐰", "farge": "Gul/Brun"}
        },
        "moduler": STANDARD_MODULER,
        "felles_sparemaal": {
            "tittel": "Tur til Badeland 🏊",
            "pris": 60,
            "spart": 0
        },
        "garderobe": {},
        "poeng": {"Far": 0, "Mor": 0, "Barn 1": 0, "Barn 2": 0},
        "sparemaal": {},
        "pakkeliste": [],
        "aktiviteter": STANDARD_AKTIVITETER,
        "stjerne_logg": [],
        "fryser": [
            {"id": str(uuid.uuid4()), "navn": "Laksefilet (4 pk)", "plassering": "fryser"},
            {"id": str(uuid.uuid4()), "navn": "Kjøttdeig 400g", "plassering": "fryser"},
            {"id": str(uuid.uuid4()), "navn": "Pastasaus på glass", "plassering": "matskap"},
            {"id": str(uuid.uuid4()), "navn": "Hakkede tomater 2 bokser", "plassering": "matskap"}
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
if "basisvarer" not in raw_data: raw_data["basisvarer"] = list(STANDARD_BASISVARER)
if "sparemaal" not in raw_data: raw_data["sparemaal"] = {}
if "pakkeliste" not in raw_data: raw_data["pakkeliste"] = []
if "garderobe" not in raw_data: raw_data["garderobe"] = {}
if "aktiviteter" not in raw_data: raw_data["aktiviteter"] = STANDARD_AKTIVITETER
if "uke_oppgaver_lost" not in raw_data: raw_data["uke_oppgaver_lost"] = 0
if "stjerne_logg" not in raw_data: raw_data["stjerne_logg"] = []
if "person_profiler" not in raw_data: raw_data["person_profiler"] = {}
if "moduler" not in raw_data: raw_data["moduler"] = dict(STANDARD_MODULER)
if "felles_sparemaal" not in raw_data or not isinstance(raw_data["felles_sparemaal"], dict):
    raw_data["felles_sparemaal"] = {"tittel": "Tur til Badeland 🏊", "pris": 60, "spart": 0}

for mod_k, mod_v in STANDARD_MODULER.items():
    if mod_k not in raw_data["moduler"]:
        raw_data["moduler"][mod_k] = mod_v

raw_data["fryser"] = migrer_fryser(raw_data.get("fryser", []))
raw_data["pakkeliste"] = migrer_pakkeliste(raw_data.get("pakkeliste", []))
raw_data["oppgaver"] = migrer_oppgaver(raw_data.get("oppgaver", []))
raw_data["handleliste"] = migrer_handleliste(raw_data.get("handleliste", []))
raw_data["middagsplan"] = migrer_middagsplan(raw_data.get("middagsplan", {}))

for p, s_info in raw_data.get("sparemaal", {}).items():
    if isinstance(s_info, dict) and "spart" not in s_info:
        s_info["spart"] = 0

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

def cb_planlegg_fra_fryser(oppskrifter, fryser_varer):
    if not oppskrifter:
        return
    
    fryser_tekster = [f["navn"].lower() for f in fryser_varer]
    matcher = []
    andre_retter = []
    
    for rett_navn, info in oppskrifter.items():
        ingredienser = [i.lower() for i in info.get("ingredienser", [])]
        matchet = False
        
        for f_vare in fryser_tekster:
            ord_deler = [ord_ren for ord_ren in f_vare.split() if len(ord_ren) > 2]
            if any(ord_del in rett_navn.lower() for ord_del in ord_deler) or \
               any(any(ord_del in ingr for ord_del in ord_deler) for ingr in ingredienser):
                matcher.append(rett_navn)
                matchet = True
                break
        
        if not matchet:
            andre_retter.append(rett_navn)
            
    matcher = list(dict.fromkeys(matcher))
    random.shuffle(matcher)
    random.shuffle(andre_retter)
    
    valgt_meny = (matcher + andre_retter)[:7]
    while len(valgt_meny) < 7 and (matcher or andre_retter):
        valgt_meny.append(random.choice(matcher + andre_retter))
        
    for i, dag in enumerate(DAGER):
        if i < len(valgt_meny):
            ny_rett = valgt_meny[i]
            data["middagsplan"][dag] = ny_rett
            st.session_state[f"rett_{dag}"] = ny_rett
            
    lagre_naa()

def slett_vare_fra_fryser_ved_navn(rett_eller_ingrediens):
    tekst = rett_eller_ingrediens.lower()
    funnet_id = None
    funnet_navn = ""
    
    for f in data.get("fryser", []):
        f_navn = f["navn"].lower()
        ord_deler = [o for o in f_navn.split() if len(o) > 2]
        if f_navn in tekst or any(o in tekst for o in ord_deler):
            funnet_id = f["id"]
            funnet_navn = f["navn"]
            break
            
    if funnet_id:
        data["fryser"] = [x for x in data["fryser"] if x["id"] != funnet_id]
        lagre_naa()
        return True, funnet_navn
    return False, ""

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

# ----------------- TOPPSTRIPE -----------------
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
                        prof = hent_profil(h_hvem, data)
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
            prof = hent_profil(hvem, data)

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
moduler = data.get("moduler", STANDARD_MODULER)

# ----------------- DYNAMISKE FANER -----------------
faner_konfig = []
if moduler.get("oppgaver", True): faner_konfig.append(("oppgaver", "⭐ Oppgaver"))
if moduler.get("butikk", True): faner_konfig.append(("butikk", "🎁 Butikk & Mål"))
if moduler.get("statistikk", True): faner_konfig.append(("statistikk", "📊 Stjernelogg"))
if moduler.get("middag", True): faner_konfig.append(("middag", "🍽️ Middag & Fryser"))
if moduler.get("handleliste", True): faner_konfig.append(("handleliste", "🛒 Handleliste"))
if moduler.get("pakkeliste", True): faner_konfig.append(("pakkeliste", "🧳 Pakkeliste"))
if moduler.get("garderobe", True): faner_konfig.append(("garderobe", "👟 Garderobe"))
if moduler.get("aktiviteter", True): faner_konfig.append(("aktiviteter", "🎲 Aktiviteter"))
if er_forelder: faner_konfig.append(("admin", "👨‍👩‍👧‍👦 Admin"))

if not faner_konfig:
    faner_konfig.append(("admin", "👨‍👩‍👧‍👦 Admin"))

faner_objekter = st.tabs([t[1] for t in faner_konfig])
fane_map = {faner_konfig[i][0]: faner_objekter[i] for i in range(len(faner_konfig))}

# ----------------- FANE: OPPGAVER & GODKJENNING -----------------
if "oppgaver" in fane_map:
    with fane_map["oppgaver"]:
        oppgaver_oppdatert = False
        slett_id = None
        medlemmer = data.get("medlemmer", [])
        stjerne_brukere = data.get("stjerne_brukere", [])

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
                prof = hent_profil(hvem, data)

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

        if stjerne_brukere:
            st.markdown("#### 🌟 Familiens Stjernetavle")
            kolonner = st.columns(len(stjerne_brukere))
            
            for idx, person in enumerate(stjerne_brukere):
                antall_stjerner = int(data["poeng"].get(person, 0))
                prof = hent_profil(person, data)
                
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

        for person in medlemmer:
            prof = hent_profil(person, data)
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

        felles_oppgaver = [o for o in data["oppgaver"] if o["hvem"] == FELLES_VALG]
        if felles_oppgaver:
            prof_felles = hent_profil(FELLES_VALG, data)
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

# ----------------- FANE: BUTIKK & SPAREMÅL -----------------
if "butikk" in fane_map:
    with fane_map["butikk"]:
        st.subheader("🏆 Felles Familiemål")
        st.caption("Her kan hele familien spare sammen mot en felles opplevelse!")
        felles_m = data.get("felles_sparemaal", {"tittel": "Tur til Badeland 🏊", "pris": 60, "spart": 0})
        f_tittel = felles_m.get("tittel", "Felles mål")
        f_pris = max(1, int(felles_m.get("pris", 60)))
        f_spart = int(felles_m.get("spart", 0))
        f_framgang = min(1.0, f_spart / f_pris)
        f_prosent = int(f_framgang * 100)

        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #065F46 0%, #047857 100%); border: 2px solid #34D399; border-radius: 14px; padding: 14px; margin-bottom: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.3);">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: 900; font-size: 1.15rem; color: #FFFFFF;">
                        🌟 {f_tittel}
                    </span>
                    <span style="font-weight: 900; font-size: 1.1rem; color: #FCD34D;">
                        {f_spart} / {f_pris} ⭐ ({f_prosent}%)
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.progress(f_framgang)

        if f_spart >= f_pris:
            st.balloons()
            st.success(f"🎉 Gratulerer hele familien! Dere har nådd fellesmålet: {f_tittel}!")
            if er_forelder and st.button("Nullstill / Sett nytt fellesmål 🔄", key="reset_felles_m"):
                felles_m["spart"] = 0
                lagre_naa()
                st.rerun()
        else:
            st.write("Overfør stjerner fra en person til felleskrukka:")
            col_f_hvem, col_f_antall, col_f_btn = st.columns([0.45, 0.25, 0.30])
            stjerne_brukere = data.get("stjerne_brukere", [])
            with col_f_hvem:
                giver = st.selectbox("Hvem bidrar?", stjerne_brukere, key="giver_felles", label_visibility="collapsed")
            with col_f_antall:
                giver_saldo = data["poeng"].get(giver, 0) if giver else 0
                antall_gi = st.number_input("Antall ⭐", min_value=1, max_value=max(1, giver_saldo), value=min(giver_saldo, 1) if giver_saldo > 0 else 1, key="num_felles", label_visibility="collapsed")
            with col_f_btn:
                kan_gi = giver and giver_saldo >= antall_gi and giver_saldo > 0
                if st.button("Putt i krukka 🍯", disabled=not kan_gi, use_container_width=True, key="btn_gi_felles"):
                    data["poeng"][giver] -= antall_gi
                    felles_m["spart"] = f_spart + antall_gi
                    logg_stjerne_hendelse(giver, "brukt", antall_gi, f"Bidro til fellesmål ({f_tittel})")
                    lagre_naa()
                    st.toast(f"{giver} la {antall_gi} ⭐ i felleskrukka! 👏")
                    st.rerun()

        if er_forelder:
            with st.expander("⚙️ Endre fellesmålet (PIN-opplåst)"):
                with st.form("form_endre_fellesm"):
                    ny_f_tittel = st.text_input("Hva er fellesmålet?", value=f_tittel)
                    ny_f_pris = st.number_input("Målkrav i stjerner:", min_value=10, max_value=500, value=f_pris)
                    if st.form_submit_button("Oppdater fellesmål"):
                        felles_m["tittel"] = ny_f_tittel.strip()
                        felles_m["pris"] = int(ny_f_pris)
                        lagre_naa()
                        st.toast("Fellesmålet er oppdatert!")
                        st.rerun()

        st.write("---")

        st.subheader("🎯 Barnas Individuelle Sparemål")
        stjerne_brukere = data.get("stjerne_brukere", [])
        if stjerne_brukere:
            for p in stjerne_brukere:
                saldo = data["poeng"].get(p, 0)
                maal_info = data.get("sparemaal", {}).get(p)
                prof = hent_profil(p, data)
                
                with st.container():
                    if maal_info:
                        maal_tittel = maal_info.get("tittel", "Mål")
                        maal_pris = max(1, int(maal_info.get("pris", 10)))
                        spart_naa = int(maal_info.get("spart", 0))
                        framgang = min(1.0, spart_naa / maal_pris)
                        prosent = int(framgang * 100)
                        
                        st.markdown(
                            f"""
                            <div style="background-color: #1E293B; border-left: 5px solid {prof['kant']}; border-radius: 10px; padding: 12px 14px; margin-bottom: 8px;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="font-weight: 800; font-size: 1.05rem; color: #FFFFFF;">
                                        {prof['ikon']} {p} sparer til: <span style="color: #FCD34D;">{maal_tittel}</span>
                                    </span>
                                    <span style="font-weight: 800; font-size: 0.95rem; color: #34D399;">
                                        {spart_naa} / {maal_pris} ⭐ ({prosent}%)
                                    </span>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        st.progress(framgang)
                        
                        if spart_naa >= maal_pris:
                            st.success(f"🎉 Målet er nådd! {p} har spart opp hele beløpet og kan hente premien sin!")
                            c_in1, c_in2 = st.columns([0.65, 0.35])
                            with c_in1:
                                if st.button(f"🎁 Løs inn {maal_tittel}! 🎉", key=f"innlos_maal_{p}", use_container_width=True):
                                    logg_stjerne_hendelse(p, "brukt", spart_naa, f"Nådde sparemål: {maal_tittel}")
                                    del data["sparemaal"][p]
                                    lagre_naa()
                                    st.balloons()
                                    st.toast(f"🎉 Gratulerer {p}! Du nådde målet ditt!")
                                    st.rerun()
                            with c_in2:
                                if st.button("Fjern mål ✕", key=f"slett_fullt_maal_{p}", help="Slett og behold stjernene"):
                                    data["poeng"][p] = data["poeng"].get(p, 0) + spart_naa
                                    del data["sparemaal"][p]
                                    lagre_naa()
                                    st.rerun()
                        else:
                            mangler = maal_pris - spart_naa
                            c_spar1, c_spar2, c_angre = st.columns([0.35, 0.35, 0.30])
                            
                            with c_spar1:
                                kan_spare_1 = saldo >= 1
                                if st.button(f"+1 ⭐ i sparebøssa", key=f"spar_1_{p}", disabled=not kan_spare_1, use_container_width=True):
                                    data["poeng"][p] -= 1
                                    maal_info["spart"] = spart_naa + 1
                                    logg_stjerne_hendelse(p, "brukt", 1, f"Låst i sparemål ({maal_tittel})")
                                    lagre_naa()
                                    st.toast(f"Puttet 1 ⭐ i sparebøssa for {p}!")
                                    st.rerun()

                            with c_spar2:
                                innskudd_5 = min(5, saldo, mangler)
                                kan_spare_flere = innskudd_5 > 1
                                tekst_flere = f"+{innskudd_5} ⭐ i sparebøssa" if kan_spare_flere else "+5 ⭐ i sparebøssa"
                                if st.button(tekst_flere, key=f"spar_flere_{p}", disabled=not kan_spare_flere, use_container_width=True):
                                    data["poeng"][p] -= innskudd_5
                                    maal_info["spart"] = spart_naa + innskudd_5
                                    logg_stjerne_hendelse(p, "brukt", innskudd_5, f"Låst i sparemål ({maal_tittel})")
                                    lagre_naa()
                                    st.toast(f"Puttet {innskudd_5} ⭐ i sparebøssa for {p}!")
                                    st.rerun()

                            with c_angre:
                                if st.button("Avbryt / Hent ut ✕", key=f"slett_maal_{p}", help="Avbryt sparemål og overfør låste stjerner tilbake til saldo"):
                                    data["poeng"][p] = data["poeng"].get(p, 0) + spart_naa
                                    if spart_naa > 0:
                                        logg_stjerne_hendelse(p, "tjent", spart_naa, f"Hentet ut fra avbrutt sparemål ({maal_tittel})")
                                    del data["sparemaal"][p]
                                    lagre_naa()
                                    st.toast(f"Sparemålet ble avbrutt. {spart_naa} ⭐ er tilbakeført til {p} sin saldo.")
                                    st.rerun()

                            st.caption(f"💡 {p} har **{saldo} ⭐** tilgjengelig. Mangler **{mangler} ⭐** for å nå målet.")
                    else:
                        st.info(f"{prof['ikon']} {p} har ikke satt noe sparemål enda.")
                        with st.expander(f"➕ Sett sparemål for {p}"):
                            with st.form(f"form_maal_{p}"):
                                ny_m_tittel = st.text_input("Hva sparer du til?", placeholder="f.eks. Lego-sett, Tur til badeland")
                                ny_m_pris = st.number_input("Hvor mange stjerner koster det?", min_value=1, max_value=200, value=25)
                                if st.form_submit_button("Start sparing! 🚀") and ny_m_tittel.strip():
                                    if "sparemaal" not in data: data["sparemaal"] = {}
                                    data["sparemaal"][p] = {
                                        "tittel": ny_m_tittel.strip(),
                                        "pris": int(ny_m_pris),
                                        "spart": 0
                                    }
                                    lagre_naa()
                                    st.rerun()
                    st.write("")

        st.write("---")
        st.subheader("🎁 Belønningsbutikk")
        if stjerne_brukere:
            saldo_tekst = " | ".join([f"**{p}:** {data['poeng'].get(p, 0)} ⭐" for p in stjerne_brukere])
            st.info(f"💳 Ledig saldo: {saldo_tekst}")

        slett_belonning_id = None
        for bel in data.get("belonninger", []):
            st.markdown(f"### {bel['tittel']} — `{bel['pris']} ⭐`")
            c_k1, c_k2 = st.columns([0.65, 0.35])
            with c_k1:
                hvem_kjoper = st.selectbox("Kjøper:", stjerne_brukere, key=f"b_who_{bel['id']}", label_visibility="collapsed")
            with c_k2:
                har_rad = data["poeng"].get(hvem_kjoper, 0) >= bel["pris"] if hvem_kjoper else False
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

# ----------------- FANE: STJERNELOGG & MÅNEDSSTATISTIKK -----------------
if "statistikk" in fane_map:
    with fane_map["statistikk"]:
        st.subheader("📊 Månedlig Stjernelogg & Statistikk")
        st.caption("Følg med på familiens innsats og se om dere er i god flyt måned for måned!")

        logg = data.get("stjerne_logg", [])
        stjerne_brukere = data.get("stjerne_brukere", [])

        denne_mnd_key = idag_dato.strftime("%Y-%m")
        forste_denne_mnd = idag_dato.replace(day=1)
        siste_forrige_mnd = forste_denne_mnd - timedelta(days=1)
        forrige_mnd_key = siste_forrige_mnd.strftime("%Y-%m")

        denne_mnd_navn = MAANEDER[idag_dato.month - 1].capitalize()
        forrige_mnd_navn = MAANEDER[siste_forrige_mnd.month - 1].capitalize()

        tjent_denne = sum(x["antall"] for x in logg if x.get("aar_mnd") == denne_mnd_key and x.get("type") == "tjent")
        brukt_denne = sum(x["antall"] for x in logg if x.get("aar_mnd") == denne_mnd_key and x.get("type") == "brukt")

        tjent_forrige = sum(x["antall"] for x in logg if x.get("aar_mnd") == forrige_mnd_key and x.get("type") == "tjent")
        brukt_forrige = sum(x["antall"] for x in logg if x.get("aar_mnd") == forrige_mnd_key and x.get("type") == "brukt")

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
            trend_tekst = f"💪 Dere ligger {abs(diff_tjent)} ⭐ bak forrige måneds nivå ({forrige_mnd_navn}). Klarer dere å ta det igjen?"
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

        if stjerne_brukere:
            st.markdown(f"##### 👤 Barnas innsats i {denne_mnd_navn}")
            kols = st.columns(len(stjerne_brukere))
            for idx, person in enumerate(stjerne_brukere):
                prof = hent_profil(person, data)
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
        st.markdown("##### 📜 Siste stjerneaktiviteter")
        if logg:
            siste_hendelser = list(reversed(logg))[:15]
            for h in siste_hendelser:
                h_person = h.get("person", "Familien")
                prof = hent_profil(h_person, data)
                h_type = h.get("type", "tjent")
                h_antall = h.get("antall", 1)
                h_tekst = h.get("beskrivelse", "Gjøremål")
                h_tid = h.get("tid", "")

                if h_type == "tjent":
                    symbol = f"+{h_antall} ⭐"
                    farge_txt = "#34D399"
                else:
                    symbol = f"-{h_antall} ⭐"
                    farge_txt = "#F87171"

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

# ----------------- FANE: MIDDAG & FRYSER -----------------
if "middag" in fane_map:
    with fane_map["middag"]:
        with st.expander("🧊 **Familiens Fryser & Matskap (Kutt matsvinn)**", expanded=False):
            fryser_data = data.get("fryser", [])
            varer_fryser = [v for v in fryser_data if v.get("plassering", "fryser") == "fryser"]
            varer_matskap = [v for v in fryser_data if v.get("plassering") == "matskap"]
            
            slett_f_id = None
            col_fryser, col_matskap = st.columns(2)

            with col_fryser:
                st.markdown("##### 🧊 Fryser")
                if varer_fryser:
                    for fv in varer_fryser:
                        c_txt, c_btn, c_del = st.columns([0.64, 0.20, 0.16])
                        c_txt.markdown(f"<div style='padding-top: 5px; font-size: 0.88rem; font-weight: 700; color: #FFFFFF;'>📦 {fv['navn']}</div>", unsafe_allow_html=True)
                        if c_btn.button("🍽️", key=f"f_sett_{fv['id']}", help=f"Sett {fv['navn']} som middag i dag"):
                            data["middagsplan"][idag_navn] = fv["navn"]
                            st.session_state[f"rett_{idag_navn}"] = fv["navn"]
                            lagre_naa()
                            st.toast(f"Satt {fv['navn']} på menyen i dag!")
                            st.rerun()
                        if c_del.button("✕", key=f"f_slett_{fv['id']}", help="Slett"):
                            slett_f_id = fv["id"]
                else:
                    st.caption("Tomt i fryseren.")

            with col_matskap:
                st.markdown("##### 🥫 Matskap / Tørrvare")
                if varer_matskap:
                    for mv in varer_matskap:
                        c_txt, c_btn, c_del = st.columns([0.64, 0.20, 0.16])
                        c_txt.markdown(f"<div style='padding-top: 5px; font-size: 0.88rem; font-weight: 700; color: #FFFFFF;'>🥫 {mv['navn']}</div>", unsafe_allow_html=True)
                        if c_btn.button("🍽️", key=f"m_sett_{mv['id']}", help=f"Sett {mv['navn']} som middag i dag"):
                            data["middagsplan"][idag_navn] = mv["navn"]
                            st.session_state[f"rett_{idag_navn}"] = mv["navn"]
                            lagre_naa()
                            st.toast(f"Satt {mv['navn']} på menyen i dag!")
                            st.rerun()
                        if c_del.button("✕", key=f"m_slett_{mv['id']}", help="Slett"):
                            slett_f_id = mv["id"]
                else:
                    st.caption("Tomt i matskapet.")

            if slett_f_id:
                data["fryser"] = [x for x in data["fryser"] if x["id"] != slett_f_id]
                lagre_naa()
                st.rerun()

            st.write("---")
            with st.form("form_ny_lagret_vare", clear_on_submit=True):
                col_in_navn, col_in_plass, col_in_btn = st.columns([0.55, 0.28, 0.17])
                ny_f_tekst = col_in_navn.text_input("Ny vare:", placeholder="f.eks. Kjøttkaker 2 pk, Laks", label_visibility="collapsed")
                ny_f_sted = col_in_plass.selectbox("Hvor?", ["🧊 Fryser", "🥫 Matskap"], label_visibility="collapsed")
                
                if col_in_btn.form_submit_button("Legg til ➕", use_container_width=True) and ny_f_tekst.strip():
                    sted_kode = "fryser" if "Fryser" in ny_f_sted else "matskap"
                    data["fryser"].append({"id": str(uuid.uuid4()), "navn": ny_f_tekst.strip(), "plassering": sted_kode})
                    lagre_naa()
                    st.rerun()

        st.write("---")
        oppskrifter = data.get("oppskrifter", STANDARD_MIDDAGER)
        oppskriftsliste = sorted(list(oppskrifter.keys()))

        c_m1, c_m2, c_m3 = st.columns(3)
        with c_m1:
            st.button("✨ Auto-planlegg uken", on_click=cb_auto_planlegg, args=(oppskriftsliste,), use_container_width=True)
        with c_m2:
            st.button("🧊 Planlegg fra fryseren", on_click=cb_planlegg_fra_fryser, args=(oppskrifter, data.get("fryser", [])), use_container_width=True)
        with c_m3:
            if st.button("🛒 Til handleliste", use_container_width=True):
                lagt = 0
                for d in DAGER:
                    rett = st.session_state.get(f"rett_{d}", "").strip()
                    if rett in oppskrifter:
                        for i_navn in oppskrifter[rett].get("ingredienser", []):
                            if legg_til_vare_i_data(i_navn): lagt += 1
                lagre_naa()
                st.toast(f"{lagt} ingredienser lagt i handlelisten! 🛒")

        st.write("---")
        
        st.markdown("#### 📅 Ukens Middagsplan")
        
        dag_rader = [
            ["Mandag", "Tirsdag"],
            ["Onsdag", "Torsdag"],
            ["Fredag", "Lørdag"],
            ["Søndag"]
        ]
        
        plan_oppdatert = False

        for rad in dag_rader:
            kols = st.columns(len(rad))
            for idx, dag in enumerate(rad):
                with kols[idx]:
                    er_idag = (dag == idag_navn)
                    valgt_rett = st.session_state.get(f"rett_{dag}", "")
                    badge_idag = " <span style='background-color: #3B82F6; color: #FFFFFF; font-size: 0.68rem; padding: 1px 5px; border-radius: 5px; font-weight: 800;'>I DAG</span>" if er_idag else ""

                    if er_idag and valgt_rett.strip():
                        c_dag_navn, c_spist = st.columns([0.62, 0.38])
                        with c_dag_navn:
                            st.markdown(f"<div style='padding-top: 4px; font-weight: 800; font-size: 0.95rem; color: #FFFFFF;'>{dag}{badge_idag}</div>", unsafe_allow_html=True)
                        with c_spist:
                            if st.button("🍽️ Spist", key=f"spist_btn_{dag}", help="Marker som spist og stryk fra fryser/matskap", use_container_width=True):
                                slettet, slettet_navn = slett_vare_fra_fryser_ved_navn(valgt_rett)
                                if slettet:
                                    st.balloons()
                                    st.toast(f"🎉 '{slettet_navn}' er nå strøket fra fryser/matskap!")
                                else:
                                    st.toast(f"Middagen for {dag} er spist! 🍽️")
                    else:
                        st.markdown(f"<div style='padding-top: 4px; font-weight: 800; font-size: 0.95rem; color: #FFFFFF; margin-bottom: 2px;'>{dag}{badge_idag}</div>", unsafe_allow_html=True)

                    if valgt_rett in oppskrifter and oppskrifter[valgt_rett].get("bilde"):
                        st.markdown(
                            f"""
                            <div style="display: flex; justify-content: center; margin: 4px 0 6px 0;">
                                <div style="width: 110px; height: 80px; overflow: hidden; border-radius: 8px; border: 1px solid #334155; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">
                                    <img src="{oppskrifter[valgt_rett]['bilde']}" style="width: 100%; height: 100%; object-fit: cover; display: block;" />
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    c_inn, c_kjop = st.columns([0.80, 0.20])
                    ny_rett = c_inn.text_input(
                        f"Rett {dag}", 
                        value=valgt_rett, 
                        key=f"rett_{dag}", 
                        placeholder="Middag...", 
                        label_visibility="collapsed"
                    )
                    
                    har_tekst = bool(ny_rett.strip())
                    if c_kjop.button("🛒", key=f"kjop_dag_{dag}", disabled=not har_tekst, help=f"Kjøp inn til {ny_rett}" if har_tekst else "Skriv inn middag først", use_container_width=True):
                        renset = ny_rett.strip()
                        if renset in oppskrifter and oppskrifter[renset].get("ingredienser"):
                            for i_navn in oppskrifter[renset]["ingredienser"]:
                                legg_til_vare_i_data(i_navn)
                            lagre_naa()
                            st.toast(f"Ingredienser til '{renset}' lagt til i handlelisten! 🛒")
                        else:
                            legg_til_vare_i_data(renset)
                            lagre_naa()
                            st.toast(f"'{renset}' lagt til i handlelisten! 🛒")

                    if ny_rett != data["middagsplan"].get(dag, ""):
                        data["middagsplan"][dag] = ny_rett
                        plan_oppdatert = True

        if plan_oppdatert: 
            lagre_naa()

        st.write("---")

        with st.expander("📖 **Familiens Bildekokebok (Velg middag)**", expanded=False):
            slett_oppskrift = None
            oppskrift_nokler = sorted(list(oppskrifter.keys()))
            
            for r_idx in range(0, len(oppskrift_nokler), 2):
                par = oppskrift_nokler[r_idx:r_idx + 2]
                cols_par = st.columns(len(par))
                
                for c_idx, tittel in enumerate(par):
                    info = oppskrifter[tittel]
                    ingr_liste = info.get("ingredienser", [])
                    bilde_url = info.get("bilde")

                    with cols_par[c_idx]:
                        st.markdown(
                            f"""
                            <div style="background-color: #1E293B; border: 1px solid #334155; border-radius: 10px; padding: 10px; margin-bottom: 8px;">
                                <div style="font-weight: 800; font-size: 1.05rem; color: #FFFFFF; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{tittel}">
                                    🍽️ {tittel}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                        if bilde_url:
                            st.markdown(
                                f"""
                                <div style="display: flex; justify-content: center; margin-bottom: 6px;">
                                    <div style="width: 140px; height: 100px; overflow: hidden; border-radius: 8px; border: 1px solid #334155; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">
                                        <img src="{bilde_url}" style="width: 100%; height: 100%; object-fit: cover; display: block;" />
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                        else:
                            st.markdown(
                                """
                                <div style="display: flex; justify-content: center; margin-bottom: 6px;">
                                    <div style="width: 140px; height: 60px; background-color: #0F172A; border: 1px dashed #334155; border-radius: 8px; display: flex; align-items: center; justify-content: center;">
                                        <span style="font-size: 0.72rem; color: #64748B;">📷 Ingen bilde</span>
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                        ingr_kort = ", ".join(ingr_liste[:4])
                        if len(ingr_liste) > 4:
                            ingr_kort += f" (+{len(ingr_liste)-4} til)"
                        st.caption(f"Ingredienser: {ingr_kort}" if ingr_liste else "Ingen ingredienser lagt inn")

                        c_dag_sel, c_sett_knapp = st.columns([0.55, 0.45])
                        valgt_dag = c_dag_sel.selectbox(f"Dag for {tittel}", DAGER, key=f"v_dag_{tittel}", label_visibility="collapsed")
                        c_sett_knapp.button("Sett på 📅", key=f"s_meny_{tittel}", on_click=cb_sett_middag, args=(valgt_dag, tittel), use_container_width=True)

                        with st.expander(f"⚙️ Rediger oppskrift / Bilde"):
                            st.markdown("**✏️ Endre ingredienser:**")
                            naavarende_ingr_str = ", ".join(ingr_liste)
                            ny_ingr_input = st.text_area(
                                "Ingredienser (komma mellom hver):",
                                value=naavarende_ingr_str,
                                key=f"edit_ingr_{tittel}",
                                help="Skriv ingrediensene adskilt med komma, f.eks: Kjøttdeig, Tacokrydder, Ost"
                            )
                            if st.button("Lagre ingredienser 💾", key=f"btn_save_ingr_{tittel}", use_container_width=True):
                                oppdaterte_ingr = [x.strip() for x in ny_ingr_input.split(",") if x.strip()]
                                oppskrifter[tittel]["ingredienser"] = oppdaterte_ingr
                                if lagre_naa():
                                    st.toast(f"Ingredienser for {tittel} er oppdatert! 🥗")
                                    st.rerun()

                            st.write("---")
                            st.markdown("**📸 Bytt bilde:**")
                            nytt_bilde_fil = st.file_uploader(f"Last opp bilde:", type=["png", "jpg", "jpeg"], key=f"file_{tittel}")
                            if st.button("Lagre bilde 💾", key=f"btn_bilde_{tittel}", use_container_width=True) and nytt_bilde_fil:
                                b64 = bilde_til_base64(nytt_bilde_fil)
                                if b64:
                                    oppskrifter[tittel]["bilde"] = b64
                                    if lagre_naa():
                                        st.toast(f"Bilde lagret for {tittel}!")
                                        st.rerun()

                            if er_forelder:
                                st.write("---")
                                if st.button("Slett rett ✕", key=f"del_op_{tittel}", use_container_width=True):
                                    slett_oppskrift = tittel
                st.write("")

            if slett_oppskrift:
                del data["oppskrifter"][slett_oppskrift]
                lagre_naa()
                st.rerun()

            if er_forelder:
                st.write("---")
                with st.form("form_ny_oppskrift", clear_on_submit=True):
                    st.markdown("##### ➕ Legg til en ny rett")
                    col_nr1, col_nr2 = st.columns([0.6, 0.4])
                    ny_r = col_nr1.text_input("Navn på retten:")
                    nytt_opp_bilde = col_nr2.file_uploader("Bilde (valgfritt):", type=["png", "jpg", "jpeg"])
                    ny_i = st.text_area("Ingredienser (komma mellom hver):", placeholder="Laksefilet, Poteter, Gulrøtter")
                    
                    if st.form_submit_button("Lagre oppgave", use_container_width=True) and ny_r.strip():
                        ingr_liste_ren = [x.strip() for x in ny_i.split(",") if x.strip()]
                        b64_str = bilde_til_base64(nytt_opp_bilde) if nytt_opp_bilde else None
                        data["oppskrifter"][ny_r.strip()] = {"ingredienser": ingr_liste_ren, "bilde": b64_str}
                        if lagre_naa():
                            st.toast(f"{ny_r.strip()} er lagt til!")
                            st.rerun()

# ----------------- FANE: HANDLELISTE -----------------
if "handleliste" in fane_map:
    with fane_map["handleliste"]:
        st.subheader("🛒 Handleliste")

        basisvarer = data.get("basisvarer", STANDARD_BASISVARER)
        if basisvarer:
            st.caption("⚡ **Hurtigknapper for basisvarer (inkl. brus & godteri):**")
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
            ny_v = col_v.text_input("Vare:", placeholder="f.eks. Pepsi Max, Melkesjokolade, Epler")
            ny_mengde = col_m.text_input("Mengde:", placeholder="f.eks. 4 pk, 1.5L, 2 poser")
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

# ----------------- FANE: PAKKELISTE -----------------
if "pakkeliste" in fane_map:
    with fane_map["pakkeliste"]:
        st.subheader("🧳 Smart Pakkeliste for tur & utflukter")
        st.caption("Gjør pakkingen til en lek! Barna kan krysse av tingene sine selv.")

        pakkeliste = data.get("pakkeliste", [])
        medlemmer = data.get("medlemmer", ["Far", "Mor", "Barn 1", "Barn 2"])

        with st.expander("⚡ **Hent inn en ferdig tur-pakkeliste**", expanded=(len(pakkeliste) == 0)):
            st.write("Velg en mal for å fylle listen automatisk:")
            col_m1, col_m2 = st.columns([0.65, 0.35])
            valgt_mal_navn = col_m1.selectbox("Velg tur-type:", list(STANDARD_PAKKEMALER.keys()), label_visibility="collapsed")
            hvem_pakker_mal = col_m2.selectbox("Til hvem?", ["Felles"] + medlemmer, label_visibility="collapsed")
            
            if st.button("Legg til malen i listen 🎒", use_container_width=True):
                items_mal = STANDARD_PAKKEMALER[valgt_mal_navn]
                for itm in items_mal:
                    pakkeliste.append({
                        "id": str(uuid.uuid4()),
                        "tekst": itm["tekst"],
                        "ikon": itm["ikon"],
                        "til": hvem_pakker_mal,
                        "pakket": False
                    })
                lagre_naa()
                st.toast(f"Lagt til pakkeliste for {valgt_mal_navn}!")
                st.rerun()

        st.write("---")

        with st.form("form_ny_pakke_ting", clear_on_submit=True):
            col_pi_tekst, col_pi_ikon, col_pi_til, col_pi_btn = st.columns([0.45, 0.20, 0.20, 0.15])
            p_tekst = col_pi_tekst.text_input("Hva skal pakkes?", placeholder="f.eks. Regnvotter, Hodelykt")
            p_ikon = col_pi_ikon.selectbox("Ikon:", ["🧸", "🥾", "🌧️", "🧦", "🪥", "🥪", "🍶", "👙", "🌙", "🎒", "🔋", "✨"])
            p_til = col_pi_til.selectbox("I sekken til:", ["Felles"] + medlemmer)
            
            if col_pi_btn.form_submit_button("Legg til", use_container_width=True) and p_tekst.strip():
                pakkeliste.append({
                    "id": str(uuid.uuid4()),
                    "tekst": p_tekst.strip(),
                    "ikon": p_ikon,
                    "til": p_til,
                    "pakket": False
                })
                lagre_naa()
                st.rerun()

        st.write("")

        grupper = ["Felles"] + [m for m in medlemmer if m != "Felles"]
        pakkeliste_oppdatert = False
        slett_pakk_id = None

        if not pakkeliste:
            st.info("Pakkelisten er tom! Velg en mal ovenfor eller legg til ting du vil ha med på tur.")
        else:
            tot_antall = len(pakkeliste)
            tot_pakket = len([p for p in pakkeliste if p.get("pakket", False)])
            total_framgang = tot_pakket / max(1, tot_antall)

            st.markdown(f"**Totalt pakket:** `{tot_pakket} / {tot_antall}` ting er i sekkene ({int(total_framgang * 100)}%)")
            st.progress(total_framgang)
            if tot_pakket == tot_antall and tot_antall > 0:
                st.balloons()
                st.success("🎉 Alt er pakket og klart! God tur!")

            st.write("")

            for grp in grupper:
                varer_i_grp = [p for p in pakkeliste if p.get("til", "Felles") == grp]
                if varer_i_grp:
                    prof = hent_profil(grp, data)
                    grp_pakket = len([p for p in varer_i_grp if p.get("pakket", False)])
                    grp_tot = len(varer_i_grp)
                    
                    with st.expander(f"{prof['ikon']} **{grp} sin sekk** ({grp_pakket}/{grp_tot})", expanded=(grp_pakket < grp_tot)):
                        for itm in varer_i_grp:
                            itm_id = itm["id"]
                            er_p = itm.get("pakket", False)
                            
                            col_chk, col_slett = st.columns([0.88, 0.12])
                            with col_chk:
                                etikett = f"~~{itm['ikon']} {itm['tekst']}~~" if er_p else f"**{itm['ikon']} {itm['tekst']}**"
                                ny_status = st.checkbox(etikett, value=er_p, key=f"chk_p_{itm_id}")
                                if ny_status != er_p:
                                    itm["pakket"] = ny_status
                                    pakkeliste_oppdatert = True
                            with col_slett:
                                if st.button("✕", key=f"del_p_{itm_id}", help="Fjern fra pakkelisten"):
                                    slett_pakk_id = itm_id

            if pakkeliste_oppdatert:
                lagre_naa()
                st.rerun()

            if slett_pakk_id:
                data["pakkeliste"] = [x for x in data["pakkeliste"] if x["id"] != slett_pakk_id]
                lagre_naa()
                st.rerun()

            st.divider()
            col_pk1, col_pk2 = st.columns(2)
            with col_pk1:
                if st.button("🔄 Nullstill avkryssing (Klar til ny tur)", use_container_width=True):
                    for p in data["pakkeliste"]:
                        p["pakket"] = False
                    lagre_naa()
                    st.toast("Avkryssinger nullstilt!")
                    st.rerun()
            with col_pk2:
                if st.button("🗑️ Tøm hele pakkelisten", use_container_width=True):
                    data["pakkeliste"] = []
                    lagre_naa()
                    st.toast("Pakkelisten er tømt!")
                    st.rerun()

# ----------------- FANE: GARDEROBE & KLESSTØRRELSER -----------------
if "garderobe" in fane_map:
    with fane_map["garderobe"]:
        st.subheader("👟 Barnas Garderobe & Klesstørrelser")
        st.caption("Aldri mer usikker i klesbutikken! Sjekk størrelser og hva som mangler i skuffen eller barnehagen.")

        medlemmer = data.get("medlemmer", [])
        stjerne_brukere = data.get("stjerne_brukere", [])
        garderobe = data.get("garderobe", {})

        if not stjerne_brukere:
            st.info("Ingen personer er satt opp som barn / stjernebrukere enda. Du kan definere dette under Admin.")
        else:
            for b_navn in stjerne_brukere:
                prof = hent_profil(b_navn, data)
                b_info = garderobe.get(b_navn, {
                    "sko": "28",
                    "klaer": "110/116",
                    "lue": "52",
                    "mangler": "Ekstra ullsokker, regnvotter"
                })

                with st.expander(f"{prof['ikon']} **{b_navn} sin garderobe**", expanded=True):
                    c_sko, c_klaer, c_lue = st.columns(3)
                    ny_sko = c_sko.text_input("Skostørrelse:", value=b_info.get("sko", ""), key=f"g_sko_{b_navn}")
                    ny_klaer = c_klaer.text_input("Klesstørrelse:", value=b_info.get("klaer", ""), key=f"g_klaer_{b_navn}")
                    ny_lue = c_lue.text_input("Luestr. / Hodeomkrets:", value=b_info.get("lue", ""), key=f"g_lue_{b_navn}")

                    ny_mangler = st.text_area(
                        "🎒 Mangler i kurven (barnehage/skole):",
                        value=b_info.get("mangler", ""),
                        key=f"g_mangler_{b_navn}",
                        placeholder="f.eks. Regnvotter, ekstra skift, gummistøvler..."
                    )

                    c_g_lagre, c_g_handle = st.columns([0.65, 0.35])
                    with c_g_lagre:
                        if st.button("Lagre størrelser 💾", key=f"btn_lagre_g_{b_navn}", use_container_width=True):
                            garderobe[b_navn] = {
                                "sko": ny_sko.strip(),
                                "klaer": ny_klaer.strip(),
                                "lue": ny_lue.strip(),
                                "mangler": ny_mangler.strip()
                            }
                            data["garderobe"] = garderobe
                            lagre_naa()
                            st.toast(f"Garderoben til {b_navn} er oppdatert!")
                            st.rerun()

                    with c_g_handle:
                        if ny_mangler.strip() and st.button("🛒 Send mangler til handleliste", key=f"btn_g_hl_{b_navn}", use_container_width=True):
                            ting_liste = [t.strip() for t in ny_mangler.replace("\n", ",").split(",") if t.strip()]
                            lagt_til = 0
                            for t in ting_liste:
                                if legg_til_vare_i_data(f"{t} ({b_navn})", "", "📦 Annet / Diverse"):
                                    lagt_til += 1
                            lagre_naa()
                            st.toast(f"Lagt til {lagt_til} ting i handlelisten!")

# ----------------- FANE: AKTIVITETER -----------------
if "aktiviteter" in fane_map:
    with fane_map["aktiviteter"]:
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

# ----------------- FANE: ADMIN -----------------
if "admin" in fane_map:
    with fane_map["admin"]:
        st.subheader("👨‍👩‍👧‍👦 Familieadministrasjon")

        with st.expander("🎛️ **Tilpass familiens moduler (Skjul/Vis funksjoner)**", expanded=False):
            st.caption("Slå av funksjoner dere ikke bruker for en renere app (f.eks. for par uten barn):")
            mod_oppg = st.checkbox("⭐ Oppgaver & Rutiner", value=moduler.get("oppgaver", True), key="mod_chk_oppg")
            mod_but = st.checkbox("🎁 Belønningsbutikk & Sparemål", value=moduler.get("butikk", True), key="mod_chk_but")
            mod_stat = st.checkbox("📊 Stjernelogg & Statistikk", value=moduler.get("statistikk", True), key="mod_chk_stat")
            mod_mid = st.checkbox("🍽️ Middagsplan & Fryser/Matskap", value=moduler.get("middag", True), key="mod_chk_mid")
            mod_han = st.checkbox("🛒 Handleliste", value=moduler.get("handleliste", True), key="mod_chk_han")
            mod_pak = st.checkbox("🧳 Smart Pakkeliste", value=moduler.get("pakkeliste", True), key="mod_chk_pak")
            mod_gard = st.checkbox("👟 Garderobe & Klesstørrelser", value=moduler.get("garderobe", True), key="mod_chk_gard")
            mod_akt = st.checkbox("🎲 Aktiviteter", value=moduler.get("aktiviteter", True), key="mod_chk_akt")

            if st.button("Lagre modulvalg 💾", use_container_width=True):
                data["moduler"] = {
                    "oppgaver": mod_oppg,
                    "butikk": mod_but,
                    "statistikk": mod_stat,
                    "middag": mod_mid,
                    "handleliste": mod_han,
                    "pakkeliste": mod_pak,
                    "garderobe": mod_gard,
                    "aktiviteter": mod_akt
                }
                lagre_naa()
                st.toast("Modulvalgene er lagret!")
                st.rerun()

        st.divider()

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

        st.markdown("#### 👤 Familiemedlemmer, Avatarer & Farger")
        if "person_profiler" not in data:
            data["person_profiler"] = {}

        for i, person in enumerate(list(data["medlemmer"])):
            pers_prof = data["person_profiler"].get(person, {})
            aktiv_fig = pers_prof.get("ikon", "🦁")
            aktiv_farge = pers_prof.get("farge", "Blå")
            
            st.markdown(f"**Person {i+1}:**")
            c_pnavn, c_pikon, c_pfarge = st.columns([0.45, 0.30, 0.25])
            
            nytt_navn = c_pnavn.text_input("Navn", value=person, key=f"adm_navn_{i}", label_visibility="collapsed")
            
            fig_idx = 0
            for f_idx, fig_str in enumerate(MULIGE_FIGURER):
                if aktiv_fig in fig_str:
                    fig_idx = f_idx
                    break
            ny_valgt_fig = c_pikon.selectbox("Figur:", MULIGE_FIGURER, index=fig_idx, key=f"adm_fig_{i}", label_visibility="collapsed")
            
            farge_navn_liste = list(FARGE_TEMALISTE.keys())
            farge_idx = farge_navn_liste.index(aktiv_farge) if aktiv_farge in farge_navn_liste else 0
            ny_valgt_farge = c_pfarge.selectbox("Farge:", farge_navn_liste, index=farge_idx, key=f"adm_farge_{i}", label_visibility="collapsed")

            bare_ikon = ny_valgt_fig.split()[0]
            if person not in data["person_profiler"]:
                data["person_profiler"][person] = {}
            if data["person_profiler"][person].get("ikon") != bare_ikon or data["person_profiler"][person].get("farge") != ny_valgt_farge:
                data["person_profiler"][person]["ikon"] = bare_ikon
                data["person_profiler"][person]["farge"] = ny_valgt_farge
                lagre_naa()
                st.rerun()

            er_stjernesamler = person in data.get("stjerne_brukere", [])
            col_stj_chk, col_slett_pers = st.columns([0.65, 0.35])
            with col_stj_chk:
                skal_ha = st.checkbox("Samler stjerner ⭐", value=er_stjernesamler, key=f"adm_stj_{i}")

            if nytt_navn.strip() and nytt_navn.strip() != person:
                gammelt = person
                nytt = nytt_navn.strip()
                data["medlemmer"][i] = nytt
                if gammelt in data.get("stjerne_brukere", []): data["stjerne_brukere"] = [nytt if x == gammelt else x for x in data["stjerne_brukere"]]
                if gammelt in data.get("poeng", {}): data["poeng"][nytt] = data["poeng"].pop(gammelt)
                if gammelt in data.get("person_profiler", {}): data["person_profiler"][nytt] = data["person_profiler"].pop(gammelt)
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

            with col_slett_pers:
                if st.button(f"Fjern {person} ✕", key=f"adm_del_{i}") and len(data["medlemmer"]) > 1:
                    data["medlemmer"].remove(person)
                    if person in data.get("stjerne_brukere", []): data["stjerne_brukere"].remove(person)
                    if person in data.get("poeng", {}): data["poeng"].pop(person)
                    if person in data.get("person_profiler", {}): data["person_profiler"].pop(person)
                    lagre_naa()
                    st.rerun()
            st.write("")

        with st.form("form_nytt_medlem", clear_on_submit=True):
            col_nm1, col_nm2, col_nm3 = st.columns([0.45, 0.30, 0.25])
            f_n = col_nm1.text_input("Ny person:", placeholder="Navn")
            f_fig = col_nm2.selectbox("Figur:", MULIGE_FIGURER)
            f_col = col_nm3.selectbox("Farge:", list(FARGE_TEMALISTE.keys()))
            f_s = st.checkbox("Samle stjerner?", value=True)
            
            if st.form_submit_button("Legg til person", use_container_width=True) and f_n.strip():
                if f_n.strip() not in data["medlemmer"]:
                    ny_p_navn = f_n.strip()
                    data["medlemmer"].append(ny_p_navn)
                    data["person_profiler"][ny_p_navn] = {
                        "ikon": f_fig.split()[0],
                        "farge": f_col
                    }
                    if f_s:
                        data["stjerne_brukere"].append(ny_p_navn)
                        data["poeng"][ny_p_navn] = 0
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