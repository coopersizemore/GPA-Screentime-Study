# select_by_college.py
import csv
import random
from collections import defaultdict
from pathlib import Path

INPUT_CSV = "st370_undergrads_college.csv"
OUTPUT_TXT = "email_list.txt"
OUTPUT_CSV = "email_list.csv"
PER_COLLEGE = 40  # number to pick per college

def load_rows(path: Path):
    rows = []
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            row = {
                "unity_id": (r.get("unity_id") or "").strip(),
                "first_name": (r.get("first_name") or "").strip(),
                "last_name": (r.get("last_name") or "").strip(),
                "email": (r.get("email") or "").strip(),
                "campus_id": (r.get("campus_id") or "").strip(),
                "college": (r.get("college") or "").strip() or "Unknown / Unclassified",
            }
            if row["email"]:
                rows.append(row)
    return rows

def dedupe_by_email_or_unity(rows):
    seen, out = set(), []
    for r in rows:
        key = (r["email"].lower() if r["email"] else "").strip() or f"uid:{r['unity_id']}"
        if key and key not in seen:
            seen.add(key)
            out.append(r)
    return out

def main():
    input_path = Path(INPUT_CSV)
    if not input_path.exists():
        raise FileNotFoundError(f"Could not find {INPUT_CSV} in {Path.cwd()}")

    rows = load_rows(input_path)

    # Group by college
    groups = defaultdict(list)
    for r in rows:
        groups[r["college"]].append(r)

    random.seed()
    selections = {}
    all_selected_emails = []

    for college, members in groups.items():
        clean = dedupe_by_email_or_unity(members)
        n = min(PER_COLLEGE, len(clean))
        pick = clean if n == len(clean) else random.sample(clean, n)
        pick.sort(key=lambda x: (x["last_name"].lower(), x["first_name"].lower()))
        selections[college] = pick
        all_selected_emails.extend([p["email"] for p in pick])

    # Write text file grouped by college
    out_txt = Path(OUTPUT_TXT)
    with out_txt.open("w", encoding="utf-8") as f:
        for college in sorted(selections.keys()):
            picked = selections[college]
            if not picked:
                continue
            f.write(f"=== {college} (selected {len(picked)}) ===\n")
            for r in picked:
                name = f"{r['first_name']} {r['last_name']}".strip()
                f.write(f"{name} <{r['email']}>  [unity_id: {r['unity_id']}]\n")
            f.write("\n")
    print(f"✅ Wrote grouped selections to {out_txt}")

    # Write flat CSV of all selected emails
    out_csv = Path(OUTPUT_CSV)
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for email in all_selected_emails:
            writer.writerow([email])
    print(f"✅ Wrote flat email list to {out_csv}")

if __name__ == "__main__":
    main()