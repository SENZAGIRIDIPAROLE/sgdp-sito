#!/usr/bin/env python3
"""SGDP – generatore del sito.

Uso:
    python3 build.py                 crea tutte le pagine HTML da articoli.json
    python3 build.py --anteprima DIR crea una copia per l'anteprima su Claude

Per aggiungere un articolo: aggiungi una voce in cima ad articoli.json e rilancia lo script.
"""
import html, json, math, os, shutil, sys
from datetime import date

# ---------------- Impostazioni da completare ----------------
SITE_URL = ""            # es. "https://sgdp.it" (serve per le anteprime dei link sui social)
EMAIL = "redazione.sgdp@gmail.com"  # email della redazione
SUBSTACK_URL = "https://senzagiridiparolesgdp.substack.com"  # pubblicazione Substack (anche in sito.js)
TITOLARE = "Ionut Gaucan"
VERSIONE_PRIVACY = "1.0 – 11 novembre 2026"
# ------------------------------------------------------------

QUI = os.path.dirname(os.path.abspath(__file__))
ASSET = ["style.css", "sito.js", "favicon.svg", "condivisione.png", "inter-latin-400-normal.woff2", "inter-latin-600-normal.woff2", "inter-latin-800-normal.woff2"]
import time
VERSIONE = str(int(time.time()))  # forza il browser a caricare i file aggiornati
SOCIAL = [
    ("Telegram", "https://t.me/SenzaGiriDiParole"),
    ("WhatsApp", "https://whatsapp.com/channel/0029VbET1P084Om58ja6zZ1t"),
    ("Instagram", "https://www.instagram.com/sgdpsenzagiridiparole/"),
    ("Facebook", "https://www.facebook.com/profile.php?id=61596050924338"),
    ("LinkedIn", "https://www.linkedin.com/company/sgdp-senza-giri-di-parole/"),
    ("X", "https://x.com/SGDParole"),
]
CATEGORIE = {
    "italia": ("Italia", "Politica, governo, leggi e fatti che riguardano il Paese."),
    "mondo": ("Mondo", "Esteri, crisi internazionali e organizzazioni globali."),
    "economia": ("Economia", "Prezzi, lavoro, tasse, mercati e conti pubblici."),
    "europa": ("Europa", "Unione europea, istituzioni e decisioni che arrivano in Italia."),
    "tech-scienza": ("Tech e scienza", "Tecnologia, intelligenza artificiale, ricerca e salute."),
}
GIORNI = ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica"]
MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto",
        "settembre", "ottobre", "novembre", "dicembre"]
e = html.escape


def data_it(s, giorno=False):
    d = date.fromisoformat(s)
    t = f"{d.day} {MESI[d.month - 1]} {d.year}"
    return (GIORNI[d.weekday()].capitalize() + " " + t) if giorno else t


def parole(a):
    return len((" ".join([a["sommario"]] + a["corpo"])).split())


# ---------------- Pezzi comuni ----------------
def testa(titolo, descrizione, r, percorso, anteprima_index=False, og_tipo="website"):
    url = (SITE_URL.rstrip("/") + "/" + percorso) if SITE_URL else ""
    og = [f'<meta property="og:title" content="{e(titolo)}">',
          f'<meta property="og:description" content="{e(descrizione)}">',
          f'<meta property="og:type" content="{og_tipo}">',
          '<meta property="og:site_name" content="SGDP – Senza giri di parole">',
          '<meta property="og:locale" content="it_IT">',
          '<meta name="twitter:card" content="summary_large_image">']
    if SITE_URL:
        og += [f'<meta property="og:url" content="{e(url)}">',
               f'<meta property="og:image" content="{e(SITE_URL.rstrip("/"))}/condivisione.png">',
               f'<link rel="canonical" href="{e(url)}">']
    righe = [f"<title>{e(titolo)}</title>",
             f'<meta name="description" content="{e(descrizione)}">',
             *og,
             f'<link rel="icon" href="{r}favicon.svg" type="image/svg+xml">',
             f'<link rel="stylesheet" href="{r}style.css?v={VERSIONE}">']
    if anteprima_index:
        righe.insert(1, '<meta name="claude:viewport-fit-sides" content="cover">')
        return "\n".join(righe) + "\n"
    return ('<!doctype html>\n<html lang="it">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            '<meta name="claude:viewport-fit-sides" content="cover">\n'
            + "\n".join(righe) + "\n</head>\n<body>\n")


