"""One editorial home per metric; bilingual secondary tags support discovery."""
CATEGORIES = [
 ('economy','Economy & productivity','Οικονομία & παραγωγικότητα'),
 ('jobs','Jobs & earnings','Εργασία & αποδοχές'),
 ('finance','Public finances','Δημόσια οικονομικά'),
 ('wellbeing','Living standards & housing','Επίπεδο διαβίωσης & στέγαση'),
 ('health','Health & care','Υγεία & φροντίδα'),
 ('education','Education & research','Εκπαίδευση & έρευνα'),
 ('governance','Democracy, justice & rights','Δημοκρατία, δικαιοσύνη & δικαιώματα'),
 ('demographics','Population & migration','Πληθυσμός & μετανάστευση'),
 ('environment','Environment & energy','Περιβάλλον & ενέργεια'),
 ('transport','Transport & infrastructure','Μεταφορές & υποδομές'),
 ('business','Business & digital economy','Επιχειρήσεις & ψηφιακή οικονομία'),
 ('culture','Culture & tourism','Πολιτισμός & τουρισμός'),
]
GROUPS = {
 'economy': 'NY.GDP.MKTP.KD.ZG NY.GDP.PCAP.KD BX.KLT.DINV.WD.GD.ZS BM.KLT.DINV.WD.GD.ZS SL.GDP.PCAP.EM.KD NY.GDP.MKTP.CD NY.GDP.MKTP.PP.CD FI.RES.TOTL.MO',
 'jobs': 'SL.UEM.TOTL.ZS SL.UEM.1524.ZS SL.TLF.CACT.FE.ZS',
 'finance': 'GC.TAX.TOTL.GD.ZS GC.REV.XGRT.GD.ZS DC.ODA.TLDC.CD DC.ODA.TOTL.CD ESTAT.GOV.EXPENDITURE ESTAT.GOV.DEBT ESTAT.GOV.BALANCE',
 'wellbeing': 'FP.CPI.TOTL.ZG FP.CPI.TOTL SI.POV.GINI SH.H2O.SMDW.ZS SH.STA.SMSS.ZS SH.H2O.BASW.ZS SH.STA.ODFC.ZS SH.STA.BASS.UR.ZS SH.H2O.BASW.RU.ZS ESTAT.HOUSING.OVERBURDEN ESTAT.LIFE.SATISFACTION ESTAT.HOUSEHOLDS.SINGLE',
 'health': 'SP.DYN.LE00.IN SP.DYN.IMRT.IN SH.STA.MMRT SH.MED.BEDS.ZS SH.XPD.CHEX.GD.ZS SH.XPD.CHEX.PC.CD SH.IMM.MEAS SH.ALC.PCAP.LI',
 'education': 'SE.XPD.TOTL.GD.ZS SE.TER.ENRR SE.SEC.ENRR SE.PRM.ENRL.TC.ZS SE.PRM.ENRR SE.PRM.CMPT.ZS SE.SEC.CMPT.LO.ZS SE.PRM.TCHR.FE.ZS GB.XPD.RSDV.GD.ZS IP.JRN.ARTC.SC SP.POP.SCIE.RD.P6',
 'governance': 'VC.IHR.PSRC.P5 SG.GEN.PARL.ZS GOV_WGI_GE.EST GOV_WGI_CC.EST GOV_WGI_RL.EST GOV_WGI_VA.EST GOV_WGI_PV.EST GOV_WGI_RQ.EST ESTAT.POLICE.DENSITY',
 'demographics': 'SP.POP.TOTL SP.DYN.TFRT.IN SP.POP.65UP.TO.ZS SP.POP.GROW EN.POP.DNST SP.DYN.CBRT.IN SP.DYN.CDRT.IN SP.POP.DPND.OL SP.POP.DPND.YG SP.POP.TOTL.FE.ZS SP.URB.TOTL.IN.ZS SM.POP.RHCR.EA SM.POP.TOTL ESTAT.MOTHERS.AGE',
 'environment': 'AG.LND.FRST.ZS EN.ATM.PM25.MC.M3 EN.GHG.CO2.PC.CE.AR5 ER.LND.PTLD.ZS EG.ELC.ACCS.ZS EG.FEC.RNEW.ZS EG.ELC.RNEW.ZS EG.IMP.CONS.ZS AG.LND.FRST.K2 AG.LND.AGRI.ZS ER.H2O.FWTL.K3 EG.EGY.PRIM.PP.KD ESTAT.WASTE.RECYCLING ESTAT.CO2.TRANSPORT ESTAT.CO2.DOMESTIC.AVIATION',
 'transport': 'IS.RRS.TOTL.KM SH.STA.TRAF.P5 IS.AIR.PSGR IS.RRS.PASG.KM IS.AIR.GOOD.MT.K1 IT.MLT.MAIN.P2',
 'business': 'NE.TRD.GNFS.ZS NE.EXP.GNFS.ZS NE.EXP.GNFS.CD IT.NET.BBND.P2 IT.NET.USER.ZS IT.CEL.SETS.P2 IP.PAT.RESD TX.VAL.TECH.MF.ZS FB.ATM.TOTL.P5',
 'culture': 'ST.INT.ARVL ST.INT.RCPT.CD ESTAT.CULTURE.EMPLOYMENT ESTAT.HOTELS.NONRESIDENT ESTAT.HOTELS.RESIDENT ESTAT.TOUR.TRIPS',
}
# Deliberate cross-topic views, not duplicate entries in the main navigation.
TAG_GROUPS = {
 ('gender','Gender equality','Ισότητα φύλων'): 'SL.TLF.CACT.FE.ZS SG.GEN.PARL.ZS SE.PRM.TCHR.FE.ZS',
 ('migration','Migration & asylum','Μετανάστευση & άσυλο'): 'SM.POP.RHCR.EA SM.POP.TOTL',
 ('resilience','Resilience','Ανθεκτικότητα'): 'SH.IMM.MEAS ER.LND.PTLD.ZS EG.FEC.RNEW.ZS EG.IMP.CONS.ZS ER.H2O.FWTL.K3 EG.EGY.PRIM.PP.KD FI.RES.TOTL.MO ESTAT.WASTE.RECYCLING',
 ('banking','Banking access','Πρόσβαση σε τραπεζικές υπηρεσίες'): 'FB.ATM.TOTL.P5',
 ('safety','Public safety','Δημόσια ασφάλεια'): 'VC.IHR.PSRC.P5 SH.STA.TRAF.P5 ESTAT.POLICE.DENSITY',
 ('trade','International trade','Διεθνές εμπόριο'): 'NE.TRD.GNFS.ZS NE.EXP.GNFS.ZS NE.EXP.GNFS.CD TX.VAL.TECH.MF.ZS',
 ('innovation','Innovation','Καινοτομία'): 'GB.XPD.RSDV.GD.ZS IP.JRN.ARTC.SC SP.POP.SCIE.RD.P6 IP.PAT.RESD TX.VAL.TECH.MF.ZS',
 ('water','Water & sanitation','Νερό & αποχέτευση'): 'SH.H2O.SMDW.ZS SH.STA.SMSS.ZS SH.H2O.BASW.ZS SH.STA.ODFC.ZS SH.STA.BASS.UR.ZS SH.H2O.BASW.RU.ZS ER.H2O.FWTL.K3',
 ('energy','Energy','Ενέργεια'): 'EG.ELC.ACCS.ZS EG.FEC.RNEW.ZS EG.ELC.RNEW.ZS EG.IMP.CONS.ZS EG.EGY.PRIM.PP.KD',
 ('tourism','Tourism','Τουρισμός'): 'ST.INT.ARVL ST.INT.RCPT.CD ESTAT.HOTELS.NONRESIDENT ESTAT.HOTELS.RESIDENT ESTAT.TOUR.TRIPS IS.AIR.PSGR',
}
CATEGORY_NOTES = {
 'jobs': {'en':'Employment, unemployment, labour participation and nominal gross salary describe different aspects of work. Salary is not take-home pay or purchasing power.','el':'Απασχόληση, ανεργία, συμμετοχή στην εργασία και ονομαστικός μικτός μισθός καλύπτουν διαφορετικές πτυχές. Ο μισθός δεν είναι καθαρό εισόδημα ή αγοραστική δύναμη.'},
 'governance': {'en':'Institutional estimates, representation and public safety describe different aspects; they are not a single government score.','el':'Θεσμικές εκτιμήσεις, εκπροσώπηση και δημόσια ασφάλεια καλύπτουν διαφορετικές πτυχές· δεν αποτελούν ενιαία βαθμολογία κυβέρνησης.'},
 'culture': {'en':'Cultural employment, tourism and recreation/culture/religion spending are separate aspects, not measures of cultural quality.','el':'Πολιτιστική απασχόληση, τουρισμός και δαπάνες αναψυχής/πολιτισμού/θρησκείας είναι διαφορετικές πτυχές, όχι μέτρα πολιτιστικής ποιότητας.'},
}
from expansion import WORLD_BANK, EUROSTAT
for metric in WORLD_BANK + EUROSTAT:
    GROUPS[metric['categories'][0]] += ' ' + metric['code']

