# -*- coding: UTF-8 -*-

CHAIRS = [u'Vizepräsidentin', u'Vizepräsident', u'Präsident']

SPEAKER_STOPWORDS = ['ich zitiere', 'zitieren', 'Zitat', 'zitiert',
                     'ich rufe den', 'ich rufe die',
                     'wir kommen zur Frage', 'kommen wir zu Frage', 'bei Frage',
                     'fordert', 'fordern', u'Ich möchte', 
                     'Darin steht', ' Aspekte ', ' Punkte ']


FACTION_MAPS = {
        u"BÜNDNIS 90/DIE GRÜNEN": u"B90/Die Grünen",
        u"DIE LINKE.": u"Die LINKE.",
        u"Bündnis 90/Die Grünen": u"B90/Die Grünen",
        u"Die Linke": "Die LINKE."
        }

DIP_GREMIUM_TO_KEY = {
    u"Ausschuss für Bildung, Forschung und Technikfolgenabschätzung": "a18",
    u"Ausschuss für Ernährung, Landwirtschaft und Verbraucherschutz": "a10",
    u"Ausschuss für Tourismus": "a20",
    u"Ausschuss für Umwelt, Naturschutz und Reaktorsicherheit": "a16",
    u"Ausschuss für Verkehr, Bau und Stadtentwicklung": "a15",
    u"Ausschuss für Arbeit und Soziales": "a11",
    u"Ausschuss für Familie, Senioren, Frauen und Jugend": "a13",
    u"Ausschuss für Wirtschaft und Technologie": "a09",
    u"Finanzausschuss": "a07",
    u"Haushaltsausschuss": "a08",
    u"Ausschuss für die Angelegenheiten der Europäischen Union": "a21",
    u"Ausschuss für Agrarpolitik und Verbraucherschutz": "a10",
    u"Ausschuss für Innere Angelegenheiten": "a04",
    u"Wirtschaftsausschuss": "a09",
    u"Ausschuss für Gesundheit": "a14",
    u"Ausschuss für Wahlprüfung, Immunität und Geschäftsordnung": "a01",
    u"Rechtsausschuss": "a06",
    u"Ausschuss für Fragen der Europäischen Union": "a21",
    u"Ausschuss für Kulturfragen": "a22",
    u"Gesundheitsausschuss": "a14",
    u"Ausschuss für Menschenrechte und humanitäre Hilfe": "a17",
    u"Ausschuss für wirtschaftliche Zusammenarbeit und Entwicklung": "a19",
    u"Ausschuss für Auswärtige Angelegenheiten": "a03",
    u"Ausschuss für Kultur und Medien": "a22",
    u"Sportausschuss": "a05",
    u"Auswärtiger Ausschuss": "a03",
    u"Ausschuss für Arbeit und Sozialpolitik": "a11",
    u"Ausschuss für Frauen und Jugend": "a13",
    u"Ausschuss für Städtebau, Wohnungswesen und Raumordnung": "a15",
    u"Innenausschuss": "a04",
    u"Verkehrsausschuss": "a15",
    u"Verteidigungsausschuss": "a12",
    u"Ausschuss für Familie und Senioren": "a13",
    u"Petitionsausschuss": "a02",
    u"Ausschuss für Verteidigung": "a12",
    u"Ältestenrat": "002"
    }


