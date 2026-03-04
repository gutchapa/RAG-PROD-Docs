import json

with open('/root/.openclaw/openclaw.json', 'r') as f:
    config = json.load(f)

# Add Brave Search API key
config['skills']['entries']['brave-search'] = {
    "apiKey": "BSAWI6S_3iEhk9DAQeX-VzAQ7-b391x"
}

with open('/root/.openclaw/openclaw.json', 'w') as f:
    json.dump(config, f, indent=2)

print("Brave Search API key added successfully!")
