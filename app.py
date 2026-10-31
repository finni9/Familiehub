import streamlit as st
import json
import random
import uuid
import base64
import io
import pandas as pd
from datetime import datetime, date
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
MAANEDER = [
    "januar", "februar", "mars", "april", "mai", "juni",
    "juli", "august", "september", "oktober", "november", "desember"
]
FELLES_VALG = "Felles (Mor & Far / Den som gjør det)"

TEMAER = {
    "🌅 Varm Solnedgang": {
        "bg_color": "#FFE9DE",
        "banner_bg": "linear-gradient(135deg, #FF5757 0%, #FF7A3D 50%, #FF9A76 100%)",
        "tag_bg": "rgba(255, 255, 255, 0.32)",
        "tag_txt": "#FFFFFF",
        "tittel_farge": "#FFFFFF",
        "sub_farge": "#FFF4ED",
        "shadow": "0 4px 16px rgba(255, 87, 87, 0.28)",
        "border": "none"
    },
    "🌊 Nordisk Havblå": {
        "bg_color": "#DCEEFE",
        "banner_bg": "linear-gradient(135deg, #1E3A8A 0%, #2563EB 60%, #0284C7 100%)",
        "tag_bg": "rgba(255, 255, 255, 0.22)",
        "tag_txt": "#BAE6FD",
        "tittel_farge": "#FFFFFF",
        "sub_farge": "#E0F2FE",
        "shadow": "0 4px 16px rgba(37, 99, 235, 0.25)",
        "border": "none"
    },
    "✨ Leken Stjernehimmel": {
        "bg_color": "#E5DEFF",
        "banner_bg": "linear-gradient(135deg, #2E1065 0%, #4338CA 50%, #6D28D9 100%)",
        "tag_bg": "rgba(253, 224, 71, 0.25)",
        "tag_txt": "#FDE047",
        "tittel_farge": "#FDE047",
        "sub_farge": "#EDE9FE",
        "shadow": "0 4px 16px rgba(67, 56, 202, 0.3)",
        "border": "2px solid rgba(253, 224, 71, 0.5)"
    },
    "🌲 Eventyrskog & Natur": {
        "bg_color": "#D5EFE0",
        "banner_bg": "linear-gradient(135deg, #064E3B 0%, #047857 60%, #10B981 100%)",
        "tag_bg": "rgba(255, 255, 255, 0.25)",
        "tag_txt": "#D1FAE5",
        "tittel_farge": "#FFFFFF",
        "sub_farge": "#ECFDF5",
        "shadow": "0 4px 16px rgba(4, 120, 87, 0.25)",
        "border": "none"
    },
    "🌸 Søt Lavendel & Blomst": {
        "bg_color": "#FADCF4",
        "banner_bg": "linear-gradient(135deg, #701A75 0%, #A21CAF 55%, #E879F9 100%)",
        "tag_bg": "rgba(255, 255, 255, 0.25)",
        "tag_txt": "#FDF4FF",
        "tittel_farge": "#FFFFFF",
        "sub_farge": "#FCE7F3",
        "shadow": "0 4px 16px rgba(162, 28, 175, 0.25)",
        "border": "none"
    },
    "☕ Kaffe & Lun Kos": {
        "bg_color": "#EFE3D5",
        "banner_bg": "linear-gradient(135deg, #451A03 0%, #78350F 55%, #B45309 100%)",
        "tag_bg": "rgba(255, 255, 255, 0.22)",
        "tag_txt": "#FEF3C7",
        "tittel_farge": "#FFFFFF",
        "sub_farge": "#FFFBEB",
        "shadow": "0 4px 16px rgba(120, 53, 15, 0.25)",
        "border": "none"
    }
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
<meta name="theme-color" content="#1E3A8A">
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

def standard_data(valgt_pin="1234"):
    idag_str = datetime.now(TIDSSONE_NORGE).strftime("%Y-%m-%d")
    return {
        "pin": str(valgt_pin),
        "sist_nullstilt": idag_str,
        "tema": "🌅 Varm Solnedgang",
        "uke_oppgaver_lost": 0,
        "medlemmer": ["Far", "Mor", "Barn 1", "Barn 2"],
        "stjerne_brukere": ["Barn 1", "Barn 2"],
        "poeng": {"Far": 0, "Mor": 0, "Barn 1": 0, "Barn 2": 0},
        "sparemaal": {},
        "aktiviteter": STANDARD_AKTIVITETER,
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
            {"id": str(uuid.uuid4()), "tekst": "Pusse tenner morgen & kveld", "hvem": "Barn 1", "ferdig": False, "stjerner": 1, "fullfort_av": None, "gjentakende": True},
            {"id": str(uuid.uuid4()), "tekst": "Pusse tenner morgen & kveld", "hvem": "Barn 2", "ferdig": False, "stjerner": 1, "fullfort_av": None, "gjentakende": True},
            {"id": str(uuid.uuid4()), "tekst": "Rydde av bordet etter middag", "hvem": FELLES_VALG, "ferdig": False, "stjerner": 2, "fullfort_av": None, "gjentakende": True},
        ],
        "oppskrifter": STANDARD_MIDDAGER,
        "middagsplan": {dag: "" for dag in DAGER},
        "basisvarer": STANDARD_BASISVARER,
        "handleliste": migrer_handleliste(["Melk", "Brød", "Smør"])
    }