DIP_ABLAUF_STATES_FINISHED = { 
    u'Beantwortet': True,
    u'Abgeschlossen': True,
    u'Abgelehnt': True,
    u'In der Beratung (Einzelheiten siehe Vorgangsablauf)': False,
    u'Verkündet': True,
    u'Angenommen': True,
    u'Keine parlamentarische Behandlung': False,
    u'Überwiesen': False,
    u'Beschlussempfehlung liegt vor': False,
    u'Noch nicht beraten': False,
    u'Für erledigt erklärt': True,
    u'Noch nicht beantwortet': False,
    u'Zurückgezogen': True,
    u'Dem Bundestag zugeleitet - Noch nicht beraten': False,
    u'Nicht beantwortet wegen Nichtanwesenheit des Fragestellers': True,
    u'Zustimmung erteilt': True,
    u'Keine parlamentarische Behandlung': True,
    u'Aufhebung nicht verlangt': False,
    u'Den Ausschüssen zugewiesen': False,
    u'Zusammengeführt mit... (siehe Vorgangsablauf)': True,
    u'Dem Bundesrat zugeleitet - Noch nicht beraten': False,
    u'Zustimmung (mit Änderungen) erteilt': True,
    u'Bundesrat hat Vermittlungsausschuss nicht angerufen': False,
    u'Bundesrat hat zugestimmt': False,
    u'1. Durchgang im Bundesrat abgeschlossen': False,
    u'Einbringung abgelehnt': True,
    u'Verabschiedet': True,
    u'Entlastung erteilt': True,
    u'Abschlussbericht liegt vor': True,
    u'Erledigt durch Ende der Wahlperiode (§ 125 GOBT)': True,
    u'Zuleitung beschlossen': False,
    u'Zuleitung in geänderter Fassung beschlossen': False,
    u'Für gegenstandslos erklärt': False,
    u'Nicht ausgefertigt wegen Zustimmungsverweigerung des Bundespräsidenten': False,
    u'Im Vermittlungsverfahren': False,
    u'Zustimmung versagt': True,
    u'Einbringung in geänderter Fassung beschlossen': False,
    u'Bundesrat hat keinen Einspruch eingelegt': False,
    u'Bundesrat hat Einspruch eingelegt': False,
    u'Zuleitung in Neufassung beschlossen': True,
    u'Untersuchungsausschuss eingesetzt': False
}

GREMIUM_RSS_FEEDS = {
        "a11": "http://www.bundestag.de/rss_feeds/arbeitsoziales.rss",
        "a03": "http://www.bundestag.de/rss_feeds/auswaertiges.rss",
        "a18": "http://www.bundestag.de/rss_feeds/bildung.rss",
        "a10": "http://www.bundestag.de/rss_feeds/landwirtschaftverbraucher.rss",
        "a21": "http://www.bundestag.de/rss_feeds/eu.rss",
        "a13": "http://www.bundestag.de/rss_feeds/familie.rss",
        "a07": "http://www.bundestag.de/rss_feeds/finanzen.rss",
        "a14": "http://www.bundestag.de/rss_feeds/gesundheit.rss",
        "a08": "http://www.bundestag.de/rss_feeds/haushalt.rss",
        "a04": "http://www.bundestag.de/rss_feeds/inneres.rss",
        "a22": "http://www.bundestag.de/rss_feeds/kultur.rss",
        "a17": "http://www.bundestag.de/rss_feeds/menschenrechte.rss",
        "a02": "http://www.bundestag.de/rss_feeds/petitionen.rss",
        "a06": "http://www.bundestag.de/rss_feeds/recht.rss",
        "a05": "http://www.bundestag.de/rss_feeds/sport.rss",
        "a20": "http://www.bundestag.de/rss_feeds/tourismus.rss",
        "a16": "http://www.bundestag.de/rss_feeds/umwelt.rss",
        "a15": "http://www.bundestag.de/rss_feeds/verkehr.rss",
        "a14": "http://www.bundestag.de/rss_feeds/verteidigung.rss",
        "a09": "http://www.bundestag.de/rss_feeds/wirtschaft.rss",
        "a19": "http://www.bundestag.de/rss_feeds/entwicklung.rss",
        "eig": "http://www.bundestag.de/rss_feeds/internetenquete.rss"
    }

GERMAN_MONTHS = {
    'Jan': 1,
    'Feb': 2,
    'Mrz': 3,
    'Apr': 4,
    'Mai': 5,
    'Jun': 6,
    'Jul': 7,
    'Aug': 8,
    'Sep': 9, 
    'Okt': 10,
    'Nov': 11,
    'Dez': 12
    }

