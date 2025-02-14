# redirects_config.py
import json

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

# Read and parse JSON properly
with open('redirect_aliases.json', 'r', encoding="utf-8") as f:
    redirect_aliases = json.load(f)  # ✅ Correct way to load JSON file

# Merge the dictionaries
REDIRECTS.update(redirect_aliases)

# Print the updated REDIRECTS
print(json.dumps(REDIRECTS, indent=4))