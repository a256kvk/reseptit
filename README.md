# reseptit

## toiminnot
* Käyttäjä voi tehdä tunnuksen ja kirjautua sisään
* Käyttäjä voi julkaista, muokata ja poistaa reseptejä
* Käyttäjä voi lisätä reseptiin kuvan
* Käyttäjä näkee sovellukseen lisätyt reseptit
* Käyttäjä voi etsiä reseptejä hakusanalla tai luokittelujen perusteella
* Käyttäjä voi lisätä resepteihin arvostelun yhdestä viiteen ja tekstiarvostelun
* Käyttäjä voi luokitella reseptejään lisäämällä useita luokitteluja: esimerkiksi italialainen, leivonnainen, kala

## Valmiina olevat toiminnot
* Käyttäjä voi tehdä tunnuksen ja kirjautua sisään
* Käyttäjä voi julkaista, muokata ja poistaa reseptejä
* Käyttäjä näkee sovellukseen lisätyt reseptit
* Käyttäjä voi lisätä resepteihin arvostelun yhdestä viiteen ja tekstiarvostelun
* Käyttäjä voi etsiä luokittelujen perusteella
* Käyttäjä voi luokitella reseptejään lisäämällä useita luokitteluja: esimerkiksi italialainen, leivonnainen, kala
* Sovelluksessa on käyttäjäsivut, jotka sisältävät tilastoja käyttäjästä esimerkiksi käyttäjän lisäämien reseptien ja arvostelujen määrät ja käyttäjän lisäämien reseptien arvosanojen keskiarvon ja kaikki käyttäjän lisäämät reseptit

## Osittain valmina olevat toiminnot
* Käyttäjä voi etsiä reseptejä hakusanalla

## Testaus
```
git clone https://github.com/a256kvk/reseptit.git
cd reseptit
python3 -m venv venv
source venv/bin/activate
pip install flask
sqlite3 database.db < schema.sql
sqlite3 database.db < add_categories.sql
cp config_test.py config.py
flask run
```
