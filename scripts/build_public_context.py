"""Public, build-time comparison context and deterministic social chart images."""
import json
import math
from datetime import date
from html import escape
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
UNEMPLOYMENT = {'SL.UEM.TOTL.ZS', 'SL.UEM.1524.ZS'}


def source_label(metric, lang):
    if metric['code'] in UNEMPLOYMENT:
        return 'Μοντελοποιημένη εκτίμηση ILO, μέσω World Bank WDI' if lang == 'el' else 'ILO modelled estimate, via World Bank WDI'
    return metric['sourceName']


def source_note(metric, lang):
    if metric['code'] not in UNEMPLOYMENT:
        return ''
    return ('Μοντελοποιημένη ετήσια εκτίμηση της ILO. Μπορεί να διαφέρει από τις εθνικές δημοσιεύσεις της ΕΛΣΤΑΤ λόγω μεθοδολογίας, περιόδου αναφοράς και αναθεωρήσεων. Μην συγκρίνετε απευθείας έναν ετήσιο μέσο όρο με ένα μηνιαίο ή τριμηνιαίο ποσοστό.' if lang == 'el' else
            'An annual ILO modelled estimate. It may differ from ELSTAT national releases because of methodology, reference periods and revisions. Do not compare an annual average directly with a monthly or quarterly rate.')


def government_table(metric, history, lang, number):
    el = lang == 'el'
    values = {y:v for y,v in metric['series']['GRC'] if isinstance(v,(int,float)) and math.isfinite(v)}
    rows = []
    for term in history['governments']:
        end = term['end'] or history['verifiedAt']
        years = [y for y in sorted(values) if term['start'] <= f'{y}-01-01' and f'{y+1}-01-01' <= end]
        if not years:
            continue
        first,last = years[0],years[-1]
        delta = values[last]-values[first] if len(years)>1 else None
        change = '—' if delta is None else ('+' if delta>0 else '')+number(delta,lang)
        unit = ('π.μ.' if el else 'pp') if metric.get('change')=='pp' else metric['unit']
        name = escape(term['coalition'][lang]+' · '+term['name'][lang])
        dates = term['start']+' → '+(term['end'] or ('σε εξέλιξη' if el else 'ongoing'))
        expected = sum(term['start'] <= f'{y}-01-01' and f'{y+1}-01-01' <= end for y in range(int(term['start'][:4]),int(end[:4])+1))
        rows.append(f'<tr><th scope="row">{name}<br><small>{dates}</small></th><td>{first}: {number(values[first],lang)}</td><td>{last}: {number(values[last],lang)}</td><td>{change} {escape(unit) if delta is not None else ""}</td><td>{number(sum(values[y] for y in years)/len(years),lang)}</td><td>{len(years)}/{expected}<br>{", ".join(map(str,years))}</td></tr>')
    title = 'Παρατηρήσεις ανά κυβερνητική περίοδο' if el else 'Observations by government period'
    headings = ['Κυβέρνηση','Πρώτη παρατήρηση','Τελευταία παρατήρηση','Μεταβολή','Μέσος όρος','Κάλυψη / έτη'] if el else ['Government','First observation','Last observation','Change','Average','Coverage / years']
    note = ('Μόνο πλήρη ημερολογιακά έτη μέσα σε κάθε κυβερνητική περίοδο· εξαιρούνται τα έτη αλλαγής κυβέρνησης. Οι τιμές δεν είναι τιμές ημέρας ανάληψης ή λήξης. Τα κενά δεν συμπληρώνονται. Οι περίοδοι διαφέρουν σε διάρκεια· απαιτούνται δύο παρατηρήσεις για μεταβολή. Περίοδοι χωρίς παρατήρηση πλήρους έτους παραλείπονται. Διαβάστε τον πίνακα μαζί με ολόκληρη την ιστορική εξέλιξη. Η χρονική σύμπτωση δεν αποδεικνύει αιτιότητα.' if el else
            'Only complete calendar years within each cabinet period; transition years are excluded. Values are not inauguration-day or end-of-office readings. Missing years remain missing. Periods differ in length; a change requires two observations. Periods without a full-year observation are omitted. Read this table alongside the full historical trend. Timing does not establish causation.')
    return f'<section class="panel"><h2>{title}</h2><p class="note">{note}</p><div class="table-wrap"><table class="government-table"><caption>{escape(metric["title"][lang])} · {escape(metric["unit"])}</caption><thead><tr>'+''.join('<th scope="col">'+h+'</th>' for h in headings)+'</tr></thead><tbody>'+''.join(rows)+'</tbody></table></div></section>'


