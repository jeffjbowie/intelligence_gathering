import pdb,requests

urls = [
    'https://aliasinfosec.com/I.Turned.Myself.Into.A.Pickle.Morty',
    'https://aliasinfosec.com/',
]
for u in urls:
    _r = requests.get(u)
    if _r.status_code == 404:
        print("404 Error")
        pdb.set_trace()
    else:
        print(f"SUCCESS **** {_r.text[:256]}")