def testata(r, attiva=None):
    voci = []
    for k, (nome, _) in CATEGORIE.items():
        cur = ' aria-current="page"' if attiva == k else ""
        voci.append(f'<li class="cat-{k}"><a href="{r}{k}.html"{cur} style="--cat: var(--c-{k})">{nome}</a></li>')
    cur = ' aria-current="page"' if attiva == "come-lavoriamo" else ""
    voci.append(f'<li><a href="{r}come-lavoriamo.html"{cur}>Come lavoriamo</a></li>')
    return f'''<a class="salta" href="#contenuto">Vai al contenuto</a>
<header class="testata">
  <div class="gutter"><div class="contenitore testata-riga">
    <a class="marchio" href="{r}index.html" aria-label="SGDP, pagina iniziale"><b>SGDP</b><span>Senza giri di parole</span></a>
    <a class="bottone" href="{r}newsletter.html">Iscriviti gratis</a>
  </div></div>
  <nav class="nav" aria-label="Sezioni"><div class="gutter"><ul class="contenitore">{"".join(voci)}</ul></div></nav>
</header>
'''


def piede(r, anteprima_index=False):
    sezioni = "".join(f'<li><a href="{r}{k}.html">{n}</a></li>' for k, (n, _) in CATEGORIE.items())
    social = "".join(f'<li><a href="{u}" target="_blank" rel="noopener">{n}</a></li>' for n, u in SOCIAL)
    chiusura = "" if anteprima_index else "</body>\n</html>\n"
    return f'''<footer class="piede">
  <div class="gutter"><div class="contenitore piede-interno">
    <div><a class="marchio" href="{r}index.html"><b>SGDP</b></a><p>Le notizie che contano per chi vive in Italia, senza giri di parole. Fonti sempre visibili.</p></div>
    <div><h2>Sezioni</h2><ul>{sezioni}</ul></div>
    <div><h2>SGDP</h2><ul><li><a href="{r}newsletter.html">Newsletter</a></li><li><a href="{r}come-lavoriamo.html">Come lavoriamo</a></li><li><a href="{r}correzioni.html">Correzioni</a></li><li><a href="{r}contatti.html">Contatti</a></li></ul></div>
    <div><h2>Note legali</h2><ul><li><a href="{r}privacy.html">Informativa privacy</a></li><li><a href="{r}cookie.html">Cookie e memoria locale</a></li></ul></div>
    <div><h2>Seguici</h2><ul>{social}</ul></div>
  </div></div>
  <div class="gutter"><div class="contenitore piede-legale">
    <span>© 2026 SGDP – Senza giri di parole</span>
    <span>Progetto editoriale di {e(TITOLARE)}</span>
    <span>Contatti: {e(EMAIL)}</span>
    <span>Testi redatti con AI e verificati dalla redazione</span>
  </div></div>
</footer>
<script src="{r}sito.js?v={VERSIONE}"></script>
{chiusura}'''


def modulo(p, r, cta="Iscriviti gratis"):
    return f'''<form class="modulo" action="{SUBSTACK_URL}/subscribe" method="get" target="_blank" novalidate aria-label="Iscrizione alla newsletter">
  <div class="riga-campo">
    <label class="etichetta-campo" for="{p}-email">La tua email</label>
    <input type="email" id="{p}-email" name="email" autocomplete="email" placeholder="La tua email" required>
    <button class="bottone" type="submit">{cta}</button>
  </div>
  <label class="consenso" for="{p}-c1"><input type="checkbox" id="{p}-c1" required data-nome="il consenso a ricevere la newsletter"><span>Voglio ricevere la newsletter di SGDP. Posso disiscrivermi in qualsiasi momento con un clic.</span></label>
  <label class="consenso" for="{p}-c2"><input type="checkbox" id="{p}-c2" required data-nome="la conferma di aver letto l'informativa e di avere almeno 14 anni"><span>Ho letto l'<a href="{r}privacy.html">informativa privacy</a> e ho almeno 14 anni.</span></label>
  <p class="errore" role="alert" hidden></p>
  <div class="passo2" hidden>
    <strong>Quasi fatto: completa l'iscrizione su Substack.</strong>
    <span class="istruzioni">Si è aperta una nuova scheda di Substack, la piattaforma che invia la nostra newsletter. Clicca <b>Iscriviti</b> e poi conferma dal link che ricevi via email. Non serve creare un account.</span>
    <span class="avviso-config" hidden>Modalità di prova: il sito non è ancora collegato a Substack, quindi questa iscrizione non è stata registrata.</span>
  </div>
  <p class="nota">Raccogliamo solo la tua email, gestita da Substack per l'invio. Niente spam e nessuna cessione a terzi. <a href="{r}privacy.html">Leggi l'informativa</a>.</p>
</form>'''


