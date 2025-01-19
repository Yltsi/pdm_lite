# PDM Lite

## Sovelluksen toiminnot

* Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
* Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan kokoonpanoja, sekä osia.
* Käyttäjä pystyy lisäämään kuvia kokoonpanoihin ja osiin.
* Käyttäjä pystyy lisäämään muokkaamaan kokoonpanojen rakenteita.
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
```

Voit käynnistää sovelluksen näin:

```
$ flask run
```