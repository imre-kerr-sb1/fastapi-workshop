# 2. Prosjektoppsett

Tre-fire kjappe kommandoer.

## Ha et sted å jobbe
Du kan gjøre alt dette på laptopen din. For dataplattform-brukere er det vel så greit å lage seg et Coder-workspace,
så slipper man å tenke på python-versjoner og installering av `uv`.

## Installer `uv`

[`uv`](https://docs.astral.sh/uv/) håndterer dependency-versjoner og virtuelle Python-miljøer.
Mye enklere enn å stuke med `pip` og `venv`.

(Workshop-deltakere som sitter i Coder har dette ferdig installert i workspace.)

=== "macOS / Linux"

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

=== "Windows"

    ```powershell
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

## Lag et prosjekt

```bash
uv init fastapi-workshop
cd fastapi-workshop
uv add "fastapi[standard]"
```

Du har nå en `pyproject.toml` og `uv.lock`, en `.venv` med FastAPI installert, og én Python-fil (`main.py`).
Du kan beholde `main.py`, men slett innholdet. Det kommer vi til å erstatte i neste steg.

!!! tip "Hva er `[standard]`?"
    FastAPI er selve rammeverket, men for å være nyttig trenger det en del moduler som ikke følger med som
    default. Grunnen til dette er at man i noen tilfeller har lyst til å utelate noe, eller bytte noe ut med alternative pakker.
    `[standard]` drar inn et fornuftig sett med defaults som er nok for de aller fleste:

    - **`uvicorn`** — webserveren. Dette er biten som faktisk håndterer TCP og HTTP på det laveste nivået.
        FastAPI sender og mottar fra denne. 
    - **`fastapi-cli`** — Et par kommandoer som gjør det enkelt å kjøre opp APIet ditt. (Og noen FastAPI Cloud-greier som vi ikke bryr oss om.)
    - **`httpx`** — en HTTP-klient, brukes til testing.
    - **`jinja2`**, **`python-multipart`** og noen andre. — templates og form-parsing, som vi ikke kommer til å bruke i dag.

    Den eneste helt nødvendige komponenten her er `uvicorn`, alt annet kunne vi strengt tatt droppet.

## Sjekk at det virket

```bash
uv run python -c "import fastapi; print(fastapi.__version__)"
```

Får du opp et versjonsnummer? I så fall har du gjort alt riktig, og vi kan gå videre til å faktisk kode litt.
