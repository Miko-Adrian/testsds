import requests

def get_cid(compound_name):
    """Ambil CID dari nama senyawa"""
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{compound_name}/cids/JSON"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    cids = data.get("IdentifierList", {}).get("CID", [])
    return cids[0] if cids else None

def get_ghs_classification(cid):
    """Ambil data GHS Classification dari CID"""
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
    ghs_section = search_section(root_sections)
    return ghs_section

def extract_ghs_info(ghs_section):
    """Ambil dan susun informasi GHS Classification"""
    if not ghs_section:
        return "Data GHS Classification tidak tersedia."

    result_lines = []
    for info in ghs_section.get("Information", []):
        title = info.get("Name", "Informasi")
        value_text = ""
        if "Value" in info and "StringWithMarkup" in info["Value"]:
            value_text = "\n".join([s["String"] for s in info["Value"]["StringWithMarkup"]])
        result_lines.append(f"🔹 {title}:\n{value_text}")
    return "\n\n".join(result_lines)

# =========================
# 🔧 CONTOH PENGGUNAAN
# =========================
compound = "acetone"  # Bisa kamu ganti dengan senyawa lain
try:
    cid = get_cid(compound)
    if cid:
        ghs_section = get_ghs_classification(cid)
        output = extract_ghs_info(ghs_section)
    else:
        output = "CID tidak ditemukan untuk senyawa tersebut."
except requests.exceptions.RequestException as e:
    output = f"Gagal mengambil data dari PubChem: {e}"

# =========================
# 🔍 TAMPILKAN HASIL
# =========================
print(f"=== GHS Classification untuk: {compound} ===\n")
print(output)
