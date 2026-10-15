# 1. Middleware

Motiverende eksempel: CORS

Duplisere masse kode, og måtte ta inn Response-objektet i alle funksjoner?
Lage egne decorators som modifiserer endepunktsfunksjonene?

Nei! Middlewares!

## Intro
Middlewares er funksjoner som pakker inn endepunktene dine, og kjører både før og etter
selve endepunktsfunksjonen. Treffer **alle** endepunkter i APIet.

Middlewares som legges til applikasjonen havner "innerst" i denne stacken, og bygges så
lag på lag utover.

TODO bilde 

## Hvordan skriver man en middleware?

```python
from fastapi import Request, Response
from typing import Awaitable, Callable

async def my_middleware(request: Request, call_next: Callable[[Request], Awaitable[Response]]): 

    # ...Kode som skjer *før* endepunktsfunksjonen...

    response = await call_next(request)

    # ...Kode som skjer *etter* endepunktsfunksjonen

    return response
```

Hvorfor dette `call_next`-parametret, og hva er den typesignaturen?

Middleware-funksjonen skal ikke trenge å tenke på hvor den befinner seg i middleware-stacken. Alt den bryr
seg om er hva som skjer før og etter neste lag innover. `call_next` er da en funksjon som sender kontrollen
videre innover i stacken. Typesignaturen kan leses som "async-funksjon som tar ett argument av type `Request`
og returnerer en `Response`".

## `request.state`
Som beskrevet over, er middlewares usynlige for hverandre, og for endepunktsfunksjonene. Men hva om du
trenger å la dem snakke sammen? Det finnes en måte å smugle data innover i stacken, ved å bruke `state`-feltet
på request-objektet. `state` er en dict som i utgangspunktet er tom, og hvor du kan lagre hva som helst. Typisk
vil dette være berikende kontekst om forespørselen, for eksempel en autogenerert ID som kan brukes for logging
og tracing.

Dette er kraftig og nyttig, og også lett å misbruke. Prøv å holde deg til "rene" middlewares så godt det lar
seg gjøre.

## Oppgaver

1. Legg til CORS-støtte i APIet ditt.
2. Logg alle kallene som treffer APIet. (FastAPI gjør dette allerede, men hey det er en oppgave)
3. Samle metrikker per endepunkt, om antall kall og total/gjennomsnittlig prosesseringstid. Server dette på et eget endepunkt (Prometheus-format hvis du vil være fancy.)
