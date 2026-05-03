# reseptit

## toiminnot
* Käyttäjä voi tehdä tunnuksen ja kirjautua sisään
* Käyttäjä voi julkaista, muokata ja poistaa reseptejä
* Käyttäjä näkee sovellukseen lisätyt reseptit
* Käyttäjä voi etsiä reseptejä hakusanalla tai luokittelujen perusteella
* Käyttäjä voi lisätä resepteihin arvostelun yhdestä viiteen ja tekstiarvostelun
* Käyttäjä voi luokitella reseptejään lisäämällä useita luokitteluja: esimerkiksi italialainen, leivonnainen, kala
* Sovelluksessa on käyttäjäsivut, jotka sisältävät tilastoja käyttäjästä käyttäjän lisäämien reseptien ja arvostelujen määrät ja käyttäjän lisäämien reseptien arvosanojen keskiarvon ja kaikki käyttäjän lisäämät reseptit
* Käyttäjä voi etsiä reseptejä myös tietyn käyttäjän reseptejä käyttäjäsivun kautta

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

### Käyttäminen
#### Tunnuksen luominen ja kirjautuminen
Käyttäjätunnuksen voi luoda painamalla Rekisteröidy- linkkiä tai osoitteessa "/register".
Käyttäjä voi kirjautua sisään painamalla Kirjaudu sisään- linkkiä tai osoitteessa "/login".

#### Reseptien julkaiseminen
Jokainen käyttäjä voi kirjauduttuaan sisään luoda reseptin painamalla Luo resepti- linkkiä tai osoitteessa "/create".
Reseptin julkaistuaan reseptiä voi muokata Muokkaa- linkkiä painamalla tai "/edit/ [reseptin id] " osoitteessa.
Reseptin voi poistaa Poista- linkkiä painamalla tai "/remove/ [reseptin id] " osoitteessa.

#### Reseptien lukeminen ja arvostelu
Reseptejä voi lukea painamalla reseptin linkkiä tai osoitteessa "/recipe/ [reseptin id]".
Reseptiin voi lisätä arvostelun, jos on kirjautunut sisään reseptin sivulla arvostelut kohdassa.
Arvosteluun kuuluu tähdet yhdestä viiteen ja mahdollinen kommentti.
Reseptin sivulla voi nähdä itsensä ja muiden arvostelut reseptille.

#### Hakuominaisuudet
Reseptejä voi hakea hakusanan perusteella etusivulla tai hakusanan ja kategorioiden perusteella painamalla linkistä "hae kategorioiden mukaan" tai osoitteessa "/search". Tämä tarkempi haku avautuu myös hakemalla jotain.
Hakusanahaku toimii niin, että tämä hakee reseptejä, joissa on sanoja, joita hakukenttään on kirjoittanut.
Kategorioiden perusteella hakeminen toimii niin, että vain ne reseptit, joissa on valitut kategoriat näkyvät.
Käyttäjäsivuilla on hakukenttä, jolla voi hakea tietyn käyttäjän julkaisemia reseptejä hakusanan perusteella. Kategorioiden perusteella hakeminen toimii vastaavalla tavalla.
