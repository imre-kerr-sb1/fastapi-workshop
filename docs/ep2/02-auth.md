# 2. Autentisering

Akkurat nå er alle endepunktene i APIet ditt åpne for alle som kan koble til, selv de som
oppdaterer eller sletter data. Skal du eksponere det på internett er det en god idé å kreve en form
for autentisering. Dette er et stort tema, og jeg anbefaler å lese [FastAPIs egen dokumentasjon om
temaet](https://fastapi.tiangolo.com/tutorial/security/).

Vi skal legge til enkel autentisering med en API-nøkkel. Dette er bare en av mange autentiseringsformer
som støttes av FastAPI. Andre det kan være nyttig å være klar over er HTTP Basic Authentication, OAuth2
(herunder client credentials og authorization code) og OpenID Connect.

## Implementasjon
Først importerer du den nødvendige klassen, og lager et objekt som representerer autentiseringsmetoden:

```python
from fastapi.security import APIKeyHeader # API key comes from a header. Also available: APIKeyQuery and APIKeyCookie

auth_scheme = APIKeyHeader(name="X-Api-Key")
```

Så trenger vi en funksjon som sjekker at API-nøkkelen har riktig verdi:

```python
import os
import secrets
from typing import Annotated

from fastapi import Depends

# Will KeyError if the environment variable is not set. 
# This is good, we do *not* want a default here.
ADMIN_API_KEY = os.environ["ADMIN_API_KEY"]

def check_api_key_value(api_key: Annotated[str, Depends(auth_scheme)]) -> str:
    if not secrets.compare_digest(api_key, ADMIN_API_KEY):  # != on strings is vulnerable to timing attacks
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect API Key",
        )
    return api_key
```

Til slutt legger du til denne funksjonen som en "dependency" i hver funksjon som krever autentisering:

```python hl_lines="5"
@app.put(
    "/pokemon/{slug}",
    summary="Create or replace a Pokémon",
    responses={201: {"description": "Created a new Pokémon"}},
    dependencies=[Depends(check_api_key_value)]
)
async def put_pokemon(
    slug: SlugPath, 
    update: PokemonUpdate, 
    response: Response,
) -> Pokemon:
```

TODO: What the frick is `Depends`? Small note, thorough treatment in the next chapter.

Vi har introdusert en påkrevd miljøvariabel (`ADMIN_API_KEY`), så for å kjøre APIet ditt nå må du skrive:

```bash
ADMIN_API_KEY=superhemmeligverdi uv run fastapi dev
```

!!! tip "Bedre håndtering av miljøvariabler"
    I virkeligheten vil du nok unngå å kjøre APIet på denne måten. Du vil kanskje også ha bedre
    validering av at alle variabler er på plass og har riktig format. Da anbefaler jeg FastAPIs
    guide om [Settings](https://fastapi.tiangolo.com/advanced/settings/).

## Testing
For å gjøre kall i terminalen, må du nå legge ved headeren:

```bash
curl \
-H 'X-Api-Key: superhemmeligverdi' \
-H 'Content-Type: application/json' \
-X PUT http://localhost:8000/pokemon/pikachu \
-d '{"display_name": "Pikachu", "type1": "electric"}'
```

Prøv også hva som skjer hvis du sender feil API-nøkkel, eller utelater den helt.

Ta også en titt på dokumentasjonssiden. Det har kommet en ny knapp merket "Authorize", og endepunktene
som krever autentisering er nå merket med hengelås. 

## Oppgave

Implementer autentisering i ditt eget API. Hvis du vil kan du teste en av de andre autentiserings­metodene
som FastAPI tilbyr. Se hvordan disse oppfører seg i docs-UIet også.