# ----------------- MULTI-FAMILIE GOOGLE SHEETS -----------------
def hent_hele_tabellen():
    try:
        df = conn.read(ttl=0)
        if df.empty:
            return pd.DataFrame(columns=["familie_kode", "data_dump"])
        if "familie_kode" not in df.columns:
            df["familie_kode"] = "hoved"
            if "data_dump" not in df.columns:
                df["data_dump"] = "{}"
        return df[["familie_kode", "data_dump"]].dropna(subset=["familie_kode"])
    except Exception:
        return pd.DataFrame(columns=["familie_kode", "data_dump"])

def hent_familie_json(familie_navn):
    df = hent_hele_tabellen()
    rad = df[df["familie_kode"].astype(str).str.lower() == str(familie_navn).lower()]
    if not rad.empty:
        try:
            return json.loads(str(rad["data_dump"].iloc[0]))
        except Exception:
            return None
    return None

def lagre_familie_data(familie_navn, ny_data):
    try:
        df = hent_hele_tabellen()
        json_tekst = json.dumps(ny_data, ensure_ascii=False)
        
        if len(json_tekst) > 48000:
            st.error("⚠️ Datamengden er for stor for regnearket. Endringen ble ikke lagret.")
            return False
        
        mask = df["familie_kode"].astype(str).str.lower() == str(familie_navn).lower()
        if mask.any():
            df.loc[mask, "data_dump"] = json_tekst
        else:
            ny_rad = pd.DataFrame([{"familie_kode": str(familie_navn).strip().lower(), "data_dump": json_tekst}])
            df = pd.concat([df, ny_rad], ignore_index=True)
            
        conn.update(data=df)
        return True
    except Exception as e:
        st.error(f"Kunne ikke lagre til Google Sheets: {e}")
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
        <div style="background-color: #FFFFFF; border-radius: 16px; padding: 26px; text-align: center; border: 2px solid #BFDBFE; box-shadow: 0 4px 12px rgba(0,0,0,0.06); margin-top: 20px;">
            <h1 style="color: #1E3A8A; margin: 0; font-size: 1.9rem; font-weight: 900;">🏡 Familiehub</h1>
            <p style="color: #3B82F6; font-size: 1.05rem; margin-top: 6px; font-weight: 600;">Logg inn i familiens hjem med navn og PIN-kode</p>
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
    st.error("Kunne ikke hente familiedata. Vennligst logg inn på nytt.")
    st.session_state["aktiv_familie"] = ""
    st.query_params.clear()
    st.stop()

