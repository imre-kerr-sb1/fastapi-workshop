# 3. Dependency injection
I forrige kapittel brukte vi `Depends` for å ta inn en API-nøkkel, og sjekke at denne hadde riktig
verdi før et endepunkt kunne bli kalt. Vi skal nå se nærmere på hvordan dette fungerer.

*Dependency injection* (og det relaterte konseptet *inversion of control*) er prinsippet i software-
utvikling om at kode ikke selv skal hente eller konstruere sine egne avhengigheter.  I stedet skal
den fortelle "noe" utenfor seg selv *hva slags* ting den trenger, og så skal dette "noe" sørge for
at den får det.

Dette kan høres veldig abstrakt og bakvendt ut, men du har faktisk drevet med en form av det hele
tiden mens du har jobbet med FastAPI. En funksjon som sier

```python
@app.get("/something")
def get_something(q: str) -> list[Something]:
    ...
```

forteller FastAPI (dette er den eksterne parten) at "jeg trenger en string som kommer fra query-
parameteret `q`". FastAPI får tak i denne fra requesten (eller håndterer det hvis den mangler), og
kaller funksjonen med stringen som parameter.

## Hvorfor?
Forhåpentligvis gir det mening at dependency injection på denne måten fører til kortfattet og lesbar
kode. Du kan outsource så mye som mulig til rammeverket ditt, som sørger for at alle avhengigheter
blir opprettet og injisert i riktig rekkefølge.

I tillegg hjelper dependency injection deg med å følge et viktig clean code-prinsipp:
*DRY (Don't repeat yourself)*. Hvis du definerer ett sted hvordan en avhengighet (token-validering,
databaseforbindelse, logging-system...) skal settes opp, er det også bare ett sted du trenger å
endre koden din hvis noen av disse tingene skulle endre seg i fremtiden.

Til slutt er dependency injection til stor hjelp når du skal skrive tester. Dette skal vi se mer på
i [kapittel 4](./04-testing.md).

## `Depends` — Dependency injection i FastAPI
FastAPI vet allerede hvordan den skal få tak i query-parametre, headere, `Request`-/`Response`-
objekter og andre HTTP-relaterte ting. Det `Depends` gjør er å fortelle FastAPI hvordan den også
kan få tak i andre typer avhengigheter.

La oss se på det enkleste mulige eksempelet (som riktignok ikke er særlig spennende):

```python
def my_dependency() -> int:
    return 42

@app.get("/my-endpoint")
def my_endpoint(dependency: Annotated[int, Depends(my_dependency)]) -> list[Something]:
    ...
```

Husk på at `Annotated` betyr "denne typen, med denne ekstra informasjonen". Så vi sier at `dependency`
skal være en verdi av type `int`, mens `Depends(my_dependency)` sier til FastAPI at den skal kalle
`my_dependency` for å få tak i verdien.

Argumentet til `Depends` må være noe som kan kalles. Ofte vil dette være en funksjon, men man kan også
gi den en klasse. FastAPI vil da kalle konstruktøren (`__init__`) til klassen.

### Avhengigheter med avhengigheter
I det forrige eksempelet var avhengigheten en funksjon som ikke tok inn noen argumenter. Hvis den
derimot skal ha argumenter, vil FastAPI også finne ut hvordan den skal skaffe disse. Dette følger
akkurat de samme reglene som argumenter til endepunktsfunksjoner, og slik kan man nøste seg innover
i avhengighetshierarkiet så langt man vil:

```python
def inner_dependency(
    n: int, m: int # Begge disse hentes fra query-parametre
) -> int:
    return n + m

def outer_dependency(dependency: Annotated[int, Depends(inner_dependency)]) -> int:
    return dependency + 1

@app.get("/my-endpoint")
def my_endpoint(dependency: Annotated[int, Depends(outer_dependency)]) -> list[Something]:
    ...
```

I koden over vil altså FastAPI først hente query-parametrene `n` og `m`, parse disse som `int`s, og
kalle `inner_dependency` med dem. Resultatet altså summen blir så sendt inn til `outer_dependency`,
og resultatet av det igjen er det som sendes inn til selve endepunktsfunksjonen.

### Avhengigheter uten returverdi
Noen ganger kan det være nyttig med en avhengighet som ikke returnerer noe, eller det kan være at
et endepunkt bare ikke bryr seg om returverdien. Dette så vi i forrige kapittel. `check_api_key_value`
var en funksjon som tok inn en API-nøkkel fra en header, og sjekket at denne stemte. Hvis den ikke
gjorde det kastet funksjonen en exception.

I slike tilfeller går det an å deklarere avhengigheten i dekoratoren, i stedet for i argumentene til
endepunktet:

```python hl_lines="5"
@app.put(
    "/pokemon/{slug}",
    summary="Create or replace a Pokémon",
    responses={201: {"description": "Created a new Pokémon"}},
    dependencies=[Depends(check_api_key_value)],
)
async def put_pokemon(
    slug: SlugPath, 
    update: PokemonUpdate, 
    response: Response,
) -> Pokemon:
```

Alternativet ser nokså grisete ut:

```python hl_lines="10"
@app.put(
    "/pokemon/{slug}",
    summary="Create or replace a Pokémon",
    responses={201: {"description": "Created a new Pokémon"}},
)
async def put_pokemon(
    slug: SlugPath, 
    update: PokemonUpdate, 
    response: Response,
    _unused: Annotated[None, Depends(check_api_key_value)],
) -> Pokemon:
```
