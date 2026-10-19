#!/usr/bin/env python3
"""Reproducible snapshot audit; makes no publication or causal-quality decisions."""
import argparse,collections,datetime,hashlib,itertools,json,math,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def full_years(term,asof):
    end=term['end'] or asof
    return [y for y in range(int(term['start'][:4]),int(end[:4])+1) if term['start']<=f'{y}-01-01' and end>=f'{y+1}-01-01']
def valid(m):
    return {y:v for y,v in m['series'].get('GRC',[]) if isinstance(v,(int,float)) and math.isfinite(v)}
def provider(m):
    for prefix,name in [('AMECO.','AMECO'),('ESTAT.','Eurostat'),('OECD.','OECD'),('ILO.','ILOSTAT'),('VDEM.','V-Dem'),('VDem.','V-Dem'),('UIS.','UIS'),('PWT.','PWT'),('UNDP.','UNDP')]:
        if m['code'].startswith(prefix):return name
    return 'V-Dem' if m.get('source')=='vdem' or 'v-dem' in m.get('sourceName','').lower() else 'World Bank'
def audit(data,history,asof):
    groups=collections.defaultdict(list);titles=collections.defaultdict(list);slices=collections.defaultdict(list)
    rows=[];terms=history['governments'];eligible={t['id']:full_years(t,asof) for t in terms}
    pair=['2015-09-21','2019-07-08'];current='2023-06-26'
    for m in data['metrics']:
        values=valid(m);years=sorted(values);observed=set(years)
        gaps=[y for y in range(years[0],years[-1]+1) if y not in observed] if years else []
        period={}
        for t in terms:
            e=eligible[t['id']];p=[y for y in e if y in values];coverage=len(p)/len(e) if e else 0
            period[t['id']]={'eligibleYears':e,'observedYears':p,'missingYears':[y for y in e if y not in values],'coverage':round(coverage,4),'hasData':bool(p),'atLeastTwo':len(p)>=2,'screenPass':len(p)>=2 and coverage>=.8}
        flags=[{'year':y,'flag':str(m.get('flags',{}).get('GRC',{}).get(str(y),''))} for y in years]
        flags=[f for f in flags if f['flag']]
        issues=[]
        for key in ['unit','definition','sourceUrl','retrievedAt','sha256']:
            if not m.get(key):issues.append('missing_'+key)
        if not m.get('title',{}).get('el'):issues.append('missing_greek_title')
        if years and years[-1]<int(asof[:4])-3:issues.append('latest_before_'+str(int(asof[:4])-3))
        if not years:issues.append('no_greek_observations')
        row={'code':m['code'],'title':m['title']['en'],'category':m.get('primaryCategory') or m['categories'][0],'provider':provider(m),'unit':m['unit'],'firstYear':years[0] if years else None,'latestYear':years[-1] if years else None,'greekObservations':len(years),'internalMissingYears':gaps,'spanCoverage':round(len(years)/(years[-1]-years[0]+1),4) if years else 0,'flags':flags,'hasResearchUncertainty':bool(m.get('uncertaintyLevel')),'issues':issues,'periods':period,'defaultPairHasBoth':all(period[t]['hasData'] for t in pair),'defaultPairTwoEach':all(period[t]['atLeastTwo'] for t in pair),'defaultPairScreenPass':all(period[t]['screenPass'] for t in pair),'currentTermScreenPass':period[current]['screenPass']}
        rows.append(row)
        if values:groups[(m['unit'],tuple(sorted(values.items())))].append(m['code'])
        titles[re.sub(r'\W+',' ',m['title']['en'].lower()).strip()].append(m['code'])
        if m.get('dimensions'):
            slices[(m.get('sourceName'),m.get('source'),m.get('indicator') or m.get('oecdSelectionId') or m.get('iloSelectionId') or m['code'],m['unit'],json.dumps(m['dimensions'],sort_keys=True))].append(m['code'])
    categories=[]
    for c in data['categories']:
        r=[x for x in rows if x['category']==c['id']]
        categories.append({'id':c['id'],'title':c['title']['en'],'count':len(r),'defaultPairHasBoth':sum(x['defaultPairHasBoth'] for x in r),'defaultPairTwoEach':sum(x['defaultPairTwoEach'] for x in r),'defaultPairScreenPass':sum(x['defaultPairScreenPass'] for x in r),'currentTermScreenPass':sum(x['currentTermScreenPass'] for x in r),'lagReview':sum(any(i.startswith('latest_before') for i in x['issues']) for x in r)})
    # Matching values are a review signal only; constants and subcomponents can be valid.
    duplicates={'duplicateCodes':[k for k,v in collections.Counter(x['code'] for x in rows).items() if v>1],'sameTitleGroups':[v for v in titles.values() if len(v)>1],'identicalGreekSeriesGroups':[v for v in groups.values() if len(v)>1],'sameDocumentedSliceGroups':[v for v in slices.values() if len(v)>1]}
    partial=[]
    for a,b in itertools.combinations(data['metrics'],2):
        if a['unit']!=b['unit']:continue
        av,bv=valid(a),valid(b);shared=sorted(av.keys()&bv.keys())
        if len(shared)<10 or len(set(av[y] for y in shared))<3:continue
        if all(math.isclose(av[y],bv[y],rel_tol=1e-9,abs_tol=1e-10) for y in shared):partial.append({'codes':[a['code'],b['code']],'matchingYears':shared,'sameFullSeries':av==bv})
    duplicates['matchingSharedYearsPairs']=partial
    counts={'metrics':len(rows),'greekObservations':sum(x['greekObservations'] for x in rows),'allCountryObservations':sum(sum(isinstance(v,(int,float)) and math.isfinite(v) for y,v in pairs) for m in data['metrics'] for pairs in m['series'].values()),'providers':dict(collections.Counter(x['provider'] for x in rows)),'defaultPairHasBoth':sum(x['defaultPairHasBoth'] for x in rows),'defaultPairTwoEach':sum(x['defaultPairTwoEach'] for x in rows),'defaultPairScreenPass':sum(x['defaultPairScreenPass'] for x in rows),'currentTermScreenPass':sum(x['currentTermScreenPass'] for x in rows),'withInternalGaps':sum(bool(x['internalMissingYears']) for x in rows),'lagReview':sum(any(i.startswith('latest_before') for i in x['issues']) for x in rows),'missingCoreMetadata':sum(any(i.startswith('missing_') for i in x['issues']) for x in rows)}
    return {'auditDate':asof,'snapshotRetrievedAt':data['retrievedAt'],'timelineVerifiedAt':history['verifiedAt'],'method':{'defaultPair':pair,'currentTerm':current,'screen':'At least two observations and at least 80% of eligible full years in each period. Editorial screening threshold, not a statistical validity guarantee.','limits':'Snapshot audit only; source endpoints and licences are not freshly revalidated. No causal inference, significance test, inflation adjustment, duplicate removal or automatic publication. Latest-year review is a publication-lag screen, not a source failure.'},'summary':counts,'categories':categories,'duplicateReview':duplicates,'metrics':rows}
