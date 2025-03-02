# PDM Lite

## Sovelluksen toiminnot

Sovelluksen on tarkoitus toimia kevyenä PDM, eli Product Data Management sovelluksena. PDM sovelluksia käytetään tietolähteenä tuotteisiin liittyvälle datalle, kuten suunnitteludokumenteille, valmistusohjeille, kokoonpanotiedoille, materiaalitietoihin ja laadunvarmistustietoihin. PDM:ää voidaan myös käyttää säilömään tilauskohtaisia toimitustietoja, esimerkiksi kokoonpanokuvia ja niiden BOM, eli Bill of Material tietoja.
Tämän sovelluksen on tarkoitus toimiessaan pystyä seuraaviin asioihin:

* Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
* Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan kokoonpanoja, sekä osia.
* Käyttäjä pystyy lisäämään ja muokkaamaan kokoonpanojen rakenteita (BOM).
* Käyttäjä näkee sovellukseen lisätyt kokoonpanot ja osat.
* Käyttäjä pystyy etsimään kokoonpanoja ja osia hakusanalla.
* Sovelluksessa on käyttäjäsivut, joilla näkyy kokoonpanojen rakenteet.
* Käyttäjä pystyy avaamaan kokoonpanoja ja tarkastamaan niiden BOM listan.
* Käyttäjä pystyy tarkistamaan revisiohistorian osista.
* Statistic sivulta käyttäjä pystyy tarkistamaan erinäisiä tietoja esimerkiksi käytetyimmistä osista eri kokoonpanoissa.

## Sovelluksen asennus

Asenna `flask`-kirjasto:

```
$ pip install flask
```

Luo tietokannan taulut ja lisää alkutiedot:

```
$ sqlite3 database.db < schema.sql

Jos haluat testata sovellusta generoidulla datalla voit suorittaa seuraavan komennon:

$ python3 seed.py

```

Voit käynnistää sovelluksen näin:

```
$ flask run
```

## Sovelluksen nykyinen tilanne
* Sovellus toimii toiminnossa selitetyllä tavalla. Valitettavasti kuvien lisäystä ohjelmaan en ehtinyt lisäämään ajan puutteessa.. Tämä olisi erittäin tärkeä ominaisuus PDM sovellukselle. Samoin tuoterakenteen tulostus ominaisuus pois lopullisesta palautuksesta. Käytettävyydessä pahin ongelma on se, että tietokannan sivutus jäi lisäämättä sovellukseen. Etusivu nyt näyttää kaikki hakutulokset, joten suurella tietokannalla käyttö alkaa olemaan vaivanloista. Idea TAB elementtien käytöstä vaikeutti sivutuksen lisäämistä, enkä saanut sitä toimimaan. Järkevintä olisi ollut jakaa search ja add omiksi sivuikseen. Muuten indeksi nopeuttaa toimintaa.

* seed.py antaa seuraavanlaista dataa, jonka seed.py tallentaa myös projektin kansioon nimellä performance_results.txt:

PDM Lite Performance Test Results
================================

Database size: 434.32 MB
Total items: 1600

Count all items:
  Time: 0.0001 seconds
  Rows: 1

Count items by type:
  Time: 0.0001 seconds
  Rows: 3

Find assemblies with most components:
  Time: 0.0003 seconds
  Rows: 10

Find most used components:
  Time: 0.0005 seconds
  Rows: 10

Complex join with filtering:
  Time: 0.0000 seconds
  Rows: 14

Search by description (without index):
  Time: 0.0002 seconds
  Rows: 8

Get user contribution statistics:
  Time: 0.0001 seconds
  Rows: 10
