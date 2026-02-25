import pathlib
import json
import yaml
import sys

root = pathlib.Path(__file__).parent
concept_dir = root / "concepts"
docs_dir = root / "docs"
scheme_file = root / "schemes.yml"

docs_dir.mkdir(exist_ok=True)


def load_yaml(path: pathlib.Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


scheme_data = load_yaml(scheme_file)["schemes"][0]
base_uri = scheme_data["baseUri"]

concepts = []
ids = set()

# -----------------------------
# CONCEPTS
# -----------------------------
for f in list(concept_dir.glob("*.yml")) + list(concept_dir.glob("*.yaml")):
    if f.name.startswith("_"):
        continue

    c = load_yaml(f)
    cid = c["id"]

    if cid in ids:
        print("Duplicate id:", cid)
        sys.exit(1)
    ids.add(cid)

    uri = base_uri + cid

    obj = {
        "@id": uri,
        "@type": "skos:Concept"
    }

    # SCHEME LINK
    if "schemeId" in c:
        obj["skos:inScheme"] = base_uri + c["schemeId"]

    # TERMS
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
            "@language": n.get("lang", "fi")
        })
    if notes:
        obj["skos:note"] = notes

    # SOURCES
# SOURCES
srcs = []
for s in c.get("sources", []):
    if isinstance(s, dict):
        node = {
            "@language": s.get("lang", "")
        }

        # label
        if s.get("label"):
            node["rdfs:label"] = s["label"]

        # URL → URI node
        if s.get("url"):
            node["@id"] = s["url"]

        srcs.append(node)

    else:
        srcs.append(s)

if srcs:
    obj["dcterms:source"] = srcs

    # RELATIONS
    rel = c.get("relations", {})
    for key in ["broader", "narrower", "related"]:
        vals = rel.get(key, [])
        if vals:
            obj["skos:" + key] = [base_uri + v for v in vals]

    # METADATA
    meta = c.get("metadata", {})
    if meta.get("created"):
        obj["dcterms:created"] = {
            "@value": meta["created"],
            "@type": "xsd:dateTime"
        }
    if meta.get("modified"):
        obj["dcterms:modified"] = {
            "@value": meta["modified"],
            "@type": "xsd:dateTime"
        }

    concepts.append(obj)

# -----------------------------
# CONCEPT SCHEME
# -----------------------------
scheme_uri = base_uri + scheme_data["id"]

scheme_obj = {
    "@id": scheme_uri,
    "@type": "skos:ConceptScheme",
    "skos:prefLabel": [
        {"@value": scheme_data["prefLabel"]["fi"], "@language": "fi"},
        {"@value": scheme_data["prefLabel"]["sv"], "@language": "sv"},
        {"@value": scheme_data["prefLabel"]["en"], "@language": "en"}
    ]
}

# -----------------------------
# OUTPUT
# -----------------------------
out = {
"@context": {
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "dcterms": "http://purl.org/dc/terms/",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#"
},
    "@graph": [scheme_obj] + concepts
}

out_path = docs_dir / "sanasto.jsonld"
out_path.write_text(
    json.dumps(out, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print(f"OK built {len(concepts)} concepts -> {out_path}")