def etichetta(cat, r, link=True):
    nome = CATEGORIE[cat][0]
    if link:
        return f'<a class="etichetta cat-{cat}" href="{r}{cat}.html">{nome}</a>'
    return f'<span class="etichetta cat-{cat}">{nome}</span>'


def riga_meta(a):
    n = parole(a)
    minuti = max(1, math.ceil(n / 200))
    fonti = len(a["fonti"])
    return (f'<p class="meta"><span>{data_it(a["data"])}</span><span>Edizione {"del mattino" if a["edizione"] == "mattino" else "della sera"}</span>'
            f'<span>{n} parole · {minuti} min</span><span>{fonti} fonti</span></p>')


def voce_elenco(a, r, cartella=""):
    esempio = '<span class="esempio">Articolo di esempio</span>' if a.get("esempio") else ""
    return f'''<article class="cat-{a["categoria"]}">
  <p class="quando"><b>{data_it(a["data"])}</b>{"Mattino" if a["edizione"] == "mattino" else "Sera"}</p>
  <div class="testo">
    <div class="meta">{etichetta(a["categoria"], r)}{esempio}</div>
    <h3><a href="{r}{a["slug"]}.html">{e(a["titolo"])}</a></h3>
    <p>{e(a["sommario"])}</p>
  </div>
</article>'''


def banda(r, p):
    return f'''<section class="banda" aria-labelledby="{p}-titolo">
  <div class="gutter"><div class="contenitore banda-interno">
    <div><h2 id="{p}-titolo">Leggi gli articoli completi. Gratis.</h2><p>Con l'iscrizione alla newsletter sblocchi tutti gli articoli del sito e ricevi ogni domenica “La settimana in 200 parole”.</p></div>
    {modulo(p, r)}
  </div></div>
</section>'''


# ---------------- Pagine ----------------
def pagina_home(articoli, anteprima=False):
    r = ""
    prima, *resto = articoli
    laterali, altri = resto[:2], resto[2:]
    lat = "".join(f'''<article class="cat-{a["categoria"]}"><div class="meta">{etichetta(a["categoria"], r)}</div><h3><a href="{a["slug"]}.html">{e(a["titolo"])}</a></h3>{riga_meta(a)}</article>''' for a in laterali)
    esempio = '<span class="esempio">Articolo di esempio</span>' if prima.get("esempio") else ""
    corpo = f'''{testata(r)}
<main id="contenuto">
  <div class="gutter"><div class="contenitore">
    <p class="riga-data"><span><strong>{data_it(articoli[0]["data"], True)}</strong> · Ultimo aggiornamento: edizione {"del mattino" if articoli[0]["edizione"] == "mattino" else "della sera"}</span><span>Le notizie che contano, senza giri di parole</span></p>
    <div class="apertura">
      <article class="apertura-principale cat-{prima["categoria"]}">
        <div class="meta">{etichetta(prima["categoria"], r)}{esempio}</div>
        <h2><a href="{prima["slug"]}.html">{e(prima["titolo"])}</a></h2>
        <p class="sommario">{e(prima["sommario"])}</p>
        {riga_meta(prima)}
      </article>
      <div class="laterale" aria-label="Altre notizie in evidenza">{lat}</div>
    </div>
  </div></div>
  {banda(r, "home")}
  <div class="gutter"><div class="contenitore">
    <section class="elenco" aria-labelledby="ultime"><h2 id="ultime" class="titolo-sezione" style="padding-top:28px">Ultime notizie</h2>{"".join(voce_elenco(a, r) for a in altri) or '<p class="vuoto">Le prossime notizie arrivano con la prossima edizione.</p>'}</section>
    <section aria-labelledby="metodo" style="padding-bottom:48px; display:grid; gap:14px">
      <h2 id="metodo" class="titolo-sezione">Come lavoriamo</h2>
      <div class="principi">
        <div><b>Due fonti per ogni fatto</b><span>O una fonte ufficiale primaria. Le trovi sempre in fondo all'articolo.</span></div>
        <div><b>Una persona approva</b><span>Testi redatti con AI, controllati e approvati dalla redazione prima di uscire.</span></div>
        <div><b>Correzioni pubbliche</b><span>Se sbagliamo lo diciamo, nella pagina <a href="correzioni.html">Correzioni</a>.</span></div>
      </div>
    </section>
  </div></div>
</main>
{piede(r, anteprima)}'''
    return testa("SGDP – Senza giri di parole", "Le notizie che contano per chi vive in Italia, senza giri di parole. Fonti sempre visibili.", r, "", anteprima) + corpo


