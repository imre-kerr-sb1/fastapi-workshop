"""Presenter's file: the other design, for the optional live demo in section 5.

Only open this if someone asks "but what if the client can't pick the identifier?" --
which is the right question, and has a real answer. Some domains genuinely can't:

- incidents, log entries, orders: no natural name, and two can be identical
- anything where the client shouldn't get to choose (guessable URLs, tenant leakage)

When the *server* owns the identifier, PUT-as-upsert stops working: the client can't
name a URL it doesn't know yet. That's precisely when POST earns its place, and it comes
with a Location header, because the response is the client's only chance to learn where
the thing landed.

Run it beside main.py:
    uv run fastapi dev main_autoid.py --port 8001

Demo script:
    curl -i -X POST localhost:8001/incidents -H 'content-type: application/json' \
      -d '{"title": "Database down", "severity": "high"}'
    # -> 201, and a Location header. Run it again: a second incident, different id.
    #    Compare with PUT in main.py, where running it twice changes nothing.
"""

import uuid
from enum import StrEnum

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, Field

app = FastAPI(
    title="Incidents (server-generated IDs)",
    summary="The design where POST is right: the server owns the identifier.",
)


class Severity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class IncidentCreate(BaseModel):
    """What the client sends. No id -- it isn't theirs to choose."""

    title: str = Field(
        min_length=1,
        max_length=200,
        description="Free text. Two incidents may legitimately share a title.",
        examples=["Database down"],
    )
    severity: Severity


class Incident(BaseModel):
    """What we store and return: the client's data plus the id we assigned."""

    id: uuid.UUID = Field(description="Assigned by the server. Clients cannot choose it.")
    title: str
    severity: Severity


datastore: dict[uuid.UUID, Incident] = {}


@app.get("/incidents", summary="List all incidents")
async def list_incidents() -> list[Incident]:
    return list(datastore.values())


@app.get(
    "/incidents/{incident_id}",
    summary="Fetch one incident",
    responses={404: {"description": "No such incident"}},
)
async def get_incident(incident_id: uuid.UUID) -> Incident:
    if incident_id not in datastore:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No incident {incident_id}")
    return datastore[incident_id]


@app.post(
    "/incidents",
    status_code=status.HTTP_201_CREATED,
    summary="File a new incident",
)
async def create_incident(to_create: IncidentCreate, response: Response) -> Incident:
    """The case POST is actually for: the client can't know the URL in advance.

    Not idempotent, and honestly so. Two identical POSTs mean two incidents, because
    "the database went down again" is a real thing that happens. Compare PUT in
    main.py, where two identical requests are indistinguishable from one.
    """
    incident = Incident(
        id=uuid.uuid4(), title=to_create.title, severity=to_create.severity
    )
    datastore[incident.id] = incident
    # The Location header now carries information the client had no way to compute --
    # this is the header doing its actual job, unlike on an upsert PUT.
    response.headers["Location"] = f"/incidents/{incident.id}"
    return incident


@app.put(
    "/incidents/{incident_id}",
    summary="Replace an existing incident",
    responses={404: {"description": "No such incident"}},
)
async def replace_incident(
    incident_id: uuid.UUID, update: IncidentCreate
) -> Incident:
    """PUT is still here, but it only replaces -- it cannot create.

    Worth saying out loud during the demo: this is the one arrangement where "POST
    creates, PUT updates" is genuinely true. It's true because the server owns the
    identifier, not because it's a rule about the verbs.
    """
    if incident_id not in datastore:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No incident {incident_id}")
    updated = Incident(
        id=incident_id, title=update.title, severity=update.severity
    )
    datastore[incident_id] = updated
    return updated


@app.delete(
    "/incidents/{incident_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an incident",
    responses={404: {"description": "No such incident"}},
)
async def delete_incident(incident_id: uuid.UUID) -> None:
    if incident_id not in datastore:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No incident {incident_id}")
    del datastore[incident_id]
