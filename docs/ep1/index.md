# Bygg et CRUD-API med FastAPI

I denne workshopen kommer du til å lage et HTTP-API: Noe et annet program kan gjøre et
nettverkskall til for å lese og skrive informasjon til et datalager. Det kommer til å ha
interaktiv dokumentasjon som forklarer forventet dataformat og validerering av innkommende
data, uten at du trenger å gjøre annet enn å skrive python-funksjoner (med typeannotasjoner).

Beregnet tid er ca. tre timer.

## Nødvendige forkunnskaper

Du er kjent med python, men har ikke nødvendigvis skrevet et API før. Hvis du kan funksjoner,
dicts, lister og helt grunnleggende klasser har du det som trengs av forkunnskaper. Vi kommer 
til å se en del konsepter du kanskje ikke har sett før, som dekoratorer, typeannotasjoner og 
`Annotated`. Alle disse blir forklart etter hvert som de dukker opp.

Ingen forkunnskaper om HTTP eller APIer kreves. Metoder, statuskoder, headers, CRUD, REST...
Alle disse er innhold, ikke forkunnskaper.

## Hvordan bruke workshopen

Hvert steg har klare instruksjoner som gradvis bygger opp APIet vårt. Du kommer i tillegg til å
se noen sånne her:

!!! question "Observer → hvorfor?"
    Brekk noe med vilje, se hva som skjer, og prøv å tenke ut hvorfor. Mye av den dypere læringen
    kommer til å skje her. Alle kan kopiere kode og gjøre små endringer på den. Ved å bevege deg
    utenfor den oppmerkede stien får du innsikt i hva som egentlig skjer.

    Hvis du sitter fast kommer svaret til å være ett klikk unna. Men prøv å gjette først.

    ??? success "Svaret"
        **42**

        ...Var jeg morsom nå?

To ting å merke seg før vi starter:

- **Du velger domene.** I [steg 4](04-model-and-get.md) velger du hva APIet ditt handler om.
    Eksemplene bruker Pokémon, og det gjør også [løsningsforslaget](solution-key.md).
- **Skriv koden selv, med dine egne fingre.** Ikke kopier og lim, og ikke la Copilot skrive for
    deg (skru den av om du må). Det er treigere og krever mer av hjernen, og det igjen gjør at 
    informasjonen fester seg. Aller helst skulle vi koblet tegnebrett til VS Code så vi kunne
    skrevet for hånd...

## Stegene

<div class="grid cards" markdown>

- **[1. Hva er i det hele tatt et API?](01-what-is-an-api.md)**

    Ingen koding her. Intro til HTTP, hva CRUD er, og hva et rammeverk gjør for deg.

- **[2. Prosjektoppsett](02-setup.md)**

    Vi lager et Python-prosjekt med `uv`, og installerer FastAPI.

- **[3. Hello world](03-hello-world.md)**

    Se hvor mye du får med fire linjer kode.

- **[4. Datamodell og GET-request](04-model-and-get.md)**

    Velg et domene. Beskriv det som en klasse. Server det i en JSON-liste.

- **[5. Identifikatorer og stier](05-identifiers.md)**

    Dette blir en diskusjon om API-design. Ingen koding, men du må gjøre et valg om 
    hva som passer best for ditt API.

- **[6. Meldingsinnhold og validering](06-request-bodies.md)**

    Hvordan ta i mot data, og sørge for at koden din aldri ser ugyldige data.

- **[7. Statuskoder](07-status-codes.md)**

    HTTPs eget vokabular for "Nei! Feil!", "Oops!", "Alt i orden" og mye mer.

- **[8. Oppsummering og neste steg](08-wrap-up.md)**

    Hva har du bygd, og to ting du bør se på som neste steg.
    (Neste workshop vil ta for seg disse.)

</div>
