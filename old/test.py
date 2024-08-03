import requests

proxies = {
    'http': 'http://isaqkhag4k-res-country-DE-state-2905330-city-2925533-hold-session-session-66ad06ae31eab:tMWKuVShlInBw2OY@93.190.138.107:9999'
}

pics = requests.get('https://wildbee.pics/site/wb?id=11990959', proxies=proxies)

print(pics)