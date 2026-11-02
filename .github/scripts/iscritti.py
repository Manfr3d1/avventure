#!/usr/bin/env python3
"""Aggiorna data-iscritti e data-max delle partenze in index.html dal sito di Avventure nel Mondo."""
import json
import re
import urllib.request

API = ("https://www.viaggiavventurenelmondo.it/api/operative/tours"
       "?fromDate={giorno}&toDate={giorno}&hasAssignment=1&spg={pagina}")
PAGINA = "index.html"


def trova(codice, giorno):
    # le partenze dello stesso giorno sono una ventina al massimo, ma si scorrono le pagine per sicurezza
    viste = set()
    for pagina in range(1, 6):
        richiesta = urllib.request.Request(API.format(giorno=giorno, pagina=pagina),
                                           headers={"User-Agent": "Mozilla/5.0 (iscritti manfreditocci.it)"})
        with urllib.request.urlopen(richiesta, timeout=30) as risposta:
            risultati = json.load(risposta)["data"]["results"]
        nuovi = [t for t in risultati if t.get("id") not in viste]
        if not nuovi:
            return None
        for t in nuovi:
            if t.get("code") == codice:
                return t
            viste.add(t.get("id"))
    return None


html = open(PAGINA, encoding="utf-8").read()
nuovo = html
for tag in re.findall(r'<li class="partenza[^"]*"[^>]*>', html):
    codice = re.search(r'data-partenza="([^"]+)"', tag)
    giorno = re.search(r'data-dal="([^"]+)"', tag)
    if not codice or not giorno:
        continue
    try:
        t = trova(codice.group(1), giorno.group(1))
    except Exception as e:
        print(f"::warning::{codice.group(1)}: sito di Avventure non raggiungibile ({e})")
        continue
    if not t or not isinstance(t.get("pax"), int) or not isinstance(t.get("paxMax"), int):
        print(f"::warning::{codice.group(1)}: partenza non trovata sul sito di Avventure")
        continue
    aggiornato = re.sub(r'data-iscritti="\d*"', f'data-iscritti="{t["pax"]}"', tag)
    aggiornato = re.sub(r'data-max="\d*"', f'data-max="{t["paxMax"]}"', aggiornato)
    print(f'{codice.group(1)}: {t["pax"]} iscritti su {t["paxMax"]}')
    nuovo = nuovo.replace(tag, aggiornato)
if nuovo != html:
    open(PAGINA, "w", encoding="utf-8").write(nuovo)
