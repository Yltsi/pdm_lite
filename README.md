# PDM Lite

## Sovelluksen toiminnot

Sovelluksen on tarkoitus toimia kevyenä PDM, eli Product Data Management sovelluksena. PDM sovelluksia käytetään tietolähteenä tuotteisiin liittyvälle datalle, kuten suunnitteludokumenteille, valmistusohjeille, kokoonpanotiedoille, materiaalitietoihin ja laadunvarmistustietoihin. PDM:ää voidaan myös käyttää säilömään tilauskohtaisia toimitustietoja, esimerkiksi kokoonpanokuvia ja niiden BOM, eli Bill of Material tietoja.
Tämän sovelluksen on tarkoitus toimiessaan pystyä seuraaviin asioihin:

* Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
* Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan kokoonpanoja, sekä osia.
* Käyttäjä pystyy lisäämään kuvia kokoonpanoihin ja osiin.
* Käyttäjä pystyy lisäämään ja muokkaamaan kokoonpanojen rakenteita (BOM).
* Käyttäjä näkee sovellukseen lisätyt kokoonpanot ja osat.
* Käyttäjä pystyy etsimään kokoonpanoja ja osia hakusanalla.
* Sovelluksessa on käyttäjäsivut, joilla näkyy kokoonpanojen rakenteet.
* Käyttäjä pystyy avaamaan kokoonpanoja ja osia piirrepuusta.
* Käyttäjä pystyy tulostamaan kokoonpanon BOM listan.

## Sovelluksen asennus

Asenna `flask`-kirjasto:

```
$ pip install flask
```

Luo tietokannan taulut ja lisää alkutiedot:

```
$ sqlite3 database.db < schema.sql
$ sqlite3 database.db < init.sql 
*Init data puuttuu kokonaan*
```

Voit käynnistää sovelluksen näin:

```
$ flask run
```

## Sovelluksen nykyinen tilanne
* Käyttäjä pystyy luomaan tunnukset ja kirjautumaan sovellukseen.
* Kirjautumistiedoilla on omat vaatimuksensa ja virhetilanteessa virheviesti kertoo mikä on vikana tunnuksien luonnissa.
* Kirjautumissivusto kertoo, mikäli käyttäjä yrittää kirjautua väärillä tunnuksilla.
* Seuraavat sivut ovat käytössä, http://127.0.0.1:5000/ /pdm /register
* Sivusto ohjaa virheellisesti /edit_item/*osanumero* Periaatteessa käyttäjä voi mennä tällä hetkellä esimerkiksi osoitteeseen /edit_item/1 muokatakseen kyseistä nimikettä tietokannassa. Muutenkin muutama redirect komento app.py:ssä toimii huonolla logiikalla. Näitä korjataan seuraavissa päivityksissä.
* Käyttäjä näkee kaikki nimikkeet search välilehdellä osoitteessa /pdm
* Flash virhe/onnistumisviestit näkyvät search ja add välilehdellä. Tässä on hieman virheitä
* Käyttäjä pystyy tällä hetkellä hakemaan tietokannan nimikkeitä description nimikkeen mukaan.
* Käyttäjä voi hakea nimikkeitä tyypin mukaan.
* Tietokanta numeroi jokaisen osan/kokoonpanon automaattisesti.