def pagina_sezione(cat, articoli):
    r = ""
    nome, desc = CATEGORIE[cat]
    lista = [a for a in articoli if a["categoria"] == cat]
    voci = "".join(voce_elenco(a, r) for a in lista) or f'<p class="vuoto">Nessun articolo in {nome} per ora. Le prossime notizie arrivano con la prossima edizione.</p>'
    return testa(f"{nome} · SGDP", desc, r, f"{cat}.html") + f'''{testata(r, cat)}
<main id="contenuto">
  <div class="gutter"><div class="contenitore">
    <div class="riga-data cat-{cat}" style="border-bottom: 4px solid var(--cat)"><span><strong style="font-size:var(--t-xl); font-weight:800; letter-spacing:-0.02em">{nome}</strong></span><span>{desc}</span></div>
    <section class="elenco" aria-label="Articoli di {nome}">{voci}</section>
  </div></div>
  {banda(r, "sez")}
</main>
{piede(r)}'''


def pagina_articolo(a, articoli):
    r = ""
    paragrafi = "\n".join(f"<p>{e(p)}</p>" for p in a["corpo"])
    fonti = "".join(f'<li><a href="{e(u)}" target="_blank" rel="noopener">{e(n)}</a></li>' for n, u in a["fonti"])
    esempio = '<span class="esempio">Articolo di esempio</span>' if a.get("esempio") else ""
    altri = [x for x in articoli if x["slug"] != a["slug"]][:3]
    return testa(f'{a["titolo"]} · SGDP', a["sommario"], r, f'{a["slug"]}.html', og_tipo="article") + f'''{testata(r, a["categoria"])}
<main id="contenuto">
  <div class="gutter">
  <article class="articolo cat-{a["categoria"]}">
    <div class="riga-top">{etichetta(a["categoria"], r)}{esempio}</div>
    <h1>{e(a["titolo"])}</h1>
    <p class="sommario">{e(a["sommario"])}</p>
    {riga_meta(a)}
    <div class="corpo bloccato" id="corpo" inert aria-hidden="true">
{paragrafi}
    </div>
    <section class="muro" aria-labelledby="muro-titolo">
      <h2 id="muro-titolo">Continua a leggere gratis</h2>
      <p class="perche">L'articolo completo è riservato agli iscritti alla newsletter. L'iscrizione è gratuita e richiede un minuto.</p>
      {modulo("art", r, "Iscriviti e leggi")}
      <p class="gia">Sei già iscritto? <button type="button" aria-controls="gia-iscritto">Sblocca l'articolo</button></p>
      <form id="gia-iscritto" class="modulo modulo-gia" novalidate hidden>
        <div class="riga-campo"><label class="etichetta-campo" for="gia-email">Email con cui ti sei iscritto</label><input type="email" id="gia-email" autocomplete="email" placeholder="Email con cui ti sei iscritto"><button class="bottone" type="submit">Sblocca</button></div>
        <p class="errore" role="alert" hidden></p>
      </form>
    </section>
    <section class="fonti" aria-labelledby="fonti-titolo">
      <h2 id="fonti-titolo" class="titolo-sezione">Fonti</h2>
      <ol>{fonti}</ol>
    </section>
    <p class="trasparenza">Testo redatto con AI e verificato dalla redazione di SGDP. Hai trovato un errore? Scrivi a {e(EMAIL)}. Leggi <a href="come-lavoriamo.html">come lavoriamo</a> e le <a href="correzioni.html">correzioni</a>.</p>
  </article>
  <section class="dopo" aria-labelledby="altri-titolo">
    <h2 id="altri-titolo" class="titolo-sezione">Altri articoli</h2>
    <div class="elenco">{"".join(voce_elenco(x, r) for x in altri)}</div>
  </section>
  </div>
</main>
{piede(r)}'''


