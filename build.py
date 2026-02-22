import pathlib, json, yaml, sys

root = pathlib.Path(__file__).parent
concept_dir = root / "concepts"
docs_dir = root / "docs"
scheme_file = root / "schemes.yml"

def load_yaml(p):
    return yaml.safe_load(p.read_text(encoding="utf-8"))

scheme = load_yaml(scheme_file)["schemes"][0]
base_uri = scheme["baseUri"]

concepts = []
ids = set()

for f in concept_dir.glob("*.yml"):
    if f.name.startswith("_"):
        continue

    c = load_yaml(f)
    cid = c["id"]

    if cid in ids:
        print("Duplicate id:", cid)
        sys.exit(1)
    ids.add(cid)

    uri = base_uri + cid
    obj = {"@id": uri, "@type": "skos:Concept"}

    pref = []
    alt = []

    for t in c.get("terms", []):
        lit = {"@value": t["label"], "@language": t["lang"]}
        if t.get("type") == "Suositettava termi":
            pref.append(lit)
        else:
            alt.append(lit)

    if pref:
        obj["skos:prefLabel"] = pref
    if alt:
        obj["skos:altLabel"] = alt

    defs = []
    for d in c.get("definitions", []):
        defs.append({"@value": d["text"], "@language": d["lang"]})

    if defs:
        obj["skos:definition"] = defs

    rel = c.get("relations", {})
    for key in ["broader", "narrower", "related"]:
        vals = rel.get(key, [])
        if vals:
            obj["skos:" + key] = [base_uri + v for v in vals]

    concepts.append(obj)

data = {
    "@context": {"skos": "http://www.w3.org/2004/02/skos/core#"},
    "@graph": concepts,
    "skos:prefLabel": [
        {"@value": scheme["prefLabel"]["fi"], "@language": "fi"},
        {"@value": scheme["prefLabel"]["sv"], "@language": "sv"},
        {"@value": scheme["prefLabel"]["en"], "@language": "en"},
    ],
}

docs_dir.mkdir(exist_ok=True)
out_file = docs_dir / "sanasto.jsonld"
out_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

print("OK built", len(concepts), "concepts →", out_file)