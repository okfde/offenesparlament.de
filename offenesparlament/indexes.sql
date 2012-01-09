
# ON ETL:

CREATE INDEX vote_psn ON abstimmung (person);
CREATE INDEX vote_subj ON abstimmung (subject);

CREATE INDEX abl_key ON ablauf (key, wahlperiode);
CREATE INDEX abl_typ ON ablauf (typ);
CREATE INDEX idx_sw ON schlagwort (key, wahlperiode);
CREATE INDEX idx_swid ON schlagwort (id);
CREATE INDEX ref_sw ON referenz (ablauf_key, wahlperiode);
CREATE INDEX bei_sw ON beitrag (fundstelle, urheber, ablauf_id);
CREATE INDEX zuw_sw ON zuweisung (fundstelle, urheber, ablauf_id);
CREATE INDEX pos_sw ON position (ablauf_id);

CREATE INDEX speech_url ON mediathek (speech_source_url);

CREATE INDEX speech_ssw ON speech (sequence, sitzung, wahlperiode);


# ON PROD:

CREATE INDEX load_person_fp ON person (fingerprint);
CREATE INDEX load_zitat ON zitat (sitzung_id, sequenz);
CREATE INDEX load_debatte_url ON debatte (source_url);
CREATE INDEX load_debatte_zit_zit ON debatte_zitat (debatte_id, zitat_id);
