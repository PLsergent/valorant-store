from crypt import methods
import os
import functools

import re
import aiohttp
import asyncio
import json

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

bp = Blueprint('store', __name__, url_prefix='/')


@bp.route("/", methods=("GET", "POST"))
def store_homepage():
    if request.method == "POST":
        session["RIOT_USERNAME"] = request.form["rusername"]
        session["RIOT_PASSWORD"] = request.form["pswd"]
        return redirect(url_for("store.store_profile"))

    return render_template("homepage.html")


@bp.route("/store", methods=("GET", "POST"))
def store_profile():
    skins_data =  asyncio.run(run())
    return render_template('store.html', data=skins_data)


async def run():
    riot_session = aiohttp.ClientSession()
    user_agent = "RiotClient/43.0.1.4195386.4190634 rso-auth (Windows; 10;;Professional, x64)"
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
            skins_data.append(json.loads(await r.text())["data"])

    await riot_session.close()

    return skins_data
