OffenesParlament
================

OffenesParlament ist eine Webseite, welche die Arbeit des Bundestags und
Bundesrats transparent und nachvollziehbar machen soll. Der Schwerpunkt liegt 
dabei auf den laufenden Arbeitsprozessen des Parlaments - nicht auf dem
Abstimmungsverhalten einzelner Abgeordneter oder dem Inhalt der Dokumente.

Dieses README befasst sich nur mit den technischen Aspekten der Seite, für 
weitere inhaltliche Informationen besuche: http://offenesparlament.de.

Installation
------------

OffenesParlament ist eine einfach Python-Anwendung auf der Basis von
Flask. Systemvoraussetzungen sind daher Python, PostgreSQL sowie das 
Kommandozeilen-Programm ``pdftohtml``, Teil der ``poppler-utils``. Zudem
benötigt die Anwendung eine Apache Solr-Instanz für Volltextsuche, die
per HTTP angesprochen wird.

Die Installation sollte immer innerhalb eines ``virtualenv`` erfolgen::

  virtualenv pyenv
  source pyenv/bin/activate
  git clone git@github.com:pudo/offenesparlament.git
  pip install -r offenesparlament/pip-requirements.txt
  
Alle Einstellungen werden in einer Python-Datei abgelegt. Die Datei 
kann aus den Standard-Einstellungen abgeleitet werden und wird per 
Umgebungsvariable gesetzt::

  cp offenesparlament/offenesparlament/default_settings.py settings.py
  # edit the file to set relevant values like DB strings.
  PARLAMENT_SETTINGS=`pwd`/settings.py
  export PARLAMENT_SETTINGS

In der Konfigurationsdatei werden zwei Datenbanken benannt. Eine davon
ist die Staging-Datenbank (ETL_URL), in der Daten aus den Scrapern
deponiert und transformiert werden. Die andere ist die
Produktivdatenbank, aus der sich das Frontend der Webseite speist. Beide
Datenbanken sollten mit dem Encoding "UTF-8" angelegt werden.

Datenextraktion
---------------

Der Kern von OffenesParlament sind die unterschiedlichen Scraper, die 
Informationen von den Webseiten des Bundestags beziehen und miteinander
verknüpfen. Die Scraper sind in mehrere Stufen unterteilt, die beim 
initialen Abruf der Daten ein der folgenden Reihenfolge ausgeführt
werden sollten:

* ``gremien`` lädt Informationen über die Ausschüsse des Bundestags.
* ``personen`` extrahiert Informationen über Abgeordnete. Andere
  Personen, etwa Mitglieder des Bundesrats und der Regierung werden 
  auch durch andere Stufen hinzugefügt. 
* ``abstimmungen`` extrahiert die Protokolle namentlicher Abstimmungen.
  Das Auslesen der PDF-Dateien erfordert ``pdftohtml``.
* ``transcripts`` lädt sowohl die Plenarprotokolle einzelner
  Bundestagssitzungen wie auch die WebTV-Aufzeichnungen der einzelnen 
  Reden. Beide Datensätze werden verknüpft, sodass eine strukturierte
  Form der Protokolle bereit steht.
* ``ablaeufe`` sind die schriftlichen Vorgänge des Bundestags und 
  Bundesrats. Sie umfassen Anfragen, Anträge und Gesetzesentwürfe.

Jede dieser Stufen kann über das ``manage.py``-Skript ausgeführt
werden::

  python offenesparlament/offenesparlament/manage.py gremien

Alle Stufen verfügen über einige Parameter:

* ``-f``, ``--force`` erzwingt das erneute Laden der Daten, auch wenn 
  diese unverändert sind.
* ``-t``, ``--threaded`` teilt die Arbeit auf mehrere Threads auf.
* ``-p``, ``--preload`` vermeidet das Laden einer Referenzdatei, die 
  kleine Operationen um einige Sekunden verzögert.
* ``-u``, ``--url`` vermeidet das Laden aller Daten und bezieht nur
  einen Eintrag, der per URL spezifiziert wird. 

Der ``-u``-Paramter kann wie folgt verwendet werden::

  python [..]/manage.py person -f -u http://www.bundestag.de/xml/mdb/A/ackermann_jens.xml

Oder::

  python [..]/manage.py ablaeufe -f -u http://dipbt.bundestag.de/extrakt/ba/WP17/242/24215.html
  
Alle Stufen können gemeinsam durch dem ``update``-Befehl ausgeführt 
werden::
  
  python [..]/manage.py update

Einige andere Befehle stehen ebenfalls zur Verfügung. 

* ``dumpindex`` beseitigt den gesamten Solr-Index zu Debug-Zwecken.
* ``aggregate`` generiert einige Statistiken. Es sollte nach dem
  Daten-Update ausgeführt werden. 
* ``notify`` liest die Abonnenten-Listen aus und verschickt E-Mails
  an alle zutreffenden Empfänger.

Webseite
--------

Um die Webseite auszuführen, kann das folgende Kommando genutzt werden::

  python [..]/manage.py runserver

Um einen Produktiv-Server zu betreiben sollte allerding eine andere
Umgebung genutzt werden, z.B. ``gunicorn``.

Kontakt
-------

* Friedrich Lindenberg <friedrich.lindenberg@okfn.org>
* http://lists.okfn.org/mailman/listinfo/offenes-parlament

Der Code von OffenesParlament steht unter der Affero GPL v3-Lizenz. Der Text
der Lizenz ist unter http://www.gnu.org/licenses/agpl.html einsehbar.


