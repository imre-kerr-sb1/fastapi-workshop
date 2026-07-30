from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Pokemon(BaseModel):
    name: str
    type1: str
    type2: str | None = None

datastore: dict[str, Pokemon] = {
    "Pikachu": Pokemon(name="Pikachu", type1="Electric")
}

@app.get("/pokemon")
async def get_all_pokemon() -> list[Pokemon]:
    return list(datastore.values())
