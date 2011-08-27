OffenesParlament
================

OffenesParlament ist eine Webplatform, welche die Arbeit des Bundestags und
Bundesrats transparent und nachvollziehbar machen soll. Der Schwerpunkt liegt 
dabei auf den laufenden Arbeitsprozessen des Parlaments - nicht auf dem
Abstimmungsverhalten einzelner Abgeordneter oder dem Inhalt der Dokumente.

Dieses README befasst sich nur mit den technischen Aspekten der Seite, für 
weitere inhaltliche Informationen besuchen Sie: http://offenesparlament.de.

Extract, Transform, Load
------------------------

Die Inhalte der Seite entstammen im wesentlichen zwei Systemen:

* Dem CMS des Bundestags (Profile von Abgeordneten, Ausschüssen und
  Nachrichten)
* Das Dokumenten- und Informationsportal des Bundestags und Bundesrats für
  aktuelle Vorgänge, Links und Beteiligte.

Die Auswertung der Inhalte erfolgt in den folgenden Schritten:

* Extraktion (``offenesparlament.extract``): die Webseiten werden gescraped
  und in einer Instanz der Webstore abgelegt. 
* Transformation (``offenesparlament.transform``): Inhalte werden
  angereichert, Personendaten vereinheitlicht und Texte analysiert.
* Load (``offenesparlament.load``): Daten aus dem Webstore-System werden in
  die eigentliche produktiv-Datenbank geladen.

Kontakt
-------

* Friedrich Lindenberg <friedrich.lindenberg@okfn.org>
* http://lists.okfn.org/mailman/listinfo/offenes-parlament

Lizenz
------

Der Code von OffenesParlament steht unter der Affero GPL v3-Lizenz. Der Text
der Lizenz ist unter http://www.gnu.org/licenses/agpl.html einsehbar.