def markdown(r):
    s=r['summary'];lines=['# DATACRITUS catalogue audit — '+r['auditDate'],'',f"Snapshot retrieved: {r['snapshotRetrievedAt']}. Timeline verified: {r['timelineVerifiedAt']}.",'',f"**{s['metrics']} published series; {s['greekObservations']:,} Greek observations; {s['allCountryObservations']:,} observations across all countries.**",'', 'These are published indicator definitions, not a verified count of independent concepts. Composite indices, components, spending subdivisions and demographic breakdowns overlap.','', '## Comparison coverage','', 'Default pair: Tsipras 2015–2019 versus Mitsotakis 2019–2023, using full calendar years 2016–2018 and 2020–2022 only. Current term uses eligible years 2024–2025 at this audit date.','',f"- Both default periods have at least one observation: **{s['defaultPairHasBoth']}**.",f"- At least two observations in each: **{s['defaultPairTwoEach']}**.",f"- At least two and 80% coverage in each: **{s['defaultPairScreenPass']}**.",f"- Current term meets the same coverage screen: **{s['currentTermScreenPass']}**.",f"- Series with internal missing years: **{s['withInternalGaps']}**.",f"- Latest Greek observation before 2023, requiring publication-lag review: **{s['lagReview']}**.",'', 'Coverage does not establish comparability. Definitions, survey breaks, source flags, research uncertainty, denominators, nominal/real money and external shocks still require interpretation. The 80% threshold is an editorial screening choice, not a proof of statistical reliability.','', '## Category depth','', '| Category | Series | Both periods | ≥2 each | ≥80% + ≥2 each | Current term | Lag review |','|---|---:|---:|---:|---:|---:|---:|']
    for c in r['categories']:lines.append('| '+c['title']+' | '+' | '.join(str(c[k]) for k in ['count','defaultPairHasBoth','defaultPairTwoEach','defaultPairScreenPass','currentTermScreenPass','lagReview'])+' |')
    lines+=['','## Duplicate review','',f"Duplicate codes: {len(r['duplicateReview']['duplicateCodes'])}. Same-title groups: {len(r['duplicateReview']['sameTitleGroups'])}. Identical Greek-series groups: {len(r['duplicateReview']['identicalGreekSeriesGroups'])}. Same documented slice groups: {len(r['duplicateReview']['sameDocumentedSliceGroups'])}.",'','Matching values do not prove duplication. Constant research indices, totals and subsets can coincide. No series is removed automatically.']
    for key in ['sameTitleGroups','identicalGreekSeriesGroups','sameDocumentedSliceGroups']:
        lines+=['','### '+key,'']
        lines+=['- '+', '.join(g) for g in r['duplicateReview'][key]] or ['None found.']
    lines+=['','### Matching on at least ten shared years','']
    lines+=['- '+', '.join(p['codes'])+' ('+str(len(p['matchingYears']))+' shared years)' for p in r['duplicateReview']['matchingSharedYearsPairs']] or ['None found.']
    lines+=['','## Metadata','',f"Missing core metadata fields: {s['missingCoreMetadata']} series. This checks presence, not legal or semantic adequacy.",'','## Next actions','', '1. Keep headline concepts separate from research components and detailed breakdowns; avoid treating 207 V-Dem series as 207 independent outcomes.', '2. Review identical-series groups manually against definitions and source slices before merging anything.', '3. Prioritise interpretable additions in categories with weak comparison coverage, then re-fetch candidate data and validate Greek history, dimensions, flags and reuse terms.', '4. Treat 600 as a target requiring 140 net new approved definitions from the current 460. A candidate pool is not a publication count.', '5. Do not silently drop older series: publication lag and historical-only measures need explicit labels.', '', 'This audit reads the published catalogue. It does not claim a fresh item-by-item reread of the original thesis or a new live-provider audit.','']
    return '\n'.join(lines)+'\nCandidate screen: [review](candidates.md), [API results](candidate-screen.json).\n'
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--as-of',default=datetime.date.today().isoformat());args=parser.parse_args()
    raw=(ROOT/'data/indicators.json').read_bytes();data=json.loads(raw);history=json.loads((ROOT/'data/history.json').read_text());r=audit(data,history,args.as_of);r['snapshotSha256']=hashlib.sha256(raw).hexdigest()
    r['allTermCoverageColumns']=['term_id','observations','eligible_years']
    for row in r['metrics']:
        row['allTermCoverage']=[[key,len(p['observedYears']),len(p['eligibleYears'])] for key,p in row['periods'].items()]
        row['periods']={key:p for key,p in row['periods'].items() if key in [*r['method']['defaultPair'],r['method']['currentTerm']]}
    target=ROOT/'data/audits'/('catalogue-'+args.as_of);target.mkdir(parents=True,exist_ok=True)
    (target/'review.json').write_text(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n');(target/'README.md').write_text(markdown(r));print(json.dumps(r['summary'],indent=2));print(json.dumps(r['categories'],indent=2));print('Duplicate groups:',{k:len(v) for k,v in r['duplicateReview'].items()})
if __name__=='__main__':main()
