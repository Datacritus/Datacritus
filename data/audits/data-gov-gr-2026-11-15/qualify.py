import json,pathlib,io,openpyxl,xlrd,math,collections,datetime,hashlib,urllib.request,urllib.parse,concurrent.futures
P=pathlib.Path('/mnt/data/datagov-audit');R=P/'resources';bog=json.loads((P/'bog.json').read_text());by={x['name']:x for x in bog}
S=[]
def add(slug,col,title,group,freq,agg,start=2000,unit='EUR million'):
 S.append(dict(dataset='bank-of-greece-'+slug,column=col,title=title,group=group,frequency=freq,annual_rule=agg,start_year=start,unit=unit))
add('index-of-apartment-prices',2,'Apartment prices — national index','Housing','quarterly','mean',2006,'source index; base must be documented on import')
rates='bank-interest-rates-on-new-euro-denominated-deposits-and-loans-vis-a-vis-euro-ar'
for c,t in [(3,'Household deposit interest rate'),(5,'Household term deposits up to one year — interest rate'),(12,'Consumer loan interest rate'),(13,'Housing loan interest rate'),(14,'Non-financial business loan interest rate'),(17,'Sole-proprietor loan interest rate')]:add(rates,c,t,'Interest rates','monthly','mean',2015,'% per annum; annual display is time average of monthly published rates')
credit='credit-to-domestic-public-and-private-sectors-by-domestic-monetary-financial-ins'
for c,t in [(10,'Loans to non-financial corporations — outstanding'),(17,'Housing loans to individuals and NPISH — outstanding'),(18,'Consumer loans to individuals and NPISH — outstanding')]:add(credit,c,t,'Lending','monthly','year_end',2019)
dep='deposits-and-repos-of-non-mfis-in-mfis-in-greece-excluding-the-bank-of-greece-ou'
for c,t in [(31,'Non-financial corporation deposits and repos — outstanding'),(34,'Household and NPISH deposits and repos — outstanding')]:add(dep,c,t,'Deposits','monthly','year_end',2019)
add('gross-external-debt',61,'Gross external debt — all sectors','External position','quarterly','year_end',2004)
add('international-investment-position-quarterly-data',193,'Net international investment position','External position','quarterly','year_end',2004)
for c,t in [(5,'Balance of trade in goods — balance-of-payments basis'),(19,'Balance of services — balance-of-payments basis')]:add('balance-of-payments-monthly-data',c,t,'External trade','monthly','sum',2002)
for slug,t,unit in [('non-residents-average-duration-of-stay-in-greece-by-country-of-origin-annually','Inbound visitor average stay','nights'),('non-residents-expenditure-per-journey-in-greece-by-country-of-origin-annually','Inbound visitor expenditure per trip','EUR per trip'),('non-residents-expenditure-per-overnight-stay-in-greece-by-country-of-origin-annu','Inbound visitor expenditure per overnight stay','EUR per night')]:add(slug,25,t,'Tourism','annual','published',2013,unit)
add('greece-nominal-effective-exchange-rate-index',2,'Nominal effective exchange rate — broad index','Competitiveness','monthly','mean',2000,'index 2000=100')
add('greece-real-effective-exchange-rate-index',2,'Real effective exchange rate — broad CPI-based index','Competitiveness','quarterly','mean',2000,'index 2000=100')
def rows_for(item):
 p=next(f for f in R.glob(item['dataset']+'.*') if f.suffix in ['.xls','.xlsx']);raw=p.read_bytes()
 if raw[:2]==b'PK':return list(openpyxl.load_workbook(io.BytesIO(raw),read_only=True,data_only=True).worksheets[0].values)
 sh=xlrd.open_workbook(file_contents=raw).sheet_by_index(0);return [sh.row_values(i) for i in range(sh.nrows)]
allout=[]
for item in S:
 rs=[r for r in rows_for(item) if any(v not in (None,'') for v in r)];head=rs[0];points=[];invalid=[]
 for row in rs[1:]:
  try:
   rawy=row[0];year=int(rawy.year if hasattr(rawy,'year') else str(rawy)[:4] if isinstance(rawy,str) else rawy)
   if not 1900<=year<=2026 or year<item['start_year']:continue
   freq=item['frequency']
   if freq=='annual':period=1
   elif isinstance(rawy,str) and '-' in rawy:period=(int(rawy[5:7])-1)//3+1 if freq=='quarterly' else int(rawy[5:7])
   elif hasattr(rawy,'month'):period=(rawy.month-1)//3+1 if freq=='quarterly' else rawy.month
   else:period=int(row[1])
   v=row[item['column']]
   if not isinstance(v,(float,int)) or not math.isfinite(v):invalid.append([year,period,str(v)]);continue
   points.append([year,period,v])
  except (ValueError,TypeError,IndexError):continue
 keys=[tuple(p[:2]) for p in points];assert len(keys)==len(set(keys)),item['title']
 groups=collections.defaultdict(list)
 for y,p,v in points:groups[y].append((p,v))
 annual=[];expected={'annual':1,'quarterly':4,'monthly':12}[item['frequency']]
 for y,ps in sorted(groups.items()):
  if len(ps)!=expected or {p for p,v in ps}!=set(range(1,expected+1)):continue
  if item['annual_rule']=='year_end':v=dict(ps)[expected]
  elif item['annual_rule']=='sum':v=sum(v for p,v in ps)
  else:v=sum(v for p,v in ps)/len(ps)
  annual.append([y,v])
 meta=json.loads((R/(item['dataset']+'.json')).read_text());assert len(annual)>=5,(item['title'],len(annual));assert annual[-1][0]>=2024,(item['title'],annual[-1])
 item.update(source_field=head[item['column']],native_points=len(points),first_native=points[0][:2],last_native=points[-1][:2],complete_annual_years=[p[0] for p in annual],annual_series=annual,missing_points=invalid,license=by[item['dataset']]['license_id'],source_url=meta['url'],resource_id=meta['resource'],sha256=meta['sha256'],status='qualified_with_documented_import_conditions')
 allout.append(item)
(P/'qualified-series.json').write_text(json.dumps(allout,ensure_ascii=False,indent=2))
print('QUALIFIED',len(allout));print('GROUPS',dict(collections.Counter(x['group'] for x in allout)))
for i,x in enumerate(allout,1):print(i,x['title'],x['first_native'],x['last_native'],'complete years',len(x['annual_series']),'missing',len(x['missing_points']))
