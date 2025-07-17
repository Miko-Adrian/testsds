import requests

def get_cid(compound_name):
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{compound_name}/cids/JSON"
    res = requests.get(url)
    res.raise_for_status()
    data = res.json()
    cids = data.get("IdentifierList", {}).get("CID", [])
    return cids[0] if cids else None

def get_ghs_classification(cid):
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/record/JSON"
    res = requests.get(url)
    res.raise_for_status()
    data = res.json()

    def search_sections(sections):
        for section in sections:
            if section.get("TOCHeading") == "GHS Classification":
                return section
            if "Section" in section:
                found = search_sections(section["Section"])
                if found:
                    return found
        return None

    sections = data.get("Record", {}).get("Section", [])
    ghs_section = search_sections(sections)
    return ghs_section

def extract_ghs_info(ghs_section):
    if not ghs_section:
        return "Data GHS Classification tidak tersedia."

    info = []
    for item in ghs_section.get("Information", []):
        heading = item.get("Name", "")
        value = ""
        if "Value" in item:
            value_dict = item["Value"]
            if "StringWithMarkup" in value_dict:
                value = "\n".join(s["String"] for s in value_dict["StringWithMarkup"])
        info.append(f"🔹 {heading}:\n{value}\n")
    return "\n".join(info)

# ==== Contoh penggunaan ====
compound_name = "acetone"
cid = get_cid(compound_name)

if cid:
    ghs_section = get_ghs_classification(cid)
    result = extract_ghs_info(ghs_section)
else:
    result = "CID tidak ditemukan."

print(result)
