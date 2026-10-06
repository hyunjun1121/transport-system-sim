import re, pathlib, json
tex = pathlib.Path("manuscript.tex").read_text(encoding="utf-8")
body = tex.split(r"\begin{thebibliography}")[0]
cited = set()
order = []
for m in re.finditer(r"\\cite\{([^}]+)\}", body):
    for k in m.group(1).split(","):
        k = k.strip()
        cited.add(k)
        if k not in order:
            order.append(k)
all_bibs = re.findall(r"\\bibitem\{([^}]+)\}", tex)
unused = [b for b in all_bibs if b not in cited]
missing = [k for k in cited if k not in all_bibs]
print("total bibitems:", len(all_bibs))
print("cited unique:", len(cited))
print("UNUSED:", unused)
print("MISSING:", missing)
print("cite order:", order)

body_only = body.split(r"\maketitle", 1)[-1]
words = len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'\-]*", body_only))
print("body_words_approx:", words)
parts = re.split(r"\\section\*?\{([^}]+)\}", body_only)
for i in range(1, len(parts), 2):
    name = parts[i]
    content = parts[i + 1] if i + 1 < len(parts) else ""
    w = len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'\-]*", content))
    print(f"  {name}: {w} words")

# claims-language quick scan (reserved words in body prose, not claim-guard)
forbidden = ["field-verified", "empirically fitted", "predictive", "best route",
             "operational", "forecast", "calibrated", "validated", "final-ready", "optimal route"]
low = body_only.lower()
for f in forbidden:
    if f in low:
        idx = low.find(f)
        print(f"FORBIDDEN hit '{f}': ...{body_only[max(0,idx-60):idx+80].replace(chr(10),' ')}...")

# DOI sanity
dois = re.findall(r"doi:\s*([0-9]\.[0-9]+/[^\s,;]+)", tex)
print("dois:", len(dois))
for d in dois:
    print(" ", d)