def pagina_testo(nome_file, titolo, descrizione, contenuto, attiva=None):
    r = ""
    return testa(f"{titolo} · SGDP", descrizione, r, nome_file) + f'''{testata(r, attiva)}
<main id="contenuto"><div class="gutter"><div class="pagina">
{contenuto}
</div></div></main>
{piede(r)}'''


def pagina_newsletter():
    c = f'''<h1>La newsletter di SGDP</h1>
<p class="attacco">Le notizie che contano, ogni domenica nella tua email. E l'accesso gratuito a tutti gli articoli completi del sito.</p>
<div class="riquadro">{modulo("nl", "")}</div>
<h2>Cosa ricevi</h2>
<ul>
  <li>L'accesso a tutti gli articoli completi pubblicati sul sito.</li>
  <li>Ogni domenica, “La settimana in 200 parole”: le notizie più importanti dei sette giorni, con le fonti.</li>
  <li>Niente spam e niente pubblicità invadente. Gli eventuali contenuti sponsorizzati sono sempre dichiarati.</li>
</ul>
<h2>Come funziona l'iscrizione</h2>
<ol>
  <li>Inserisci la tua email e spunta i due consensi.</li>
  <li>Si apre Substack, la piattaforma che invia la newsletter: confermi lì.</li>
  <li>Ricevi un'email con il link di conferma. Da quel momento sei iscritto.</li>
</ol>
<h2>I tuoi dati, in breve</h2>
<p>Ci serve solo la tua email. Substack registra anche data e provenienza dell'iscrizione e, per le statistiche, se apri le email e su quali link clicchi. Non vendiamo e non cediamo i tuoi dati a nessuno, sponsor compresi. Puoi disiscriverti in qualsiasi momento dal link presente in ogni email. Tutti i dettagli sono nell'<a href="privacy.html">informativa privacy</a>.</p>'''
    return pagina_testo("newsletter.html", "Newsletter", "Iscriviti gratis alla newsletter di SGDP e leggi gli articoli completi.", c)


def pagina_come_lavoriamo():
    c = f'''<h1>Come lavoriamo</h1>
<p class="attacco">SGDP racconta le notizie che contano per chi vive in Italia, senza giri di parole. Qui spieghiamo come lavoriamo, così puoi controllarci.</p>
<h2>Due formati</h2>
<p>Sui social trovi la notizia in massimo 200 parole: cosa è successo, perché conta, cosa succede ora. Sul sito trovi l'articolo completo, con contesto e numeri, gratis per chi è iscritto alla newsletter.</p>
<h2>Le fonti</h2>
<ul>
  <li>Pubblichiamo un fatto solo se è confermato da almeno due fonti indipendenti o da una fonte ufficiale primaria: istituzioni, banche centrali, istituti di statistica, atti pubblicati.</li>
  <li>Le testate giornalistiche ci servono per sapere cosa sta succedendo. I nostri testi sono scritti da zero e non riprendono gli articoli di altri.</li>
  <li>Le fonti sono sempre elencate in fondo a ogni articolo, visibili anche a chi non è iscritto.</li>
</ul>
<h2>L'intelligenza artificiale</h2>
<p>I testi sono redatti con l'aiuto dell'intelligenza artificiale. Ogni numero, nome e data viene controllato sulle fonti, e una persona approva ogni articolo prima della pubblicazione. Lo dichiariamo su ogni contenuto con la frase “Testo redatto con AI e verificato dalla redazione”.</p>
<h2>Tono</h2>
<p>Linguaggio semplice e neutro. Niente opinioni nelle notizie, niente titoli acchiappaclic. Sui temi politici riportiamo le posizioni delle parti coinvolte.</p>
<h2>Errori e correzioni</h2>
<p>Se sbagliamo, correggiamo e lo diciamo. Gli errori di dettaglio vengono corretti con una nota in fondo all'articolo; gli errori sostanziali con una rettifica pubblica su tutti i canali. Trovi tutto nella pagina <a href="correzioni.html">Correzioni</a>.</p>
<h2>Sponsor e indipendenza</h2>
<p>I contenuti sponsorizzati sono sempre indicati come tali. Gli sponsor non decidono di quali notizie parliamo né come. Agli sponsor non diamo mai i dati degli iscritti, al massimo numeri aggregati e anonimi.</p>
<h2>Chi c'è dietro</h2>
<p>SGDP è un progetto editoriale indipendente di {e(TITOLARE)}. Per qualsiasi domanda: <a href="contatti.html">contatti</a>.</p>'''
    return pagina_testo("come-lavoriamo.html", "Come lavoriamo", "Fonti, uso dell'AI, correzioni e indipendenza: il metodo di SGDP.", c, "come-lavoriamo")


