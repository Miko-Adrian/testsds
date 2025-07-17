import streamlit as st
import requests

st.set_page_config(page_title="PubChem GHS & First Aid", layout="centered")

st.title("🔬 PubChem - GHS & First Aid Data")
chemical_name = st.text_input("Masukkan nama senyawa:", "acetone")

def get_cid(name):
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{name}/cids/JSON"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        cids = data.get("IdentifierList", {}).get("CID", [])
        if cids:
            return cids[0]
    return None

def find_section(sections, heading):
    for section in sections:
        if section.get("TOCHeading", "") == heading:
            return section
        if "Section" in section:
            found = find_section(section["Section"], heading)
            if found:
                return found
    return None

def extract_ghs_pictograms(section):
    pictograms = []
    for info in section.get("Information", []):
        for value in info.get("Value", {}).get("StringWithMarkup", []):
            if "http" in value.get("String", ""):
                pictograms.append(value["String"])
    return pictograms

def extract_first_aid(section):
    texts = []
    for info in section.get("Information", []):
        for item in info.get("Value", {}).get("StringWithMarkup", []):
            texts.append(item["String"])
    return texts

if st.button("🔍 Cari Data"):
    with st.spinner("Mengambil data dari PubChem..."):
        cid = get_cid(chemical_name)
        if not cid:
            st.error("❌ CID tidak ditemukan untuk senyawa ini.")
        else:
            url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/record/JSON"
            response = requests.get(url)
            record_data = response.json()

            if "Record" not in record_data:
                st.error("❌ Data record tidak ditemukan untuk senyawa ini.")
            else:
                sections = record_data["Record"].get("Section", [])
                ghs_section = find_section(sections, "GHS Classification")
                first_aid_section = find_section(sections, "First Aid Measures")

                # Tampilkan simbol bahaya
                st.subheader("⚠️ Simbol Bahaya (GHS Pictograms)")
                if ghs_section:
                    pictograms = extract_ghs_pictograms(ghs_section)
                    if pictograms:
                        for url in pictograms:
                            st.image(url, width=80)
                    else:
                        st.warning("Tidak ada simbol bahaya ditemukan.")
                else:
                    st.warning("Data GHS Classification tidak tersedia.")

                # Tampilkan penanganan pertama
                st.subheader("🩹 Penanganan Pertama (First Aid Measures)")
                if first_aid_section:
                    first_aid_text = extract_first_aid(first_aid_section)
                    if first_aid_text:
                        for item in first_aid_text:
                            st.markdown(f"- {item}")
                    else:
                        st.warning("Tidak ada teks penanganan pertama ditemukan.")
                else:
                    st.warning("Data First Aid Measures tidak tersedia.")
