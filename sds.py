import streamlit as st
import requests

st.set_page_config(
    page_title="PubChem GHS & First Aid Viewer",
    layout="wide"
)

st.title("🔬 PubChem - GHS Symbols & First Aid Info")

# Input senyawa
compound_name = st.text_input("Masukkan nama senyawa:", "formaldehyde")

# Fungsi cari CID dari nama senyawa
def get_cid(name):
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/cids/JSON"
    res = requests.get(url)
    if res.status_code != 200:
        return None
    data = res.json()
    return data.get("IdentifierList", {}).get("CID", [None])[0]

# Fungsi rekursif cari section berdasarkan TOCHeading
def find_section(sections, heading):
    for section in sections:
        if section.get("TOCHeading") == heading:
            return section
        elif "Section" in section:
            result = find_section(section["Section"], heading)
            if result:
                return result
    return None

# Fungsi ambil pictogram dan first aid
def get_pubchem_data(cid):
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/record/JSON"
    res = requests.get(url)
    if res.status_code != 200:
        st.error("❌ Gagal mengambil data dari PubChem.")
        return

    record_data = res.json()
    if "Record" not in record_data:
        st.error("❌ Data record tidak ditemukan untuk senyawa ini.")
        return

    sections = record_data["Record"].get("Section", [])

    # GHS Classification
    ghs_section = find_section(sections, "GHS Classification")
    if ghs_section and "Information" in ghs_section:
        pictograms = ghs_section["Information"][0].get("Value", {}).get("StringWithMarkup", [])
        if pictograms:
            st.subheader("⚠️ GHS Pictograms")
            for picto in pictograms:
                st.image(picto["String"], width=100)
        else:
            st.info("✅ Tidak ada simbol GHS ditemukan.")
    else:
        st.warning("⚠️ Data GHS Classification tidak tersedia untuk senyawa ini.")

    # First Aid Measures
    aid_section = find_section(sections, "First Aid Measures")
    if aid_section and "Information" in aid_section:
        st.subheader("🚑 First Aid Measures")
        for info in aid_section["Information"]:
            texts = info.get("Value", {}).get("StringWithMarkup", [])
            for t in texts:
                st.markdown(f"- {t['String']}")
    else:
        st.warning("⚠️ Data First Aid Measures tidak tersedia untuk senyawa ini.")

# Jalankan jika ada input
if compound_name:
    cid = get_cid(compound_name)
    if cid:
        get_pubchem_data(cid)
    else:
        st.error("❌ Senyawa tidak ditemukan di PubChem.")
