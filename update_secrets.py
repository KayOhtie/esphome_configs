import requests, json, yaml, subprocess, os, pathlib, datetime

try:
    bw_server = subprocess.Popen(['bw','serve','--port','42069'])
    api_url = "http://localhost:42069"
except FileNotFoundError:
    print("ERROR: 'bw' binary not found!")

r = requests.Response()
while r.status_code != 200:
    bw_pass = ""
    while bw_pass == "":
        bw_pass = input("BW pass? ")
    r = requests.post(api_url+'/unlock',json={'password':bw_pass})
    if r.status_code != 200:
        message = r.json()['message']
        print(f"ERROR: {message}")

r = requests.get(api_url + '/object/item/220ddfa8-9820-49a9-b525-af2d0002b861')
bw_secrets = {x['name']:x['value'] for x in r.json()['data']['fields']}

if os.path.exists('secrets.yaml'):
    with open('secrets.yaml') as f:
        file_secrets = yaml.load(f,yaml.FullLoader)
    file_mtime = pathlib.Path('secrets.yaml').stat().st_mtime
    file_mdatetime = datetime.datetime.fromtimestamp(file_mtime)
    