def social_image(metric, lang, slug):
    folder = ROOT/'assets/social'; folder.mkdir(parents=True,exist_ok=True)
    image = Image.new('RGB',(1200,630),'#073b4c'); d=ImageDraw.Draw(image)
    font = lambda size: ImageFont.truetype(str(ROOT/'scripts/fonts/DejaVuSans.ttf'),size)
    d.text((54,30),'DATACRITUS',font=font(30),fill='#ffd166')
    title=metric['title'][lang];size=43
    while d.textbbox((0,0),title,font=font(size))[2]>1090:size-=1
    d.text((54,86),title,font=font(size),fill='white')
    rows=[(y,v) for y,v in metric['series']['GRC'] if isinstance(v,(int,float)) and math.isfinite(v)]
    first,last=rows[0][0],rows[-1][0];lo=min(v for _,v in rows);hi=max(v for _,v in rows);pad=(hi-lo)*.12 or 1;lo-=pad;hi+=pad
    x=lambda year:110+(year-first)/(last-first or 1)*1010
    y=lambda value:475-(value-lo)/(hi-lo)*260
    for i in range(4):
        v=lo+(hi-lo)*i/3; yy=y(v);d.line((110,yy,1120,yy),fill='#315867',width=1);d.text((18,yy-10),f'{v:.1f}',font=font(17),fill='#c9dfe6')
    for i,(year,value) in enumerate(rows):
        if i and year==rows[i-1][0]+1:d.line((x(rows[i-1][0]),y(rows[i-1][1]),x(year),y(value)),fill='#ffd166',width=5)
    d.ellipse((x(last)-6,y(rows[-1][1])-6,x(last)+6,y(rows[-1][1])+6),fill='#ffd166')
    d.text((110,492),str(first),font=font(21),fill='white');d.text((1050,492),str(last),font=font(21),fill='white')
    label=('Ελλάδα' if lang=='el' else 'Greece')+' · '+metric['unit']
    d.text((54,151),label,font=font(23),fill='#c9dfe6')
    credit=source_label(metric,lang);d.text((54,545),credit,font=font(20),fill='#c9dfe6')
    d.text((54,580),metric['code']+' · '+metric['retrievedAt'][:10],font=font(17),fill='#c9dfe6')
    image.save(folder/f'{slug}-{lang}.png',optimize=True)


