"""Reviewed transcription of official cabinet dates and parliamentary elections.

Cabinet boundary dates are from the government archive, which takes precedence
over narrative biographies. End dates are exclusive (the next cabinet's start).
"""
import json
from pathlib import Path
SOURCE='https://gslegal.gov.gr/kyvernisi/istorika-stoixeia/'
ELECTION_SOURCE='https://www.hellenicparliament.gr/Vouli-ton-Ellinon/To-Politevma/Ekloges/Eklogika-apotelesmata-New/'
ROWS=[
 ('1974-07-24','1974-11-21','Konstantinos Karamanlis','Κωνσταντίνος Καραμανλής','UNITY','National unity government','Κυβέρνηση εθνικής ενότητας'),
 ('1974-11-21','1977-11-28','Konstantinos Karamanlis','Κωνσταντίνος Καραμανλής','ND','New Democracy','Νέα Δημοκρατία'),
 ('1977-11-28','1980-05-10','Konstantinos Karamanlis','Κωνσταντίνος Καραμανλής','ND','New Democracy','Νέα Δημοκρατία'),
 ('1980-05-10','1981-10-21','Georgios Rallis','Γεώργιος Ράλλης','ND','New Democracy','Νέα Δημοκρατία'),
 ('1981-10-21','1985-06-05','Andreas Papandreou','Ανδρέας Παπανδρέου','PASOK','PASOK','ΠΑΣΟΚ'),
 ('1985-06-05','1989-07-02','Andreas Papandreou','Ανδρέας Παπανδρέου','PASOK','PASOK','ΠΑΣΟΚ'),
 ('1989-07-02','1989-10-12','Tzannis Tzannetakis','Τζαννής Τζαννετάκης','COALITION','ND–Synaspismos coalition','Συνεργασία ΝΔ–Συνασπισμού'),
 ('1989-10-12','1989-11-23','Ioannis Grivas','Ιωάννης Γρίβας','CARETAKER','Caretaker government','Υπηρεσιακή κυβέρνηση'),
 ('1989-11-23','1990-04-11','Xenophon Zolotas','Ξενοφών Ζολώτας','COALITION','ND–PASOK–Synaspismos coalition','Οικουμενική ΝΔ–ΠΑΣΟΚ–Συνασπισμού'),
 ('1990-04-11','1993-10-13','Konstantinos Mitsotakis','Κωνσταντίνος Μητσοτάκης','ND','New Democracy','Νέα Δημοκρατία'),
 ('1993-10-13','1996-01-22','Andreas Papandreou','Ανδρέας Παπανδρέου','PASOK','PASOK','ΠΑΣΟΚ'),
 ('1996-01-22','1996-09-25','Costas Simitis','Κώστας Σημίτης','PASOK','PASOK','ΠΑΣΟΚ'),
 ('1996-09-25','2000-04-13','Costas Simitis','Κώστας Σημίτης','PASOK','PASOK','ΠΑΣΟΚ'),
 ('2000-04-13','2004-03-10','Costas Simitis','Κώστας Σημίτης','PASOK','PASOK','ΠΑΣΟΚ'),
 ('2004-03-10','2007-09-19','Kostas Karamanlis','Κώστας Καραμανλής','ND','New Democracy','Νέα Δημοκρατία'),
 ('2007-09-19','2009-10-06','Kostas Karamanlis','Κώστας Καραμανλής','ND','New Democracy','Νέα Δημοκρατία'),
 ('2009-10-06','2011-11-11','George Papandreou','Γιώργος Παπανδρέου','PASOK','PASOK','ΠΑΣΟΚ'),
 ('2011-11-11','2012-05-16','Lucas Papademos','Λουκάς Παπαδήμος','COALITION','PASOK–ND; LAOS until February 2012','ΠΑΣΟΚ–ΝΔ· ΛΑΟΣ έως Φεβρουάριο 2012'),
 ('2012-05-16','2012-06-20','Panagiotis Pikrammenos','Παναγιώτης Πικραμμένος','CARETAKER','Caretaker government','Υπηρεσιακή κυβέρνηση'),
 ('2012-06-20','2015-01-26','Antonis Samaras','Αντώνης Σαμαράς','COALITION','ND–PASOK; DIMAR until June 2013','ΝΔ–ΠΑΣΟΚ· ΔΗΜΑΡ έως Ιούνιο 2013'),
 ('2015-01-26','2015-08-27','Alexis Tsipras','Αλέξης Τσίπρας','SYRIZA','SYRIZA–ANEL coalition','Συνεργασία ΣΥΡΙΖΑ–ΑΝΕΛ'),
 ('2015-08-27','2015-09-21','Vassiliki Thanou','Βασιλική Θάνου','CARETAKER','Caretaker government','Υπηρεσιακή κυβέρνηση'),
 ('2015-09-21','2019-07-08','Alexis Tsipras','Αλέξης Τσίπρας','SYRIZA','SYRIZA–ANEL; SYRIZA minority from January 2019','ΣΥΡΙΖΑ–ΑΝΕΛ· μειοψηφία ΣΥΡΙΖΑ από Ιανουάριο 2019'),
 ('2019-07-08','2023-05-25','Kyriakos Mitsotakis','Κυριάκος Μητσοτάκης','ND','New Democracy','Νέα Δημοκρατία'),
 ('2023-05-25','2023-06-26','Ioannis Sarmas','Ιωάννης Σαρμάς','CARETAKER','Caretaker government','Υπηρεσιακή κυβέρνηση'),
 ('2023-06-26',None,'Kyriakos Mitsotakis','Κυριάκος Μητσοτάκης','ND','New Democracy','Νέα Δημοκρατία'),
]
ELECTIONS=[('1974-11-17','ND'),('1977-11-20','ND'),('1981-10-18','PASOK'),('1985-06-02','PASOK'),('1989-06-18','ND'),('1989-11-05','ND'),('1990-04-08','ND'),('1993-10-10','PASOK'),('1996-09-22','PASOK'),('2000-04-09','PASOK'),('2004-03-07','ND'),('2007-09-16','ND'),('2009-10-04','PASOK'),('2012-05-06','ND'),('2012-06-17','ND'),('2015-01-25','SYRIZA'),('2015-09-20','SYRIZA'),('2019-07-07','ND'),('2023-05-21','ND'),('2023-06-25','ND')]
def build():
    data={'verifiedAt':'2026-09-19','governmentSource':SOURCE,'electionSource':ELECTION_SOURCE,
    'parties':{'ND':{'en':'New Democracy','el':'Νέα Δημοκρατία','color':'#2479b7'},'PASOK':{'en':'PASOK','el':'ΠΑΣΟΚ','color':'#32805b'},'SYRIZA':{'en':'SYRIZA-led','el':'ΣΥΡΙΖΑ','color':'#b94d62'},'COALITION':{'en':'Coalition','el':'Συνεργασία','color':'#8460a0'},'CARETAKER':{'en':'Caretaker','el':'Υπηρεσιακή','color':'#7c858e'},'UNITY':{'en':'National unity','el':'Εθνική ενότητα','color':'#967744'}},
    'governments':[{'id':start,'start':start,'end':end,'name':{'en':en,'el':el},'party':party,'coalition':{'en':co,'el':coel},'sourceUrl':SOURCE} for start,end,en,el,party,co,coel in ROWS],
    'elections':[{'date':date,'largestParty':party,'sourceUrl':ELECTION_SOURCE} for date,party in ELECTIONS]}
    path=Path(__file__).resolve().parents[1]/'data'/'history.json'
    path.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
if __name__=='__main__':build()
