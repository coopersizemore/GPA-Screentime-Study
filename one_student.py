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

student_first = "Ally"
student_last = "Waddell"


conn.search(
    search_base="DC=wolftech,DC=ad,DC=ncsu,DC=edu",
    search_filter=f"(&(givenName={student_first})(sn={student_last}))",
    search_scope=SUBTREE,
    attributes=["*"]
)

for entry in conn.entries:
    print(entry)