def public_pages(document):
    paths=[]
    for lang in ['el','en']:
        el=lang=='el'
        content={
            'about': ('Σχετικά με το Datacritus' if el else 'About Datacritus',
                '<h2>Σκοπός και υπεύθυνος έργου</h2><p>Το Datacritus είναι πρωτοβουλία του Ioannis Beris. Σκοπός του είναι η προσβάσιμη εξερεύνηση δημόσιων δεδομένων για την Ελλάδα και η περιγραφική σύγκριση κυβερνητικών περιόδων.</p><h2>Ανεξαρτησία</h2><p>Πρόκειται για ανεξάρτητο έργο, χωρίς σύνδεση ή έγκριση από την ελληνική κυβέρνηση, πολιτικό κόμμα ή τους παρόχους δεδομένων. Η επαγγελματική ιδιότητα του δημιουργού δεν συνεπάγεται θεσμική εκπροσώπηση.</p><h2>Χρηματοδότηση και διαφάνεια</h2><p>Δεν έχει ακόμη δημοσιευθεί δήλωση χρηματοδότησης ή χορηγιών.</p>' if el else
                '<h2>Purpose and project lead</h2><p>Datacritus is an initiative by Ioannis Beris. It makes public data about Greece easier to explore and supports descriptive comparisons of government periods.</p><h2>Independence</h2><p>This is an independent project, without affiliation or endorsement from the Greek government, a political party or its data providers. The creator’s professional role does not imply institutional representation.</p><h2>Funding and transparency</h2><p>A funding or sponsorship statement has not yet been published.</p>'),
            'methodology': ('Μεθοδολογία και απόρρητο' if el else 'Methodology and privacy',
                '<h2>Πηγές και ενημέρωση</h2><p>Χρησιμοποιούμε ελεγμένα στιγμιότυπα στατιστικών API και εκδόσεων ερευνητικών δεδομένων. Η αυτόματη διαδικασία εκτελείται εβδομαδιαία· οι πηγές μπορεί να δημοσιεύουν αραιότερα ή να αναθεωρούν το ιστορικό. Κάθε δείκτης διατηρεί πηγή, μονάδα, έτη και ημερομηνία ανάκτησης. Δεν αποτελούν δεδομένα πραγματικού χρόνου.</p><h2>Κυβερνητικές περίοδοι</h2><p>Χρησιμοποιούνται μόνο πλήρη ημερολογιακά έτη εντός κάθε κυβέρνησης· τα έτη αλλαγής εξαιρούνται. Ο μέσος όρος είναι αριθμητικός μέσος των διαθέσιμων ετήσιων παρατηρήσεων, όχι διάμεσος. Πρώτη/τελευταία σημαίνει πρώτη/τελευταία διαθέσιμη ετήσια παρατήρηση, όχι τιμή την ημέρα ανάληψης ή λήξης. Οι συνεχόμενες κυβερνήσεις διατηρούνται χωριστά.</p><h2>Μεταβολές και κενά</h2><p>Απαιτούνται δύο παρατηρήσεις για μεταβολή. Στα ποσοστά η απόλυτη μεταβολή εκφράζεται σε ποσοστιαίες μονάδες. Οι υπολογισμοί προηγούνται της στρογγυλοποίησης. Τα κενά παραμένουν κενά· δεν μετατρέπονται σε μηδέν ούτε παρεμβάλλονται τιμές.</p><h2>Ερμηνεία</h2><p>Προηγούμενες πολιτικές, κρίσεις, διεθνείς συνθήκες και χρονικές υστερήσεις επηρεάζουν τα αποτελέσματα. Η χρονική σύμπτωση δεν αποδεικνύει αιτιότητα. Δεν υπολογίζουμε συνολικό βαθμό κυβέρνησης. Οι ευρωπαϊκοί μέσοι ακολουθούν τη μεθοδολογία κάθε παρόχου.</p><h2>Απόρρητο</h2><p>Δεν χρησιμοποιούμε λογαριασμούς, αναλυτικά επισκεψιμότητας ή ιχνηλάτες. Οι αποθηκευμένοι δείκτες παραμένουν στον φυλλομετρητή σας. Ο πάροχος φιλοξενίας μπορεί να τηρεί συνήθη αρχεία πρόσβασης. Η επικοινωνία μέσω email υπόκειται και στους αντίστοιχους παρόχους email.</p>' if el else
                '<h2>Sources and updates</h2><p>We use validated snapshots of statistical APIs and versioned research releases. The automated process runs weekly; providers may publish less frequently or revise history. Each indicator retains its source, unit, years and retrieval date. These are not real-time observations.</p><h2>Government periods</h2><p>Only complete calendar years within each cabinet period are used; transition years are excluded. The average is the arithmetic mean of available annual observations, not the median. First/last means the first/last available annual observation, not the value on inauguration or departure day. Consecutive cabinets remain separate.</p><h2>Changes and gaps</h2><p>A change requires two observations. Absolute changes in percentage indicators use percentage points. Calculations precede rounding. Missing values stay missing: no replacement with zero or interpolation.</p><h2>Interpretation</h2><p>Earlier policies, crises, international conditions and time lags affect outcomes. Timing does not establish causation. We do not calculate an overall government score. European aggregates follow each provider’s methodology.</p><h2>Privacy</h2><p>We use no accounts, analytics or trackers. Saved indicators remain in your browser. The hosting provider may retain standard access logs. Email correspondence is also subject to the respective email providers.</p>')}
        for slug,(title,text) in content.items():
            path=f'/{lang}/{slug}/';other='en' if el else 'el'
            body=f'<h1>{title}</h1>'+text+f'<h2>{"Διορθώσεις και επικοινωνία" if el else "Corrections and contact"}</h2><p><a href="mailto:info@datacritus.gr">info@datacritus.gr</a></p>'
            target=ROOT/path.lstrip('/')/'index.html';target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text(document(lang,title,title,path,f'/{other}/{slug}/',body,{'@context':'https://schema.org','@type':'AboutPage' if slug=='about' else 'WebPage','name':title,'url':'https://www.datacritus.gr'+path,'inLanguage':lang}),encoding='utf-8');paths.append(path)
    return paths
