import streamlit as st
import requests

st.set_page_config(page_title="PubChem GHS Classification", page_icon="🧪", layout="centered")

st.title("🔬 GHS Classification dari PubChem")
compound = st.text_input("Masukkan nama senyawa:", "acetone")

def get_cid(compound_name):
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{compound_name}/cids/JSON"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    cids = data.get("IdentifierList", {}).get("CID", [])
    return cids[0] if cids else None

def get_ghs_classification(cid):
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/record/JSON"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    def search_section(sections):
        for section in sections:
            if section.get("TOCHeading") == "GHS Classification":
                return section
            if "Section" in section:
                result = search_section(section["Section"])
                if result:
                    return result
        return None

    root_sections = data.get("Record", {}).get("Section", [])
    return search_section(root_sections)

def extract_ghs_info(ghs_section):
    if not ghs_section:
        return "⚠️ Data GHS Classification tidak tersedia untuk senyawa ini."

    result_lines = []
    for info in ghs_section.get("Information", []):
        title = info.get("Name", "Informasi")
        value_text = ""
        if "Value" in info and "StringWithMarkup" in info["Value"]:
            value_text = "\n".join([s["String"] for s in info["Value"]["StringWithMarkup"]])
        result_lines.append(f"**{title}**\n{value_text}")
    return "\n\n".join(result_lines)

if st.button("Cari Data"):
    try:
        cid = get_cid(compound)
        if cid:
            ghs_section = get_ghs_classification(cid)
            result = extract_ghs_info(ghs_section)
            st.markdown(f"### 🧾 Hasil untuk: `{compound}`\n{result}")
        else:
            st.warning("❌ CID tidak ditemukan untuk senyawa ini.")
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Gagal mengambil data: {e}")