if "merkedager" not in raw_data: raw_data["merkedager"] = []
if "oppskrifter" not in raw_data: raw_data["oppskrifter"] = STANDARD_MIDDAGER
else: raw_data["oppskrifter"] = migrer_oppskrifter(raw_data["oppskrifter"])
if "basisvarer" not in raw_data: raw_data["basisvarer"] = STANDARD_BASISVARER
if "sparemaal" not in raw_data: raw_data["sparemaal"] = {}
if "aktiviteter" not in raw_data: raw_data["aktiviteter"] = STANDARD_AKTIVITETER
if "fryser" not in raw_data: raw_data["fryser"] = []
if "uke_oppgaver_lost" not in raw_data: raw_data["uke_oppgaver_lost"] = 0
if "tema" not in raw_data: raw_data["tema"] = "🌅 Varm Solnedgang"

raw_data["handleliste"] = migrer_handleliste(raw_data.get("handleliste", []))
raw_data["middagsplan"] = migrer_middagsplan(raw_data.get("middagsplan", {}))

data = raw_data

def lagre_naa():
    return lagre_familie_data(aktiv_kode, data)

# ----------------- MIDNATT-NULLSTILLING -----------------
idag_dato = datetime.now(TIDSSONE_NORGE).date()
idag_str = idag_dato.strftime("%Y-%m-%d")

if data.get("sist_nullstilt") != idag_str:
    for o in data["oppgaver"]:
        if o.get("gjentakende", False):
            o["ferdig"] = False
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
    data["oppgaver"] = [o for o in data["oppgaver"] if o.get("gjentakende", False) or not o["ferdig"]]
    for o in data["oppgaver"]:
        o["ferdig"] = False
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
    st.caption("Skriv inn familiens PIN for å låse opp Admin-funksjonene:")
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

# ----------------- HENT TEMA & SETT BAKGRUNN MED SKARP KONTRAST -----------------
valgt_tema = data.get("tema", "🌅 Varm Solnedgang")
if valgt_tema not in TEMAER:
    valgt_tema = "🌅 Varm Solnedgang"

t_stil = TEMAER[valgt_tema]

