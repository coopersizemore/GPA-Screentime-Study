from ldap3 import Server, Connection, ALL, SUBTREE
from dotenv import load_dotenv
import os

load_dotenv()
password = os.getenv("PASSWORD")
user = os.getenv("USER")

# AD host with SSL on port 636
server = Server("ldaps.wolftech.ad.ncsu.edu", port=636, use_ssl=True, get_info=ALL)

# Use UPN (unityid@ncsu.edu) for bind

conn = Connection(server, user=user, password=password, auto_bind=True)

print("✅ Successfully bound to LDAP!")

group_to_list = {
    'CN=WT-CSC-Computer Science - Students,OU=Managed Groups,OU=NCSU,DC=wolftech,DC=ad,DC=ncsu,DC=edu': [],
    'CN=WT-COEDEAN-All COE users,OU=Managed Groups,OU=NCSU,DC=wolftech,DC=ad,DC=ncsu,DC=edu': [],
}

# The base of the search
search_base='DC=wolftech,DC=ad,DC=ncsu,DC=edu',
# Filter for students in the undergraduate group
search_filter="(&(objectClass=user)(memberOf=CN=WT-NCSU-Students-Undergraduate,OU=Managed Groups,OU=NCSU,DC=wolftech,DC=ad,DC=ncsu,DC=edu))"
search_scope=SUBTREE
# Retrieve the account name (unityid), first name, last name, email, campus ID, and group memberships
attributes=['sAMAccountName', 'givenName', 'sn', 'mail', 'ncsuCampusID', 'memberOf']

all_entries = []

# Implement paging to retrieve all entries
# by only getting 5000 values at a time
# page_size = 5000
# cookie = None
# while True:
#     conn.search(
#         search_base,
#         search_filter,
#         search_scope=SUBTREE,
#         attributes=attributes,
#         paged_size=page_size,
#         paged_cookie=cookie
#     )
#     all_entries.extend(conn.entries)
#     cookie = conn.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
#     if not cookie:
#         break

# for entry in all_entries:
#     for group in group_to_list:
#         if group in entry.memberOf:
#             group_to_list[group].append(entry)

# print(f"Total undergrads found: {len(all_entries)}")
# for group in group_to_list:
#     print(f"{group}: {len(group_to_list[group])} students")

# major_groups = []
# conn.search(
#     search_base="OU=Managed Groups,OU=NCSU,DC=wolftech,DC=ad,DC=ncsu,DC=edu",
#     search_filter="(&(objectClass=group)(cn=*UNDERGRAD*))",
#     attributes=["cn", "member"]
# )
# for g in conn.entries:
#     major_groups.append({
#         "group_name": g.cn.value
#     })

# print(major_groups)

conn.search(
    search_base="OU=Managed Groups,OU=NCSU,DC=wolftech,DC=ad,DC=ncsu,DC=edu",
    search_filter="(&(objectClass=group)(|(cn=*Undergrad*)(cn=*Students*)))",
    search_scope=SUBTREE,
    attributes=["cn"]
)

groups = [entry.cn.value for entry in conn.entries]

# --- STEP 2: Filter out noise groups ---
def is_major_group(name: str) -> bool:
    """Heuristic filter: keep only major/program-related undergrad groups."""
    name_lower = name.lower()
    noise = [
        "admissions", "access", "committee", "services",
        "misc", "test", "all people", "all students"
    ]
    if any(bad in name_lower for bad in noise):
        return False
    good = ["undergrad", "undergraduate", "undergrads", "students"]
    return any(good_word in name_lower for good_word in good)

major_groups = [g for g in groups if is_major_group(g)]

print(f"Found {len(major_groups)} candidate major groups.")

# --- STEP 3: Build dictionary {major_name: roster_of_students} ---
majors = {}

for cn in major_groups:
    conn.search(
        search_base="OU=Managed Groups,OU=NCSU,DC=wolftech,DC=ad,DC=ncsu,DC=edu",
        search_filter=f"(cn={cn})",
        attributes=["member"]
    )
    if conn.entries:
        members = conn.entries[0].member.values if "member" in conn.entries[0] else []
        majors[cn] = members

print(f"Built roster for {len(majors)} majors.")

# Example: show 3 majors with student counts
for m, students in list(majors.items()):
    print(f"{m}: {len(students)} students")

# CN=WT-CS-College of Agriculture and Life Sciences,OU=Managed Groups,OU=NCSU,DC=wolftech,DC=ad,DC=ncsu,DC=edu
# CN=WT-COEDEAN-All COE users,OU=Managed Groups,OU=NCSU,DC=wolftech,DC=ad,DC=ncsu,DC=edu
# CN=PERSONA-PCOMIT.undergrads,OU=Managed Groups,OU=NCSU,DC=wolftech,DC=ad,DC=ncsu,DC=edu
