import aiohttp
import json
import re
import ssl

from flask import session
from multidict import MultiDict


async def get_skins_from_api():
    try:
        ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ctx.set_ciphers("DEFAULT@SECLEVEL=1")
        conn = aiohttp.TCPConnector(ssl=ctx)

        riot_session = aiohttp.ClientSession(connector=conn, headers=MultiDict({
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "application/json, text/plain, */*"
        }))
        
        user_agent = "RiotClient/51.0.0.4429735.4381201 rso-auth (Windows;10;;Professional, x64)"
        data = {
            'client_id': 'play-valorant-web-prod',
            'nonce': '1',
            'redirect_uri': 'https://playvalorant.com/opt_in',
            'response_type': 'token id_token',
        }

        headers = {'Content-Type': 'application/json', 'User-Agent': user_agent }

        await riot_session.post('https://auth.riotgames.com/api/v1/authorization', json=data, headers=headers)

        data = {
            'type': 'auth',
            'username': session.get('RIOT_USERNAME'),
            'password': session.get('RIOT_PASSWORD')
        }

        async with riot_session.put('https://auth.riotgames.com/api/v1/authorization', json=data, headers=headers) as r:
            data = await r.json()

        # Handle user authentication failure
        if "error" in data.keys():
            await riot_session.close()
            return data["error"]
        
        pattern = re.compile('access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)')
        data = pattern.findall(data['response']['parameters']['uri'])[0]
        access_token = data[0]

        headers = {
            'Authorization': f'Bearer {access_token}',
        }
        async with riot_session.post('https://entitlements.auth.riotgames.com/api/token/v1', headers=headers, json={}) as r:
            data = await r.json()
        entitlements_token = data['entitlements_token']

        headers['X-Riot-Entitlements-JWT'] = entitlements_token

        async with riot_session.post('https://auth.riotgames.com/userinfo', headers=headers, json={}) as r:
            data = await r.json()
        user_id = data['sub']
    
        # Request
        async with riot_session.get(f'https://pd.EU.a.pvp.net/store/v2/storefront/{user_id}', headers=headers) as r:
            data = json.loads(await r.text())

        data_store = data["SkinsPanelLayout"]["SingleItemOffers"]

        skins_data = []

        for skin in data_store:
            async with riot_session.get(f"https://valorant-api.com/v1/weapons/skinlevels/{skin}") as r:
                skin = json.loads(await r.text())["data"]
            
            async with riot_session.get(f'https://pd.EU.a.pvp.net/store/v1/offers/', headers=headers) as r:
                offers = json.loads(await r.text())["Offers"]
            
            skin["price"] = get_skin_price_from_json(offers, skin["uuid"])
            skins_data.append(skin)
        
    except Exception as e:
        print(e)
        await riot_session.close()
        return "error"

    await riot_session.close()

    return skins_data


def get_skin_price_from_json(offers, skin_id):
    for item in offers:
        if item["OfferID"] == skin_id:
            return item["Cost"]["85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741"]