def pagina_correzioni():
    c = f'''<h1>Correzioni</h1>
<p class="attacco">Qui elenchiamo ogni errore corretto negli articoli di SGDP, con la data e cosa è cambiato.</p>
<div class="tabella"><table>
  <thead><tr><th scope="col">Data</th><th scope="col">Articolo</th><th scope="col">Cosa abbiamo corretto</th></tr></thead>
  <tbody><tr><td colspan="3">Nessuna correzione finora.</td></tr></tbody>
</table></div>
<h2>Come segnalare un errore</h2>
<p>Scrivi a <strong>{e(EMAIL)}</strong> indicando l'articolo, cosa non è corretto e, se puoi, una fonte. Controlliamo ogni segnalazione.</p>
<h2>Come correggiamo</h2>
<div class="tabella"><table>
  <thead><tr><th scope="col">Tipo di errore</th><th scope="col">Esempio</th><th scope="col">Cosa facciamo</th></tr></thead>
  <tbody>
    <tr><td>Refuso</td><td>Errore di battitura che non cambia il senso</td><td>Correggiamo il testo.</td></tr>
    <tr><td>Errore di dettaglio</td><td>Una data o una cifra secondaria</td><td>Correggiamo entro 2 ore e aggiungiamo una nota in fondo all'articolo.</td></tr>
    <tr><td>Errore sostanziale</td><td>Il fatto principale è sbagliato</td><td>Entro 1 ora rimuoviamo il contenuto da tutti i canali e pubblichiamo una rettifica.</td></tr>
  </tbody>
</table></div>'''
    return pagina_testo("correzioni.html", "Correzioni", "Gli errori corretti negli articoli di SGDP e come segnalarne uno.", c)


def pagina_contatti():
    c = f'''<h1>Contatti</h1>
<p class="attacco">Per qualsiasi richiesta scrivi alla redazione via email. È l'unico canale di contatto di SGDP.</p>
<div class="riquadro">
  <div class="email-box"><code id="email-redazione">{e(EMAIL)}</code><button class="bottone secondario" type="button" data-copia="email-redazione">Copia</button></div>
  <p class="meta" id="esito-copia" aria-live="polite"></p>
</div>
<h2>Scrivici per</h2>
<ul>
  <li>Segnalare un errore in un articolo, indicando l'articolo e una fonte.</li>
  <li>Proporre una notizia o un tema.</li>
  <li>Chiedere informazioni su sponsorizzazioni e collaborazioni.</li>
  <li>Esercitare i tuoi diritti sui dati personali, come previsto dall'<a href="privacy.html">informativa privacy</a>.</li>
</ul>
<p>Proviamo a rispondere entro due giorni lavorativi.</p>'''
    return pagina_testo("contatti.html", "Contatti", "Come contattare la redazione di SGDP.", c)


