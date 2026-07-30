# Loose tasks
Tasks (or just infodumps) that have not yet been placed in the outline.

## Dev vs prod mode differences
Docs give two main differences:
- dev mode has live reloading
- dev mode only listens on localhost

## HTTP Status codes
These map well to the CRUD API project.

### Easy case: success
```python
@app.post("/path", status_code=201)
# or
from fastapi import status
@app.post("/path", status_code=status.HTTP_201_CREATED)
```

### Medium case: errors
Just use `HTTPException`.

### Hard case: dynamically change based on code
Requires a `Response` argument to the function.

The docs has a "get or create" example for this. "create or update" should also work fine for a PUT endpoint.
