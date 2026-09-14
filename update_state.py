import json
import datetime

with open('/home/iliko/.hermes/skills/free-model-rotator/state.json', 'r') as f:
    data = json.load(f)

# Filter out xiaomi from fallback_providers
data['fallback_providers'] = [p for p in data['fallback_providers'] if p.get('provider') != 'xiaomi']

data['last_updated'] = datetime.datetime.now().isoformat()

with open('/home/iliko/.hermes/skills/free-model-rotator/state.json', 'w') as f:
    json.dump(data, f, indent=2)

print('Updated state.json: removed xiaomi from free fallback providers')