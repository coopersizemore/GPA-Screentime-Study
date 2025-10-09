# export_students.py
from ldap3 import Server, Connection, ALL, SUBTREE
from dotenv import load_dotenv
from pathlib import Path
import os, csv, re

# --- Config ---
LDAP_HOST = "ldaps.wolftech.ad.ncsu.edu"
BASE_DN   = "DC=wolftech,DC=ad,DC=ncsu,DC=edu"
FILTER    = "(&(objectClass=user)(memberOf=CN=WT-NCSU-Students-Undergraduate,OU=Managed Groups,OU=NCSU,DC=wolftech,DC=ad,DC=ncsu,DC=edu))"
ATTRS     = [
    "sAMAccountName",  # Unity ID
    "givenName",       # First name
    "sn",              # Last name
    "mail",            # Email
    "ncsuCampusID",    # Campus ID
    "memberOf"         # Group memberships
]

# --- Creds ---
load_dotenv(Path(__file__).with_name("user.env"), override=True)
user = os.getenv("LDAP_USER") or os.getenv("USER")
password = os.getenv("LDAP_PASSWORD") or os.getenv("PASSWORD")
if not user or not password:
    raise RuntimeError("Missing LDAP_USER/LDAP_PASSWORD (or USER/PASSWORD) in user.env")

# --- Connect ---
server = Server(LDAP_HOST, port=636, use_ssl=True, get_info=ALL)
conn = Connection(server, user=user, password=password, auto_bind=True)
print("✅ Bound to LDAP")

# --- Paged search ---
all_entries = []
page_size = 5000
cookie = None
while True:
    conn.search(
        search_base=BASE_DN,
        search_filter=FILTER,
        search_scope=SUBTREE,
        attributes=ATTRS,
        paged_size=page_size,
        paged_cookie=cookie
    )
    all_entries.extend(conn.entries)
    cookie = conn.result.get("controls", {}).get("1.2.840.113556.1.4.319", {}).get("value", {}).get("cookie")
    if not cookie:
        break

print(f"Found {len(all_entries)} undergrads")

# --- Helpers ---
COLLEGE_MAP = [
    (re.compile(r'\bPCOM\b|poole', re.I), "Poole College of Management"),
    (re.compile(r'\bCOE\b|engineer', re.I), "College of Engineering"),
    (re.compile(r'\bCALS\b|agricult|life\s*sciences', re.I), "College of Agriculture and Life Sciences"),
    (re.compile(r'\bCHASS\b|humanities|social\s*sciences', re.I), "Humanities & Social Sciences"),
    (re.compile(r'\bCOS\b|^science(s)?$|college[-\s]*of\s*sciences', re.I), "College of Sciences"),
    (re.compile(r'\bCNR\b|natural\s*resources', re.I), "College of Natural Resources"),
    (re.compile(r'design', re.I), "College of Design"),
    (re.compile(r'education', re.I), "College of Education"),
    (re.compile(r'textile', re.I), "Wilson College of Textiles"),
    (re.compile(r'veterinary', re.I), "College of Veterinary Medicine"),
    (re.compile(r'graduate', re.I), "The Graduate School"),
]

def extract_cns(member_of_values):
    vals = member_of_values if isinstance(member_of_values, list) else ([member_of_values] if member_of_values else [])
    cns = []
    for v in vals:
        if not v:
            continue
        cn = v.split(",", 1)[0]
        if cn.startswith("CN="):
            cn = cn[3:]
        cns.append(cn)
    return cns

def derive_college(entry):
    try:
        cns = extract_cns(entry["memberOf"].value)
    except Exception:
        cns = []
    for cn in cns:
        for pat, label in COLLEGE_MAP:
            if pat.search(cn):
                return label
    return ""  # or "Unknown"

def get(entry, attr):
    try:
        val = entry[attr].value
        if isinstance(val, list):
            return ";".join(str(x) for x in val)
        return "" if val is None else str(val)
    except Exception:
        return ""

# --- Write CSV (single college, no memberOf column) ---
out_path = "st370_undergrads_college.csv"
with open(out_path, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["unity_id", "first_name", "last_name", "email", "campus_id", "college"])
    for e in all_entries:
        w.writerow([
            get(e, "sAMAccountName"),
            get(e, "givenName"),
            get(e, "sn"),
            get(e, "mail"),
            get(e, "ncsuCampusID"),
            derive_college(e),
        ])

print(f"📄 Wrote {out_path}")