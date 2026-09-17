# Slides

Presentasjonen til workshopen, som [Marp](https://marp.app/)-markdown. Ett steg fra
[docs/](../docs/) per del, komprimert til stikkord og kode -- resten av forklaringen ligger
som presenter-notater i HTML-kommentarer.

## Presenter nå (ingenting å bygge)

```bash
cd slides
npx @marp-team/marp-cli@latest -s .
```

Åpner en server på `http://localhost:8080`. Trykk **P** i nettleseren for presenter-view
med notatene synlige. Rediger `slides.md` og siden oppdaterer seg automatisk.

## Bygg en fast HTML-fil

```bash
npx @marp-team/marp-cli@latest slides.md -o slides.html
```

Én selvstendig fil, ingen server nødvendig -- fin å ha liggende klar hvis nettet er dårlig
på presentasjonsdagen. `slides.html` er i `.gitignore`, bygg den på nytt etter endringer.

## PDF (til utskrift eller backup)

```bash
npx @marp-team/marp-cli@latest slides.md -o slides.pdf --allow-local-files
```

Presenter-notatene kommer ikke med i PDFen -- kun i HTML/server-visningen.
