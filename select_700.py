# select_700.py
import csv
import random
from pathlib import Path

INPUT_CSV = "st370_undergrads_college.csv"
OUTPUT_CSV = "email_list.csv"
TARGET_N = 700  # number to pick overall

def load_unique_emails(path: Path):
    emails = []
    seen = set()
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            email = (r.get("email") or "").strip()
            if not email:
                continue
            key = email.lower()
            if key not in seen:
                seen.add(key)
                emails.append(email)
    return emails

def main():
    input_path = Path(INPUT_CSV)
    if not input_path.exists():
        raise FileNotFoundError(f"Could not find {INPUT_CSV} in {Path.cwd()}")

    emails = load_unique_emails(input_path)
    if not emails:
        raise RuntimeError("No emails found in input CSV.")

    # random sample up to TARGET_N (without replacement)
    n = min(TARGET_N, len(emails))
    random.seed()  # use system entropy
    selected = emails if n == len(emails) else random.sample(emails, n)

    # write one email per row
    out_path = Path(OUTPUT_CSV)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for e in selected:
            writer.writerow([e])

    print(f"✅ Selected {len(selected)} emails and wrote to {out_path}")

if __name__ == "__main__":
    main()