import json
from pathlib import Path
MANIFEST = json.loads(Path(__file__).with_name("vetted_manifest.json").read_text())
for metric in MANIFEST:
    GROUPS[metric['category']] += ' ' + metric['code']

ILO_MANIFEST = json.loads(Path(__file__).with_name('ilo_selection.json').read_text())
for metric in ILO_MANIFEST:
    GROUPS[metric['category']] += ' ' + metric['code']

OECD_MANIFEST = json.loads(Path(__file__).with_name('oecd_selection.json').read_text())
for metric in OECD_MANIFEST:
    GROUPS[metric['category']] += ' ' + metric['code']

PRIMARY = {code:cat for cat,codes in GROUPS.items() for code in codes.split()}
assert len(PRIMARY) == sum(len(codes.split()) for codes in GROUPS.values())
LEGACY = {'housing':'wellbeing','security':'governance','digital':'business','technology':'education','justice':'governance','energy':'environment','infrastructure':'transport','resilience':'environment','international':'business','freedom':'governance'}

def classify(metric):
    code=metric['code']
    if code not in PRIMARY: raise ValueError(f'No reviewed category for {code}')
    # Retain the old editorial topics for discoverability, with misleading placements removed.
    legacy=metric.get('legacyCategories',metric['categories'])
    legacy=[x for x in legacy if not (code=='SM.POP.RHCR.EA' and x=='security') and not (code=='FB.ATM.TOTL.P5' and x=='digital')]
    old_labels={'international':('International context','Διεθνές πλαίσιο'),'freedom':('Participation','Συμμετοχή'),'technology':('Technology','Τεχνολογία'),'housing':('Housing','Στέγαση'),'infrastructure':('Infrastructure','Υποδομές'),'justice':('Justice','Δικαιοσύνη'),'digital':('Digital access','Ψηφιακή πρόσβαση')}
    titles={i:(en,el) for i,en,el in CATEGORIES}
    tags={}
    for topic in legacy:
        if topic in ('security','resilience'): continue
        title=old_labels.get(topic,titles.get(topic))
        if title and topic!=PRIMARY[code]: tags[topic]={'id':topic,'title':dict(zip(('en','el'),title))}
    for (tag,en,el),codes in TAG_GROUPS.items():
        if code in codes.split():tags[tag]={'id':tag,'title':{'en':en,'el':el}}
    return {**metric,'legacyCategories':legacy,'primaryCategory':PRIMARY[code],'categories':[PRIMARY[code]],'tags':list(tags.values())}

def categories():
    return [{'id':i,'title':{'en':en,'el':el},'note':CATEGORY_NOTES.get(i)} for i,en,el in CATEGORIES]
