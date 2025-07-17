import streamlit as st
import requests

# Konfigurasi halaman
st.set_page_config(page_title="Informasi Bahan Kimia dari PubChem", layout="wide")
st.title("🧪 Informasi Bahan Kimia dari PubChem")

# Input senyawa
compound_name = st.text_input("Masukkan nama senyawa:", "formaldehyde")

if st.button("Cari Data"):
    with st.spinner("Mengambil data..."):
        try:
            # Step 1: Ambil CID
            cid_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{compound_name}/cids/JSON"
            cid = requests.get(cid_url).json()['IdentifierList']['CID'][0]

         # Step 2: Ambil record
url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/record/JSON"
response = requests.get(url)
record_data = response.json()

if "Record" not in record_data:
    st.error("❌ Data record tidak ditemukan untuk senyawa ini. Mungkin senyawanya tidak memiliki data keamanan di PubChem.")
else:
    data = record_data
    # lanjutkan proses seperti biasa di sini
    ...

            root_sections = data["Record"]["Section"]
            safety = find_section(root_sections, "Safety and Hazards")

            # --- GHS Section ---
            ghs = find_section(safety["Section"], "GHS Classification") if safety else None
            st.subheader("⚠️ GHS Classification")
            if ghs:
                for info in ghs.get("Information", []):
                    if info.get("Name") == "Pictogram(s)":
                        for url in info["Value"]["ExternalDataURL"]:
                            st.image(url, width=100)
                    elif info.get("Name") == "Signal Word":
                        st.markdown(f"**Signal Word:** {info['Value']['StringWithMarkup'][0]['String']}")
                    elif info.get("Name") == "Hazard Statements":
                        st.markdown("**Hazard Statements:**")
                        for h in info["Value"]["StringWithMarkup"]:
                            st.write(f"- {h['String']}")
            else:
                st.warning("Data GHS tidak ditemukan.")

            # --- First Aid ---
            faid = find_section(safety["Section"], "First Aid Measures") if safety else None
            st.subheader("🩺 First Aid Measures")
            if faid:
                for info in faid.get("Information", []):
                    for val in info.get("Value", {}).get("StringWithMarkup", []):
                        st.write(f"- {val['String']}")
            else:
                st.warning("Data First Aid tidak tersedia.")

            # --- Firefighting Measures ---
            fire = find_section(safety["Section"], "Fire Fighting Measures") if safety else None
            st.subheader("🔥 Fire Fighting Measures")
            if fire:
                for info in fire.get("Information", []):
                    for val in info.get("Value", {}).get("StringWithMarkup", []):
                        st.write(f"- {val['String']}")
            else:
                st.warning("Data Fire Fighting tidak tersedia.")

            # --- Stability and Reactivity ---
            stab = find_section(safety["Section"], "Stability and Reactivity") if safety else None
            st.subheader("⚗️ Stability and Reactivity")
            if stab:
                for info in stab.get("Information", []):
                    for val in info.get("Value", {}).get("StringWithMarkup", []):
                        st.write(f"- {val['String']}")
            else:
                st.warning("Data Stability and Reactivity tidak tersedia.")

            # --- PPE (Personal Protection) ---
            exposure = find_section(safety["Section"], "Exposure Controls / Personal Protection") if safety else None
            st.subheader("🧤 PPE / Personal Protection")
            if exposure:
                for info in exposure.get("Information", []):
                    for val in info.get("Value", {}).get("StringWithMarkup", []):
                        st.write(f"- {val['String']}")
            else:
                st.warning("Data PPE tidak tersedia.")

        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")
