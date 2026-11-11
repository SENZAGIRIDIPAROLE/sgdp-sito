# Sito SGDP – istruzioni rapide

## Prima della pubblicazione (una volta sola)
1. In `build.py` compila: `EMAIL` (email della redazione) e, quando avrai il dominio, `SITE_URL`.
2. In `assets/sito.js` compila `SUBSTACK_URL` con l'indirizzo della tua pubblicazione, es. `https://sgdp.substack.com`.
3. Cancella da `articoli.json` gli articoli di esempio (quelli con `"esempio": true`).
4. Rigenera il sito: `python3 build.py`

## Aggiungere un articolo
Aggiungi una voce in `articoli.json` con: slug, categoria (italia, mondo, economia, europa, tech-scienza),
data (AAAA-MM-GG), edizione (mattino o sera), titolo, sommario, corpo (elenco di paragrafi), fonti ([nome, link]).
Poi lancia `python3 build.py`: home, sezioni e pagina dell'articolo si aggiornano da sole.

## Pubblicazione
Il sito è un insieme di file statici: si pubblica gratis su GitHub Pages caricando questa cartella in un repository.
