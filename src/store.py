import asyncio

from flask import (
    Blueprint, flash, redirect, render_template, request, session, url_for
)

from . import utils


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
    skins_data = asyncio.run(utils.get_skins_from_api())

    if skins_data == "auth_failure":
        flash("Authentication failed. Please try again.")
        return redirect(url_for("store.store_homepage"))
    
    if skins_data == "error":
        flash("An error occurred. Please try again later.")
        return redirect(url_for("store.store_homepage"))
        
    return render_template('store.html', data=skins_data)
