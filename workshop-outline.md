# Workshop Outline

Time: 3 hours, with breaks.


## Initial setup
1. Everyone creates a repo (https://github.com/new)
2. Open it in Coder
3. `uv init && uv add "fastapi[standard]"`

## Hello world
Write this into main.py:

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}
```

`uv run fastapi dev`, and let it rip.

Show how to call it (curl). Also take a look at the docs. 

## Main meat: A toy CRUD API for something or other (don't do pet store plz)
Ephemeral data store might be an issue given hot-reload? Test.