def pagina_privacy():
    c = f'''<h1>Informativa privacy</h1>
<p class="aggiornato">Versione {VERSIONE_PRIVACY}</p>
<p class="attacco">Questa informativa spiega quali dati personali tratta SGDP, perché e per quanto tempo, ai sensi degli articoli 13 e 14 del Regolamento (UE) 2016/679 (GDPR).</p>

<h2>1. Titolare del trattamento</h2>
<p>{e(TITOLARE)}, curatore del progetto editoriale SGDP – Senza giri di parole. Contatto: {e(EMAIL)}.</p>

<h2>2. Quali dati trattiamo</h2>
<ul>
  <li><strong>Dati di navigazione.</strong> Il sito è ospitato su GitHub Pages (GitHub, Inc.). Il fornitore registra nei log del server dati tecnici come indirizzo IP, tipo di browser, data e ora della visita, per sicurezza e funzionamento del servizio. SGDP non usa questi dati per identificare chi visita il sito.</li>
  <li><strong>Iscrizione alla newsletter.</strong> Il tuo indirizzo email. Attraverso Substack, la piattaforma che gestisce la newsletter, sono trattati anche: data, ora e provenienza dell'iscrizione; indirizzo IP e Paese approssimativo; dati sull'apertura delle email e sui clic sui link, usati per statistiche; le eventuali sezioni che scegli di ricevere.</li>
  <li><strong>Email che ci scrivi.</strong> Il tuo indirizzo email e il contenuto del messaggio.</li>
  <li><strong>Memoria locale del browser.</strong> Un indicatore tecnico che ricorda che hai sbloccato gli articoli. Non contiene la tua email. Dettagli nella pagina <a href="cookie.html">Cookie e memoria locale</a>.</li>
</ul>
<p>Il modulo di iscrizione del sito non salva la tua email: la passa a Substack quando confermi l'iscrizione. Non raccogliamo dati che non servono alle finalità indicate qui sotto.</p>

<h2>3. Finalità, base giuridica e conservazione</h2>
<div class="tabella"><table>
  <thead><tr><th scope="col">Finalità</th><th scope="col">Base giuridica</th><th scope="col">Per quanto tempo</th></tr></thead>
  <tbody>
    <tr><td>Inviarti la newsletter e darti accesso agli articoli completi</td><td>Il tuo consenso (art. 6.1.a GDPR)</td><td>Fino alla disiscrizione o alla revoca del consenso</td></tr>
    <tr><td>Statistiche su aperture e clic per migliorare la newsletter</td><td>Legittimo interesse del titolare (art. 6.1.f); puoi opporti in qualsiasi momento</td><td>Per la durata dell'iscrizione</td></tr>
    <tr><td>Rispondere a richieste e segnalazioni via email</td><td>Richiesta dell'interessato e legittimo interesse (art. 6.1.b e 6.1.f)</td><td>Il tempo necessario a gestire la richiesta, al massimo 24 mesi</td></tr>
    <tr><td>Sicurezza e funzionamento del sito</td><td>Legittimo interesse (art. 6.1.f)</td><td>Secondo i tempi del fornitore di hosting</td></tr>
    <tr><td>Adempiere a obblighi di legge</td><td>Obbligo legale (art. 6.1.c)</td><td>Per i tempi previsti dalla legge</td></tr>
  </tbody>
</table></div>
<p>Dopo la disiscrizione la tua email viene cancellata dalla lista o resa anonima entro 30 giorni, salvo obblighi di legge.</p>

<h2>4. Obbligo di fornire i dati</h2>
<p>L'email è necessaria per iscriverti alla newsletter: senza non è possibile inviarla. Le caselle di consenso non sono mai preselezionate.</p>

<h2>5. Minori</h2>
<p>L'iscrizione è riservata a chi ha almeno 14 anni, età minima prevista in Italia per prestare da soli il consenso ai servizi online (art. 2-quinquies del D.Lgs. 196/2003).</p>

<h2>6. Chi riceve i dati</h2>
<ul>
  <li><strong>Substack, Inc.</strong> (Stati Uniti), che gestisce l'invio della newsletter come responsabile del trattamento.</li>
  <li><strong>GitHub, Inc.</strong> (Stati Uniti), che ospita il sito.</li>
  <li>Il fornitore della casella email della redazione, per i messaggi che ci invii.</li>
</ul>
<p>Non vendiamo e non cediamo i dati a terzi. Gli sponsor non ricevono dati degli iscritti, ma al massimo numeri aggregati e anonimi.</p>

<h2>7. Trasferimenti fuori dall'Unione europea</h2>
<p>Substack e GitHub hanno sede negli Stati Uniti. I trasferimenti avvengono sulla base delle garanzie previste dagli articoli 45 e 46 del GDPR: la decisione di adeguatezza UE-USA (Data Privacy Framework) per le società che vi aderiscono, oppure le clausole contrattuali standard approvate dalla Commissione europea.</p>

<h2>8. I tuoi diritti</h2>
<p>Puoi chiedere in qualsiasi momento di accedere ai tuoi dati, correggerli, cancellarli, limitarne il trattamento, riceverli in un formato leggibile (portabilità) e opporti al trattamento basato sul legittimo interesse (articoli 15–22 GDPR). Puoi revocare il consenso con il link di disiscrizione presente in ogni email o scrivendo a {e(EMAIL)}; la revoca non incide sui trattamenti già effettuati. Rispondiamo entro un mese.</p>
<p>Se ritieni che il trattamento violi il GDPR, puoi presentare reclamo al Garante per la protezione dei dati personali (<a href="https://www.garanteprivacy.it" target="_blank" rel="noopener">garanteprivacy.it</a>).</p>

<h2>9. Decisioni automatizzate</h2>
<p>Non prendiamo decisioni basate unicamente su trattamenti automatizzati e non facciamo profilazione per finalità di marketing.</p>

<h2>10. Modifiche</h2>
<p>Possiamo aggiornare questa informativa. La versione in vigore è sempre su questa pagina, con la data di aggiornamento in alto.</p>'''
    return pagina_testo("privacy.html", "Informativa privacy", "Come SGDP tratta i dati personali di lettori e iscritti alla newsletter.", c)


