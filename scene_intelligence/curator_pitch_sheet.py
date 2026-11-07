"""Rank curator-contacts into a pitch sheet. Legitimacy over vanity: fit, then
cross-list count (weighted above saves), then saves. Flags likely farms.
"""
import json
import argparse

FIT_ORDER = {"top": 0, "good": 1, "partial": 2}
SUSPECT_SAVES = 1000


def rank(curators):
    """Return curators sorted by fit, cross_list_count desc, saves desc; add `suspect`."""
    out = []
    for c in curators:
        c = dict(c)
        c["suspect"] = (c.get("cross_list_count", 0) == 0 and (c.get("saves") or 0) >= SUSPECT_SAVES)
        out.append(c)
    out.sort(key=lambda c: (FIT_ORDER.get(c.get("fit", ""), 3),
                            -(c.get("cross_list_count") or 0),
                            -(c.get("saves") or 0)))
    return out


def main():
    ap = argparse.ArgumentParser(description="Print the ranked curator pitch sheet")
    ap.add_argument("--contacts", default="scene_intelligence/enriched_contacts.json")
    args = ap.parse_args()

    data = json.load(open(args.contacts, encoding="utf-8"))
    rows = data if isinstance(data, list) else (data.get("contacts") or list(data.values()))
    curators = [c for c in rows if isinstance(c, dict) and c.get("category") == "curator"]
    ranked = rank(curators)

    print(f"Curator pitch sheet ({len(ranked)} curators)\n")
    for c in ranked:
        ct = c.get("contact", {})
        reach = ct.get("ig") and f"IG @{ct['ig']}" or ct.get("email") or ct.get("submission", "")
        flag = "  [SUSPECT - vet]" if c.get("suspect") else ""
        print(f"  [{c.get('fit','?'):7}] x{c.get('cross_list_count',0)} | saves {c.get('saves',0):>6} | "
              f"{c.get('name','?')[:28]:28} | {ct.get('route','?'):4} -> {reach}{flag}")


if __name__ == "__main__":
    main()