st.markdown(
    f"""
    <style>
        /* Tvinger farge på alle bakgrunnslag i Streamlit */
        .stApp, [data-testid="stAppViewContainer"], .main {{
            background-color: {t_stil['bg_color']} !important;
        }}
        
        /* Gjør innholdskort og expanders tydelige og skarpe mot bakgrunnen */
        div[data-testid="stExpander"] {{
            background-color: #FFFFFF !important;
            border-radius: 12px !important;
            border: 1px solid rgba(0, 0, 0, 0.08) !important;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04) !important;
            margin-bottom: 8px !important;
        }}

        /* Sikrer at vanlige knapper har hvit bakgrunn, mørk tekst og tydelig kant */
        div.stButton > button, [data-testid="baseButton-secondary"], div.stFormSubmitButton > button {{
            background-color: #FFFFFF !important;
            border: 1.5px solid #94A3B8 !important;
            border-radius: 10px !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important;
        }}

        /* Tvinger teksten inni knapper til å være mørk koksgrå og fet */
        div.stButton > button *, [data-testid="baseButton-secondary"] *, div.stFormSubmitButton > button * {{
            color: #0F172A !important;
            font-weight: 700 !important;
        }}

        /* Hover-effekt på vanlige knapper */
        div.stButton > button:hover, div.stFormSubmitButton > button:hover {{
            background-color: #F1F5F9 !important;
            border-color: #475569 !important;
        }}

        /* Primærknapper får solid blå bakgrunn og hvit skrift */
        div.stButton > button[kind="primary"], [data-testid="baseButton-primary"] {{
            background-color: #2563EB !important;
            border: none !important;
        }}
        div.stButton > button[kind="primary"] *, [data-testid="baseButton-primary"] * {{
            color: #FFFFFF !important;
            font-weight: 700 !important;
        }}

        /* Fanelinjen */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: rgba(255, 255, 255, 0.75) !important;
            border-radius: 10px !important;
            padding: 4px !important;
            border: 1px solid rgba(0,0,0,0.06) !important;
        }}

        /* Faneknapper */
        .stTabs [data-baseweb="tab"] {{
            color: #334155 !important;
            font-weight: 600 !important;
        }}

        /* All vanlig tekst på siden */
        .stMarkdown p, .stMarkdown span, label {{
            color: #0F172A !important;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------- TOPPSTRIPE MED FORELDREKNAPP PÅ SKJERMEN -----------------
naa = datetime.now(TIDSSONE_NORGE)
dag_indeks = naa.weekday()
idag_navn = DAGER[dag_indeks]
dato_tekst = f"{idag_navn} {naa.day}. {MAANEDER[naa.month - 1]}"
klokke_tekst = naa.strftime("%H:%M")

col_banner, col_parent_btn = st.columns([0.76, 0.24])

with col_parent_btn:
    st.write("")
    if st.session_state["foreldremodus"]:
        if st.button("🔓 Lås foreldre", use_container_width=True, help="Slå av foreldremodus og gå tilbake til barnemodus"):
            st.session_state["foreldremodus"] = False
            st.toast("Barnemodus aktivert!")
            st.rerun()
    else:
        if st.button("🔐 Foreldre", use_container_width=True, help="Tast PIN for å åpne Admin-fanen"):
            aapne_pin_dialog()

with col_banner:
    banner_html = f"""
    <div style="background: {t_stil['banner_bg']}; 
                border-radius: 16px; padding: 12px 14px; text-align: left; margin-bottom: 6px; 
                box-shadow: {t_stil['shadow']}; border: {t_stil['border']};">
        <div style="display: inline-block; background: {t_stil['tag_bg']}; 
                    padding: 2px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 800; 
                    color: {t_stil['tag_txt']}; text-transform: uppercase; margin-bottom: 4px;">
            ✨ Familiens Hjem
        </div>
        <h3 style="margin: 0; color: {t_stil['tittel_farge']}; font-size: 1.4rem; font-weight: 900;">
            🏡 Familiehub <span style="font-weight: 400; opacity: 0.95;">({aktiv_kode.capitalize()})</span>
        </h3>
        <div style="font-size: 0.85rem; font-weight: 600; color: {t_stil['sub_farge']}; margin-top: 2px;">
            📅 {dato_tekst} &nbsp;•&nbsp; ⏰ {klokke_tekst}
        </div>
    </div>
    """
    st.markdown(banner_html, unsafe_allow_html=True)

# ----------------- KALENDER -----------------
with st.expander("🗓️ **Familiens Kalender & Merkedager**", expanded=False):
    merkedager = data.get("merkedager", [])
    slett_merkedag_id = None
    
    if merkedager:
        merkedager_sortert = sorted(merkedager, key=lambda x: x["dato"])
        for m in merkedager_sortert:
            m_dato = datetime.strptime(m["dato"], "%Y-%m-%d").date()
            dager_igjen = (m_dato - idag_dato).days
            
            if dager_igjen == 0:
                nedtelling = "🎉 I DAG!"
                bg_farge, kant_farge = "#D1FAE5", "#10B981"
            elif dager_igjen == 1:
                nedtelling = "⏰ I morgen!"
                bg_farge, kant_farge = "#FEF3C7", "#F59E0B"
            else:
                nedtelling = f"⏳ Om {dager_igjen} dager"
                bg_farge, kant_farge = "#F0FDF4", "#3B82F6"

            c_info, c_slett = st.columns([0.84, 0.16])
            with c_info:
                st.markdown(
                    f"""
                    <div style="background-color: {bg_farge}; border-left: 4px solid {kant_farge}; padding: 8px 12px; border-radius: 6px; margin-bottom: 6px;">
                        <span style="font-size: 1.05rem; font-weight: 700; color: #1F2937;">{m.get('ikon', '📌')} {m['tittel']}</span><br>
                        <span style="font-size: 0.85rem; color: #4B5563;">📅 {m_dato.strftime('%d.%m.%Y')} — <b>{nedtelling}</b></span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with c_slett:
                if st.button("✕", key=f"del_m_{m['id']}", help="Fjern"):
                    slett_merkedag_id = m["id"]

        if slett_merkedag_id:
            data["merkedager"] = [m for m in data["merkedager"] if m["id"] != slett_merkedag_id]
            lagre_naa()
            st.rerun()
    else:
        st.caption("Ingen merkedager lagt inn.")

    st.write("---")
    with st.form("form_ny_merkedag", clear_on_submit=True):
        m_tittel = st.text_input("Hva skal skje?", placeholder="f.eks. Bursdag, Ferie, Tannlege")
        col_d, col_i = st.columns([0.65, 0.35])
        m_dato_valg = col_d.date_input("Dato:", min_value=idag_dato, value=idag_dato)
        m_ikon = col_i.selectbox("Type:", ["🎂 Bursdag", "✈️ Ferie/Tur", "🦷 Tannlege/Lege", "🎒 Skole/Barnehage", "📌 Annet"])
        
        if st.form_submit_button("Lagre i kalenderen", use_container_width=True) and m_tittel.strip():
            data["merkedager"].append({
                "id": str(uuid.uuid4()),
                "tittel": m_tittel.strip(),
                "dato": m_dato_valg.strftime("%Y-%m-%d"),
                "ikon": m_ikon.split()[0]
            })
            lagre_naa()
            st.toast("Merkedag lagret!")
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

fane_navn = ["⭐ Oppgaver", "🎁 Butikk & Mål", "🍽️ Middag & Fryser", "🛒 Handleliste", "🎲 Aktiviteter"]
if er_forelder: fane_navn.append("👨‍👩‍👧‍👦 Admin")

faner = st.tabs(fane_navn)
fane_oppgaver, fane_butikk, fane_middag, fane_handleliste, fane_aktiviteter = faner[0], faner[1], faner[2], faner[3], faner[4]
fane_familie = faner[5] if er_forelder else None

# ----------------- FANE 1: OPPGAVER & DIPLOM -----------------
with fane_oppgaver:
    oppgaver_oppdatert = False
    slett_id = None
    medlemmer = data.get("medlemmer", [])
    stjerne_brukere = data.get("stjerne_brukere", [])

    with st.expander("🏆 **Ukens Stjernediplom (Trykk for å feire)**", expanded=False):
        antall_lost = data.get("uke_oppgaver_lost", 0)
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%); 
                        border: 3px dashed #F59E0B; border-radius: 16px; padding: 18px; text-align: center; margin-bottom: 8px;">
                <div style="font-size: 2.2rem;">🎖️ 📜 🌟</div>
                <h3 style="color: #92400E; margin: 4px 0 2px 0;">Ukens Superinnsats!</h3>
                <p style="color: #B45309; font-size: 1.05rem; margin-bottom: 8px;">
                    Familien har løst hele <b>{antall_lost} oppgaver</b> sammen denne uken!
                </p>
                <div style="font-size: 0.9rem; color: #78350F;">
                    {' ⭐ '.join([f'<b>{p}:</b> {data["poeng"].get(p, 0)} ⭐' for p in stjerne_brukere])}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("🎉 Skyt opp konfetti!", use_container_width=True):
            st.balloons()

    if stjerne_brukere:
        st.markdown("#### 🌟 Familiens Stjernetavle")
        kolonner = st.columns(len(stjerne_brukere))
        
        for idx, person in enumerate(stjerne_brukere):
            antall_stjerner = int(data["poeng"].get(person, 0))
            with kolonner[idx]:
                if antall_stjerner == 0:
                    stjerne_symboler = "<span style='color: #CA8A04; opacity: 0.4;'>☆☆☆☆☆</span>"
                    pluss_tekst = ""
                    motivasjon = "<div style='font-size: 0.72rem; color: #854D0E; font-weight: 600; margin-top: 4px;'>🚀 Gjør en oppgave for å få din første stjerne!</div>"
                else:
                    synlige = min(antall_stjerner, 10)
                    stjerne_symboler = "⭐" * synlige
                    pluss_tekst = f" <span style='font-size: 0.8rem; font-weight: 700; color: #854D0E;'>(+{antall_stjerner - 10})</span>" if antall_stjerner > 10 else ""
                    
                    p_maal = data.get("sparemaal", {}).get(person)
                    if p_maal:
                        mangler = p_maal["pris"] - antall_stjerner
                        if mangler <= 0:
                            motivasjon = f"<div style='font-size: 0.75rem; color: #047857; font-weight: 700; margin-top: 4px;'>🎯 Målet nådd: {p_maal['tittel']}!</div>"
                        else:
                            motivasjon = f"<div style='font-size: 0.72rem; color: #B45309; margin-top: 4px;'>🎯 <b>{mangler} ⭐</b> til {p_maal['tittel']}</div>"
                    else:
                        motivasjon = ""

                st.markdown(
                    f"""
                    <div style="background: linear-gradient(135deg, #FEF9C3 0%, #FEF08A 100%); 
                                border: 2px solid #FACC15; border-radius: 12px; padding: 10px; 
                                text-align: center; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                        <div style="font-size: 0.95rem; font-weight: 800; color: #854D0E;">👤 {person}</div>
                        <div style="font-size: 1.8rem; font-weight: 900; color: #A16207; line-height: 1.1; margin: 4px 0;">
                            {antall_stjerner} <span style="font-size: 1.3rem;">⭐</span>
                        </div>
                        <div style="font-size: 1.05rem; letter-spacing: 2px; min-height: 22px;">
                            {stjerne_symboler}{pluss_tekst}
                        </div>
                        {motivasjon}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    c_dag, c_uke = st.columns(2)
    with c_dag:
        if st.button("☀️ Nullstill nå (Manuell)", use_container_width=True):
            for o in data["oppgaver"]:
                if o.get("gjentakende", False):
                    o["ferdig"] = False
                    o["fullfort_av"] = None
            lagre_naa()
            st.toast("Daglige rutiner er nullstilt! ☀️")
            st.rerun()
    with c_uke:
        if er_forelder:
            st.button("🗓️ Start ny uke (Nullstill diplom)", on_click=cb_start_ny_uke, use_container_width=True)
        else:
            st.caption("🔒 Ny uke krever PIN")

    st.write("")
    for person in medlemmer:
        er_samler = person in stjerne_brukere
        poeng_badge = f" 🪙 {data['poeng'].get(person, 0)} ⭐" if er_samler else ""
        person_oppgaver = [o for o in data["oppgaver"] if o["hvem"] == person]
        gjenstaende = len([o for o in person_oppgaver if not o["ferdig"]])
        status_tekst = f"({gjenstaende} igjen)" if gjenstaende > 0 else "(Alt fullført! 🎉)"

        with st.expander(f"👤 **{person}**{poeng_badge} — {status_tekst}", expanded=(gjenstaende > 0)):
            for oppg in person_oppgaver:
                oppg_id = oppg["id"]
                merke = "🔄 " if oppg.get("gjentakende") else ""
                tekst_visning = f"{merke}{oppg['tekst']}"
                if oppg.get("stjerner", 0) > 0: tekst_visning += f" *(+{oppg['stjerner']} ⭐)*"

                if er_forelder:
                    c_chk, c_del = st.columns([0.85, 0.15])
                    er_ferdig = c_chk.checkbox(tekst_visning, value=oppg["ferdig"], key=f"chk_{oppg_id}")
                    if c_del.button("✕", key=f"del_{oppg_id}", help="Slett"): slett_id = oppg_id
                else:
                    er_ferdig = st.checkbox(tekst_visning, value=oppg["ferdig"], key=f"chk_{oppg_id}")

                if er_ferdig != oppg["ferdig"]:
                    oppg["ferdig"] = er_ferdig
                    stjerner = oppg.get("stjerner", 0)
                    if er_ferdig:
                        if er_samler:
                            data["poeng"][person] = data["poeng"].get(person, 0) + stjerner
                            data["uke_oppgaver_lost"] = data.get("uke_oppgaver_lost", 0) + 1
                            st.balloons()
                    else:
                        if er_samler:
                            data["poeng"][person] = max(0, data["poeng"].get(person, 0) - stjerner)
                            data["uke_oppgaver_lost"] = max(0, data.get("uke_oppgaver_lost", 1) - 1)
                    oppgaver_oppdatert = True

    # Fellesoppgaver
    felles_oppgaver = [o for o in data["oppgaver"] if o["hvem"] == FELLES_VALG]
    if felles_oppgaver:
        with st.expander(f"🤝 **Fellesoppgaver** ({len(felles_oppgaver)})", expanded=True):
            for oppg in felles_oppgaver:
                oppg_id = oppg["id"]
                merke = "🔄 " if oppg.get("gjentakende") else ""
                tot_stjerner = oppg.get("stjerner", 2)
                tekst_visning = f"{merke}{oppg['tekst']} *(+{tot_stjerner} ⭐)*"

                fa_raw = oppg.get("fullfort_av")
                if isinstance(fa_raw, list):
                    tidligere_hjelpere = fa_raw
                elif isinstance(fa_raw, str) and fa_raw:
                    tidligere_hjelpere = [fa_raw]
                else:
                    tidligere_hjelpere = []

                if oppg["ferdig"] and tidligere_hjelpere:
                    hjelper_tekst = ", ".join(tidligere_hjelpere)
                    tekst_visning += f" — *(Hjelpere: {hjelper_tekst})*"

                c_f_chk, c_f_who = st.columns([0.55, 0.45])
                er_ferdig = c_f_chk.checkbox(tekst_visning, value=oppg["ferdig"], key=f"f_chk_{oppg_id}")
                
                if not oppg["ferdig"]:
                    valgte_hjelpere = c_f_who.multiselect(
                        "Hvem hjalp til?",
                        options=medlemmer,
                        default=[medlemmer[0]] if medlemmer else [],
                        key=f"f_who_{oppg_id}",
                        label_visibility="collapsed"
                    )
                else:
                    c_f_who.write("")
                    valgte_hjelpere = tidligere_hjelpere

                if er_forelder and st.button("Slett fellesoppgave ✕", key=f"f_del_{oppg_id}"):
                    slett_id = oppg_id

                if er_ferdig != oppg["ferdig"]:
                    oppg["ferdig"] = er_ferdig
                    
                    if er_ferdig:
                        hjelpere_aa_belonne = valgte_hjelpere if valgte_hjelpere else ([medlemmer[0]] if medlemmer else [])
                        oppg["fullfort_av"] = hjelpere_aa_belonne
                        antall_hjelpere = max(1, len(hjelpere_aa_belonne))
                        stjerner_hver = max(1, round(tot_stjerner / antall_hjelpere))
                        
                        for h in hjelpere_aa_belonne:
                            if h in stjerne_brukere:
                                data["poeng"][h] = data["poeng"].get(h, 0) + stjerner_hver
                        
                        data["uke_oppgaver_lost"] = data.get("uke_oppgaver_lost", 0) + 1
                        st.balloons()
                        st.toast(f"🎉 Samarbeidsbonus! +{stjerner_hver} ⭐ til hver.")
                    else:
                        gamle_hjelpere = tidligere_hjelpere
                        antall_for = max(1, len(gamle_hjelpere))
                        trekk_hver = max(1, round(tot_stjerner / antall_for))
                        for h in gamle_hjelpere:
                            if h in stjerne_brukere:
                                data["poeng"][h] = max(0, data["poeng"].get(h, 0) - trekk_hver)
                        oppg["fullfort_av"] = None
                        data["uke_oppgaver_lost"] = max(0, data.get("uke_oppgaver_lost", 1) - 1)

                    oppgaver_oppdatert = True

    if slett_id:
        data["oppgaver"] = [o for o in data["oppgaver"] if o["id"] != slett_id]
        lagre_naa()
        st.rerun()

    if oppgaver_oppdatert:
        lagre_naa()
        st.rerun()

    if er_forelder:
        st.write("---")
        with st.expander("➕ **Legg til ny oppgave**"):
            with st.form("form_ny_oppg", clear_on_submit=True):
                oppg_tekst = st.text_input("Gjøremål:")
                valgte = st.multiselect("Til hvem?", [FELLES_VALG] + medlemmer, default=[medlemmer[0]] if medlemmer else [])
                stjerner = st.number_input("Stjerner (deles ved fellesoppgave):", min_value=1, max_value=20, value=2)
                er_daglig = st.checkbox("🔄 Daglig rutine", value=True)
                if st.form_submit_button("Lagre oppgave", use_container_width=True) and oppg_tekst.strip() and valgte:
                    for p in valgte:
                        data["oppgaver"].append({
                            "id": str(uuid.uuid4()), "tekst": oppg_tekst.strip(), "hvem": p,
                            "ferdig": False, "stjerner": int(stjerner), "fullfort_av": None, "gjentakende": er_daglig
                        })
                    lagre_naa()
                    st.toast("Oppgave lagt til!")
                    st.rerun()

# ----------------- FANE 2: BUTIKK & SPAREMÅL -----------------
with fane_butikk:
    st.subheader("🎯 Barnas Sparemål")
    stjerne_brukere = data.get("stjerne_brukere", [])

    if stjerne_brukere:
        for p in stjerne_brukere:
            saldo = data["poeng"].get(p, 0)
            maal_info = data.get("sparemaal", {}).get(p)
            
            with st.container():
                if maal_info:
                    maal_tittel = maal_info.get("tittel", "Mål")
                    maal_pris = max(1, int(maal_info.get("pris", 10)))
                    framgang = min(1.0, saldo / maal_pris)
                    prosent = int(framgang * 100)
                    
                    st.markdown(f"**👤 {p} sparer til: {maal_tittel}** (`{saldo} / {maal_pris} ⭐` — {prosent}%)")
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
                    st.info(f"👤 {p} har ikke satt noe sparemål enda.")
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

# ----------------- FANE 3: MIDDAG & FRYSER -----------------
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
                
                if st.form_submit_button("Lagre oppskrift", use_container_width=True) and ny_r.strip():
                    ingr_liste_ren = [x.strip() for x in ny_i.split(",") if x.strip()]
                    b64_str = bilde_til_base64(nytt_opp_bilde) if nytt_opp_bilde else None
                    data["oppskrifter"][ny_r.strip()] = {"ingredienser": ingr_liste_ren, "bilde": b64_str}
                    if lagre_naa():
                        st.toast(f"{ny_r.strip()} er lagt til!")
                        st.rerun()

# ----------------- FANE 4: HANDLELISTE -----------------
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

# ----------------- FANE 5: AKTIVITETER -----------------
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
            <div style="background-color: #ECFDF5; border: 2px solid #10B981; border-radius: 12px; padding: 18px; text-align: center; margin: 14px 0;">
                <div style="font-size: 1.1rem; color: #047857; font-weight: 800;">Dagens utvalgte aktivitet:</div>
                <div style="font-size: 1.45rem; font-weight: 900; color: #065F46; margin-top: 6px;">
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

# ----------------- FANE 6: ADMIN -----------------
if er_forelder and fane_familie:
    with fane_familie:
        st.subheader("👨‍👩‍👧‍👦 Familieadministrasjon")
        
        with st.expander("🎨 **Utseende & Tema for Appen**", expanded=True):
            st.caption("Velg familiens favoritt-tema (endrer både bakgrunnsfargen og toppbanneret):")
            tema_alternativer = list(TEMAER.keys())
            naavaerende_tema = data.get("tema", "🌅 Varm Solnedgang")
            if naavaerende_tema not in tema_alternativer:
                naavaerende_tema = "🌅 Varm Solnedgang"
                
            valgt_nytt_tema = st.radio(
                "Velg stil:", 
                tema_alternativer, 
                index=tema_alternativer.index(naavaerende_tema)
            )
            if valgt_nytt_tema != data.get("tema"):
                data["tema"] = valgt_nytt_tema
                lagre_naa()
                st.toast(f"Tema oppdatert til {valgt_nytt_tema}! 🎉")
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

        st.markdown("#### 👤 Familiemedlemmer")
        for i, person in enumerate(list(data["medlemmer"])):
            st.markdown(f"**Person {i+1}: {person}**")
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
                    if isinstance(o.get("fullfort_av"), list):
                        o["fullfort_av"] = [nytt if x == gammelt else x for x in o["fullfort_av"]]
                    elif o.get("fullfort_av") == gammelt:
                        o["fullfort_av"] = nytt
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