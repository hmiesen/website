import json
import sqlite3

# If you want a direct redirect, do not add a title. If you want to redirect with a message, do use a title. 
REDIRECTS = {
    "/jobs": {
        "url": "https://docs.google.com/document/d/e/2PACX-1vRZ4jhEafDjxErgAtjnjCkRFj1R0NGSEW4Yz6-nFXwdPk_5PLSfwnrRgLIq1iF_ZA/pub",
        "title": "the Tilburg Science Hub Job Page"
    },
    "/lab": {
        "url": "https://github.com/tilburgsciencehub/onboard/wiki",
        "title": "the wiki page for the lab"
    },
    "/onboarding": {
        "url": "https://github.com/tilburgsciencehub/onboard/wiki",
        "title": "the onboarding wiki page"
    }
}

# Reads all redirects from the SQLite database and returns them as a JSON object.
# param db_path: Path to the SQLite database file.
# return: JSON object with alias as the key and {url, title} as values.
def get_redirects_as_json(db_path):
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT alias, path, title FROM redirects")
    rows = cursor.fetchall()
    redirects = {}
    base_url = "https://tilburgsciencehub.com"

    for alias, path, title in rows:
        redirects[alias] = {
            "url": f"{base_url}/{path}" if not path.startswith("http") else path
        }

    conn.close()
    REDIRECTS.update(redirects)
    
    return redirects

# Read redirects from database
db_path = "tsh.db"  # Adjust to your actual database file
redirects_json = get_redirects_as_json(db_path)
