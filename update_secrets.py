import requests, yaml, subprocess, os, pytz, sys
from pathlib import Path
from datetime import datetime
from socket import socket, AF_INET, SOCK_STREAM

bw_port = 42666
note_id = "220ddfa8-9820-49a9-b525-af2d0002b861"

api_url = f"http://localhost:{bw_port}"

def is_port_in_use(port: int) -> bool:
    try:
        with socket(AF_INET, SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0
    except:
        return True
def unlock_loop():
    try:
        r = requests.Response()
        while r.status_code != 200:
            bw_pass = ""
            while bw_pass == "":
                bw_pass = input("BW pass? ")
            r = requests.post(f"{api_url}/unlock",json={'password':bw_pass})
            if r.status_code != 200:
                message = r.json()['message']
                print(f"ERROR: {message}")
    except KeyboardInterrupt:
        print("Cancelling unlock")
        sys.exit(1)

if not is_port_in_use(bw_port):
    try:
        bw_server = subprocess.Popen(['bw','serve','--port',str(bw_port)])
    except FileNotFoundError:
        print("ERROR: 'bw' binary not found!")
        sys.exit(1)
    unlock_loop()
else:
    r = requests.get(api_url + '/status')
    response = r.json()['data']['template']
    if response['status'] == 'locked':
        unlock_loop()
    else:
        print("Bitwarden vault already unlocked; proceeding")
    r = requests.post(f"{api_url}/sync")
    
r = requests.get(f"{api_url}/object/item/{note_id}")
bw_note_info = r.json()['data']
bw_secrets = {x['name']:x['value'] for x in bw_note_info['fields']}

if not os.path.exists('secrets.yaml'):
    with open('secrets.yaml','w') as f:
        yaml.dump(bw_secrets,f,yaml.Dumper)
    print("No secrets file existed, created from Bitwarden")
    sys.exit(0)

with open('secrets.yaml') as f:
    file_secrets = yaml.load(f,yaml.FullLoader)

bw_secret_keys = bw_secrets.keys()
file_secret_keys = file_secrets.keys()
overlaps = [x for x in bw_secret_keys if x in file_secret_keys and file_secrets[x] != bw_secrets[x]]
if len(overlaps) > 0:
    print(f"Found {len(overlaps)} mismatched overlapped keys")
else:
    print("No overlaps, can merge safely!")
file_mtime_raw = datetime.fromtimestamp(Path('secrets.yaml').stat().st_mtime)
central = pytz.timezone('US/Central')
file_mtime = central.localize(file_mtime_raw)
bw_mtime = datetime.fromisoformat(bw_note_info['revisionDate'])

all_secrets = {}
if bw_mtime > file_mtime:
    print("Bitwarden is newer, will overwrite changes from Bitwarden")
    for key in file_secret_keys:
        all_secrets[key] = file_secrets[key]
    for key in bw_secret_keys:
        all_secrets[key] = bw_secrets[key]
else:
    print("Local file is newer, will overwrite changes from local file")
    for key in bw_secret_keys:
        all_secrets[key] = bw_secrets[key]
    for key in file_secret_keys:
        all_secrets[key] = file_secrets[key]
print(f"Local file: {file_mtime}")
print(f"Bitwarden:  {bw_mtime}")

key_count = len(all_secrets.keys())
bw_note_info['fields'] = [{"name":x, "value": all_secrets[x], "type": 1} for x in all_secrets.keys()]
r = requests.put(f"{api_url}/object/item/{note_id}",json=bw_note_info)
if r.status_code == 200 and r.json()['success'] == True:
    print(f"Successfully wrote {key_count} keys to Bitwarden, syncing...")
else:
    print(f"ERROR: {r.text}")
    sys.exit(1)
r = requests.post(f"{api_url}/sync")
if r.status_code == 200 and r.json()['success'] == True:
    print("Successfully synced changes!")
with open('secrets.yaml','w') as f:
    yaml.dump(all_secrets,f,yaml.Dumper)
    print(f"Wrote {key_count} keys to 'secrets.yaml'")
print("Finished!")