import pathlib, json, yaml, sys

root = pathlib.Path(__file__).parent
concept_dir = root / "concepts"
docs_dir = root / "docs"
scheme_file = root / "schemes.yml"

docs_dir.mkdir(exist_ok=True)

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
<<<<<<< HEAD
    obj = {"@id": uri, "@type": "skos:Concept"}

=======

    obj = {
        "@id": uri,
        "@type": "skos:Concept"
    }

    # STATUS
    if "status" in c:
        obj["betk:status"] = c["status"]

    # SCHEME
    if "schemeId" in c:
        obj["skos:inScheme"] = base_uri + c["schemeId"]

    # TERMS
>>>>>>> e5a5584320286bfce67f0f1e3d9f0b98556dfd74
    pref = []
    alt = []

    for t in c.get("terms", []):
        lit = {"@value": t["label"], "@language": t["lang"]}
        if t.get("type") == "Suositettava termi":
            pref.append(lit)
        else:
            alt.append(lit)

<<<<<<< HEAD
    if pref:
        obj["skos:prefLabel"] = pref
    if alt:
        obj["skos:altLabel"] = alt

    defs = []
    for d in c.get("definitions", []):
        defs.append({"@value": d["text"], "@language": d["lang"]})

    if defs:
        obj["skos:definition"] = defs

=======
    if pref: obj["skos:prefLabel"] = pref
    if alt: obj["skos:altLabel"] = alt

    # DEFINITIONS
    defs = []
    for d in c.get("definitions", []):
        defs.append({
            "@value": d["text"],
            "@language": d.get("lang", "fi")
        })
    if defs:
        obj["skos:definition"] = defs

    # NOTES
    notes = []
    for n in c.get("notes", []):
        notes.append({
            "@value": n["text"],
            "@language": n.get("lang", "fi"),
            "source": n.get("source", ""),
            "quote": n.get("quote", False)
        })
    if notes:
        obj["skos:note"] = notes

    # SOURCES
    srcs = []
    for s in c.get("sources", []):
        if isinstance(s, dict):
            srcs.append({
                "@value": s["label"],
                "@language": s.get("lang", "")
            })
        else:
            srcs.append(s)
    if srcs:
        obj["dct:source"] = srcs

    # RELATIONS
>>>>>>> e5a5584320286bfce67f0f1e3d9f0b98556dfd74
    rel = c.get("relations", {})
    for key in ["broader", "narrower", "related"]:
        vals = rel.get(key, [])
        if vals:
            obj["skos:" + key] = [base_uri + v for v in vals]

    concepts.append(obj)

<<<<<<< HEAD
data = {
    "@context": {"skos": "http://www.w3.org/2004/02/skos/core#"},
=======
out = {
    "@context": {
        "skos": "http://www.w3.org/2004/02/skos/core#",
        "dct": "http://purl.org/dc/terms/",
        "betk": "https://w3id.org/betk/def/"
    },
>>>>>>> e5a5584320286bfce67f0f1e3d9f0b98556dfd74
    "@graph": concepts,
    "skos:prefLabel": [
        {"@value": scheme["prefLabel"]["fi"], "@language": "fi"},
        {"@value": scheme["prefLabel"]["sv"], "@language": "sv"},
<<<<<<< HEAD
        {"@value": scheme["prefLabel"]["en"], "@language": "en"},
    ],
}

docs_dir.mkdir(exist_ok=True)
out_file = docs_dir / "sanasto.jsonld"
out_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

print("OK built", len(concepts), "concepts →", out_file)
=======
        {"@value": scheme["prefLabel"]["en"], "@language": "en"}
}

(docs_dir / "sanasto.jsonld").write_text(
    json.dumps(out, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print("OK built", len(concepts), "concepts → docs/sanasto.jsonld")
>>>>>>> e5a5584320286bfce67f0f1e3d9f0b98556dfd74
