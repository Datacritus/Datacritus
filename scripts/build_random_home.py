"""Homepage comparison catalogue generated from the verified snapshot."""
from datetime import date
import math
import json

def render(snapshot, history):
    # Public-facing measures selected for relevance and understandable units.
    codes = set('''
NY.GDP.MKTP.KD.ZG NY.GDP.PCAP.KD FP.CPI.TOTL.ZG SL.UEM.TOTL.ZS
SL.UEM.1524.ZS SL.TLF.CACT.FE.ZS SL.UEM.NEET.ZS SP.DYN.LE00.IN
SP.DYN.IMRT.IN SH.MED.BEDS.ZS SH.XPD.CHEX.GD.ZS SH.XPD.OOPC.CH.ZS
SE.XPD.TOTL.GD.ZS SE.PRM.ENRL.TC.ZS EN.ATM.PM25.MC.M3
EN.GHG.CO2.PC.CE.AR5 SI.POV.GINI ST.INT.ARVL ST.INT.RCPT.CD
VC.IHR.PSRC.P5 SH.STA.TRAF.P5 SP.DYN.TFRT.IN EG.FEC.RNEW.ZS
EG.ELC.RNEW.ZS EG.IMP.CONS.ZS GOV_WGI_CC.EST GOV_WGI_RL.EST
ESTAT.GOV.DEBT ESTAT.GOV.BALANCE ESTAT.HOUSING.OVERBURDEN
ESTAT.WASTE.RECYCLING ESTAT.LIFE.SATISFACTION ESTAT.POVERTY.AROPE
ESTAT.DEPRIVATION.SEVERE ESTAT.HOUSING.OVERCROWDING ESTAT.HOUSING.WARMTH
ESTAT.INCOME.MEDIAN ESTAT.EDUCATION.EARLY.LEAVERS
ESTAT.EDUCATION.TERTIARY.ATTAINMENT ESTAT.UNEMPLOYMENT.LONGTERM
ESTAT.SALARY.FTE ESTAT.HEALTH.UNMET.ACCESS ESTAT.ARREARS.PAYMENTS
ESTAT.POVERTY.INWORK ESTAT.INTERNET.HOUSEHOLDS ESTAT.EXPENSES.UNEXPECTED
ESTAT.FOOD.AFFORDABILITY ESTAT.ENDS.MEET.GREATDIFFICULTY ESTAT.POVERTY.CHILD
ESTAT.WORK.PARTTIME.INVOLUNTARY ESTAT.EDUCATION.GRADUATE.EMPLOYMENT
ESTAT.HOUSING.COST.MEDIAN ESTAT.INFLATION.FOOD
UNDP.hdi VDEM.v2x_freexp VDEM.v2x_libdem ILO.HOW_TEMP_SEX_NB
AMECO.RWCDC
'''.split())
    groups = {}
    for metric in snapshot['metrics']:
        if metric['code'] not in codes:
            continue
        rows = dict(metric['series']['GRC'])
        periods = []
        for term in history['governments']:
            start = date.fromisoformat(term['start'])
            end = date.fromisoformat(term['end'] or history['verifiedAt'])
            years = [y for y in range(start.year, end.year) if start <= date(y,1,1) and end >= date(y+1,1,1)]
            if len(years) < 3 or any(not isinstance(rows.get(y),(int,float)) or not math.isfinite(rows[y]) for y in years):
                continue
            points = [rows[y] for y in years]
            periods.append(dict(id=term['id'],name=term['name'],years=years,mean=sum(points)/len(points),first=points[0],last=points[-1]))
        pairs = [[i,j] for i,a in enumerate(periods) for j,b in enumerate(periods) if i < j and len(a['years'])==len(b['years'])]
        if pairs:
            groups.setdefault(metric['categories'][0],[]).append(dict(code=metric['code'],title=metric['title'],unit=metric['unit'],source=metric['sourceName'],periods=periods,pairs=pairs))
    return json.dumps(list(groups.values()),ensure_ascii=False).replace('<','\\u003c')
