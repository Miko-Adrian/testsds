import streamlit as st
import requests
import pandas as pd
from PIL import Image
from io import BytesIO

# Set page config
st.set_page_config(
    page_title="PubChem Hazard Data Viewer",
    layout="wide",
    page_icon="🧪"
)

# Title and input
st.title("PubChem Hazard Data Viewer")
compound_name = st.text_input("Masukkan nama senyawa (misal: Acetone):")

# Fungsi ambil data
def fetch_pubchem_data(compound):
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/name/{compound}/JSON"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Gagal mengambil data dari PubChem: {str(e)}")
        return None

# Fungsi interpretasi data
def interpret_hazards(compound_data):
    """Extract hazard codes from PubChem PUG View JSON (Record format)"""
    hazards = []
    try:
        sections = compound_data.get("Record", {}).get("Section", [])
        for section in sections:
            if section.get("TOCHeading") == "Safety and Hazards":
                for subsec in section.get("Section", []):
                    if subsec.get("TOCHeading") == "GHS Classification":
                        for info in subsec.get("Information", []):
                            string_data = info.get("Value", {}).get("StringWithMarkup", [])
                            for item in string_data:
                                text = item.get("String", "")
                                if text.startswith("H"):
                                    code = text.split(":")[0].strip()
                                    hazards.append(code)
    except Exception as e:
        st.warning(f"Gagal membaca informasi hazard: {str(e)}")
    return hazards

# Pemetaan simbol GHS
def hazard_to_symbol(code):
    code_mapping = {
        "H200": "💥 Explosive",
        "H220": "🔥 Flammable Gas",
        "H280": "🗜️ Gas Under Pressure",
        "H300": "☠️ Fatal if swallowed",
        "H314": "🧪 Causes severe skin burns",
        "H318": "👁️ Serious eye damage",
        "H330": "☠️ Fatal if inhaled",
        "H334": "🌬️ May cause allergy or asthma",
        "H340": "🧬 May cause genetic defects",
        "H350": "🎗️ May cause cancer",
        "H360": "👶 May damage fertility or the unborn child",
        "H370": "🧠 Damage to organs",
        "H410": "🐟 Very toxic to aquatic life"
    }
    for h_code, name in code_mapping.items():
        if code.startswith(h_code[:3]):
            return {"code": h_code, "name": name, "symbol": name.split()[0]}
    return {"code": code, "name": "⚠️ Unknown Hazard", "symbol": "⚠️"}

# Menampilkan hasil
if compound_name:
    data = fetch_pubchem_data(compound_name)
    if data:
        hazards = interpret_hazards(data)
        if hazards:
            st.subheader("Simbol Bahaya (GHS):")
            cols = st.columns(4)
            unique_hazards = set()
            for i, hazard in enumerate(hazards):
                if isinstance(hazard, str):
                    hazard_code = hazard.split(':')[0] if ':' in hazard else hazard
                    if hazard_code not in unique_hazards:
                        unique_hazards.add(hazard_code)
                        hazard_info = hazard_to_symbol(hazard_code)
                        with cols[i % 4]:
                            st.markdown(f"""
                            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                                <span style="font-size: 24px; margin-right: 10px;">{hazard_info['symbol']}</span>
                                <span>{hazard_info['name']}</span>
                            </div>
                            """, unsafe_allow_html=True)
        else:
            st.info("Tidak ada informasi bahaya yang ditemukan untuk bahan kimia ini.")