def pagina_cookie():
    c = '''<h1>Cookie e memoria locale</h1>
<p class="aggiornato">Versione ''' + VERSIONE_PRIVACY + '''</p>
<p class="attacco">Il sito di SGDP non usa cookie di profilazione, né strumenti di statistica, né pubblicità.</p>
<h2>Cosa usiamo</h2>
<div class="tabella"><table>
  <thead><tr><th scope="col">Nome</th><th scope="col">Tipo</th><th scope="col">A cosa serve</th><th scope="col">Durata</th></tr></thead>
  <tbody><tr><td>sgdp_iscritto</td><td>Memoria locale del browser (tecnica)</td><td>Ricorda che hai sbloccato gli articoli, così non devi farlo a ogni visita. Non contiene dati personali.</td><td>Finché non la cancelli dal browser</td></tr></tbody>
</table></div>
<p>Si tratta di uno strumento tecnico, necessario al servizio che hai richiesto. Secondo le Linee guida del Garante per la protezione dei dati personali del 10 giugno 2021, per gli strumenti tecnici non è richiesto il consenso, quindi il sito non mostra un banner.</p>
<h2>Contenuti di terze parti</h2>
<p>Il sito non incorpora contenuti di terze parti: i caratteri sono ospitati sul nostro server e non ci sono video, mappe o pulsanti social integrati. I link verso Substack e i social portano su siti esterni, che hanno le proprie regole sui cookie.</p>
<h2>Come cancellarla</h2>
<p>Puoi cancellare la memoria locale dalle impostazioni del browser, alla voce che riguarda i dati dei siti. Gli articoli torneranno bloccati fino al prossimo sblocco.</p>
<h2>Modifiche</h2>
<p>Se in futuro aggiungeremo strumenti di statistica o altri cookie, aggiorneremo questa pagina e, quando la legge lo richiede, chiederemo il tuo consenso prima di attivarli.</p>'''
    return pagina_testo("cookie.html", "Cookie e memoria locale", "Quali strumenti tecnici usa il sito di SGDP.", c)


# ---------------- Esecuzione ----------------
def scrivi(base, nome, testo):
    p = os.path.join(base, nome)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(testo)


def costruisci(base, anteprima=False):
    with open(os.path.join(QUI, "articoli.json"), encoding="utf-8") as f:
        articoli = json.load(f)
    articoli.sort(key=lambda a: (a["data"], a["edizione"] == "sera"), reverse=True)
    scrivi(base, "index.html", pagina_home(articoli, anteprima))
    for k in CATEGORIE:
        scrivi(base, f"{k}.html", pagina_sezione(k, articoli))
    for a in articoli:
        scrivi(base, f"{a['slug']}.html", pagina_articolo(a, articoli))
    scrivi(base, "newsletter.html", pagina_newsletter())
    scrivi(base, "come-lavoriamo.html", pagina_come_lavoriamo())
    scrivi(base, "correzioni.html", pagina_correzioni())
    scrivi(base, "contatti.html", pagina_contatti())
    scrivi(base, "privacy.html", pagina_privacy())
    scrivi(base, "cookie.html", pagina_cookie())
    return len(articoli)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--anteprima":
        dest = os.path.abspath(sys.argv[2])
        if os.path.exists(dest):
            shutil.rmtree(dest)
        os.makedirs(dest)
        for f in ASSET:
            shutil.copy(os.path.join(QUI, f), dest)
        n = costruisci(dest, anteprima=True)
    else:
        n = costruisci(QUI)
    print(f"Sito generato: {n} articoli.")
