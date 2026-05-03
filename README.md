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

### Suurten tietomäärien käsittely
Seuraavilla komennoilla voi luoda tietokannan, jossa on suuria tietomääriä. (Komennoissa oletetaan, ettei database.db tiedostoa ole olemassa ennen niiden käyttöä)
```
sqlite3 database.db < schema.sql
sqlite3 database.db < add_categories.sql
python seed.py
```

Tällöin tietokantaan lisätään 10 000 käyttäjää ja 100 000 reseptiä.
Näistä resepteistä tuhat ensimmäistä on ensimmäisen käyttäjän (käyttäjän, jonka id on 1).
Seuraavat tuhat reseptiä ovat toisen käyttäjän (käyttäjän jonka id on 2).
Ensimmäisen käyttäjän resepteillä on suunnilleen miljoona arvostelua, eli noin 1000 arvostelua per resepti.
Toisen käyttäjän resepteillä on noin 100 000 arvostelua, eli noin 100 per resepti.
Loput reseptit ovat muiden käyttäjien reseptejä, ja muilla käyttäjillä on suunnilleen kymmenen reseptiä per käyttäjä. Lisäksi näillä resepteillä on yhteensä suunnilleen miljoona arvostelua, eli noin 10 arvostelua per resepti.

Kaikkien reseptien sivujen lataaminen on erittäin nopeaa ja tapahtuu melkein välittömästi.

Käyttäjän 1 käyttäjäsivun lataaminen kestää ~ 7 sekuntia.bg, koska käyttäjän resepteille on suunnilleen miljoona arvostelua, ja näille täytyy laskea keskiarvo.
Käyttäjällä 2 on suunnilleen 100 reseptiä, joille on yhteensä noin 100 000 arvostelua. Käyttäjän 2 sivun lataaminen ei ole hidasta ja sivu latautuu suunnilleen sekunnissa.
Muilla käyttäjillä on suunnilleen 10 reseptiä per käyttäjä, joilla on suunnilleen kymmenen arvostelua per resepti. Näiden käyttäjien sivut latautuvat lähes silmänräpäyksessä.

Reseptien hakeminen pelkällä hakusanalla tapahtuu melkein välittömästi hakusanasta riippumatta.
Reseptien hakeminen pelkillä kategorioilla tapahtuu valittujen kategorioiden määrästä riippuen neljännessekuntista pariin sekuntiin.
Kun hakee reseptiä hakusanalla ja kategorioilla, niin sivun lataamisen nopeus riippuu hakusanan yleisyydestä ja kategorioiden määrästä. Esimerkiksi yhden kategorian etsiminen hakusanalla, joka on jokaisessa reseptissä ("lol") menee noin sekunti. Hakiessa sanaa ("tuhat") joka on sadassa reseptissä ja vaikka olisi kolme kategoriaa, niin haku tapahtuu noin sekunnissa. Mutta esimerkiksi jos hakee sanaa, joka on kaikissa resepteissä ja seitsemää kategoriaa, niin sivu ei lataudu edes yhdessätoista minuutissa.

## Pylint-raportti
katso [pylint-report.md](pylint-report.md)
