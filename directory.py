from ldap3 import Server, Connection, ALL, SUBTREE
from dotenv import load_dotenv
import os
# Remove the parameter from load_dotenv if you have issues running in a Windows environment
load_dotenv(dotenv_path="user.env", override=True)

password = os.getenv("PASSWORD")
user = os.getenv("USER")

# AD host with SSL on port 636
server = Server("ldaps.wolftech.ad.ncsu.edu", port=636, use_ssl=True, get_info=ALL)

# Use UPN (unityid@ncsu.edu) for bind

conn = Connection(server, user=user, password=password, auto_bind=True)

print("✅ Successfully bound to LDAP!")

search_base='DC=wolftech,DC=ad,DC=ncsu,DC=edu',
search_filter="(&(objectClass=user)(memberOf=CN=WT-NCSU-Students-Undergraduate,OU=Managed Groups,OU=NCSU,DC=wolftech,DC=ad,DC=ncsu,DC=edu))"
search_scope=SUBTREE
attributes=['sAMAccountName', 'givenName', 'sn', 'mail', 'ncsuCampusID', 'memberOf']

all_entries = []

page_size = 5000
cookie = None
while True:
    conn.search(
        search_base,
        search_filter,
        search_scope=SUBTREE,
        attributes=attributes,
        paged_size=page_size,
        paged_cookie=cookie
    )
    all_entries.extend(conn.entries)
    cookie = conn.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
    if not cookie:
        break

print(all_entries[0])

print(f"Total undergrads found: {len(all_entries)}")


