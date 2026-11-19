# 5. Oppsummering

## Hva du bygde

APIet ditt fra forrige gang har fått tre nye ting:

- **Autentisering.** Endepunktene som endrer data krever nå en API-nøkkel.
- **En ekte database.** Dataene dine overlever en restart, og SQLen ligger i egne funksjoner som
    ikke vet noe om HTTP.
- **Automatiske tester** som får en egen, tom database hver, og som ikke trenger miljøvariabler
    for å kjøre.

Alle tre bygger på det samme: **Endepunktene sier hva de trenger, og FastAPI sørger for at de får
det.** `check_api_key_value`, `get_db` og `get_admin_api_key` er helt vanlige funksjoner. `Depends`
er det som gjør dem til avhengigheter, og `dependency_overrides` er det som lar testene bytte dem
ut.

## I virkeligheten

Vi har tatt noen snarveier for å rekke alt på tre timer. Skal du lage noe som skal i produksjon,
vil det nok se litt annerledes ut:

- **Postgres i stedet for SQLite.** SQLite er supert for å komme i gang og for små apper, men de
    fleste APIer med flere brukere snakker med en egen databaseserver.
- **Et bibliotek mellom deg og databasen.** De fleste FastAPI-prosjekter bruker
    [SQLAlchemy](https://www.sqlalchemy.org/) eller [SQLModel](https://sqlmodel.tiangolo.com/)
    (laget av samme person som FastAPI). Da får du en `Session` i stedet for en `Connection`, men
    mønsteret med `Depends` er akkurat det samme. Er du like glad i rå SQL som meg, går det helt
    fint an å bruke en driver som [psycopg](https://www.psycopg.org/) direkte.
- **Migrasjoner.** `CREATE TABLE IF NOT EXISTS` holder ikke så lenge. Se tipsboksen i
    [databasekapittelet](./03-persistence.md) for noen verktøy.
- **Tester mot en ekte Postgres.** Typisk kjører man opp Postgres i en container med
    [testcontainers](https://testcontainers.com/), og lar hver test kjøre i en transaksjon som
    rulles tilbake etterpå. Trikset er det samme som vårt: Overstyr `get_db`.
- **Ikke test mot SQLite hvis du kjører Postgres i produksjon.** SQL-dialektene er forskjellige
    nok til at testene kan bli grønne mens produksjon feiler.
- **Konfigurasjon med pydantic-settings** i stedet for `os.environ` spredt rundt i koden. Se
    FastAPIs guide om [Settings](https://fastapi.tiangolo.com/advanced/settings/).

## Neste gang

Det blir kanskje en episode 3. Har du ønsker om temaer, si ifra!
