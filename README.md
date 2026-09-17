# fastapi-workshop

En workshop der du bygger et fungerende CRUD-API med FastAPI, fra bunnen av. Ca. tre timer,
og du trenger bare grunnleggende Python — resten forklares underveis.

## Var du ikke med på workshopen, eller gikk du tom for tid?

Hele workshopen finnes som en **selvgående håndbok**, og du kan gjøre den helt på egen hånd.
Ingen instruktør nødvendig.

```bash
uv run zensical serve
```

Åpne [http://localhost:8000](http://localhost:8000). Start på steg 1 og jobb deg gjennom —
hvert steg bygger videre på det forrige, og de fleste stegene har en **Observer → hvorfor?**-
boks der du bryter noe med vilje og prøver å forstå hvorfor, før du titter på svaret.

Gikk du tom for tid midt i workshopen? Se hvilket steg du var på i [docs/](docs/) (filnavnene
er nummererte), og fortsett derfra — hvert steg sier hvor `main.py` bør være når du starter.

Sitter du fast, eller vil du sjekke koden din mot en fasit? [docs/solution-key.md](docs/solution-key.md)
har hele det ferdige APIet.

## Layout

- [docs/](docs/) — håndboken, på norsk. Bygget med [zensical](https://zensical.org/), én
  side per steg.
- [code/](code/) — løsningsforslag. `main.py` er det ferdige APIet (in-memory, ingen POST),
  `main_autoid.py` er varianten med server-genererte IDer fra steg 5.

## Kjøre koden selv

```bash
cd code
uv run fastapi dev main.py
```

Se [docs/02-setup.md](docs/02-setup.md) hvis du ikke har `uv` installert ennå.

## Bygge håndboken

```bash
uv run zensical serve      # http://localhost:8000, live reload
uv run zensical build -s   # strict: feiler på ødelagte lenker og anker
```

Kjør fra rot-mappa i repoet. [docs/solution-key.md](docs/solution-key.md) inkluderer koden
direkte fra [code/](code/) med snippets, så den kan ikke komme ut av synk — men
`pymdownx.snippets` løser `base_path` relativt til arbeidsmappa, så bygging fra et annet sted
knekker det. `-s` fanger opp dette.

## Neste workshop

Denne workshopen dekker CRUD, validering, statuskoder og identifikator-design. Persistens
(en ekte database), dependency injection og testing kommer i en oppfølger — bevisst ikke
bygget ut her ennå, så det er en grunn til å komme tilbake. [docs/08-wrap-up.md](docs/08-wrap-up.md)
gir en smakebit på hva som venter.
