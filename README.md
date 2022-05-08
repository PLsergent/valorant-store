# valorant-store
Web app to know what is in your Valorant store without having to open the game.

## Run locally

Required dependencies:
- python3
- poetry

```
git clone git@github.com:PLsergent/valorant-store.git
cd valorant-store
poetry install
echo "FLASK_APP=src" >> .flaskenv
poetry run flask run
```

## Disclaimer

This app requires the user riot account credentials to work. Even though the creds are stored securely, they'll be read in plain-text by the program, when sending the request to get the tokens from the riot api endpoint. Therefore there is always a risk that the credentials could be exposed. That's why **I recommend to run the app locally only.**

The apis used for the app are **not official** and are not maintained by Riot Games.