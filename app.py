from pydantic import BaseModel
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chat.openai.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_TODOS = {}


@app.get("/")
async def hello_world():
    return {"Hello": "world"}


class Todo(BaseModel):
    todo: str | None = None
    idx: int | None = None


@app.post("/todos/{username}", status_code=200)
def add_todo(username: str, todo: Todo | None = None):
    if username not in _TODOS:
        _TODOS[username] = []
    _TODOS[username].append(todo.todo)
    return {"todo": todo.todo, "user": username}


@app.get("/todos/{username}", status_code=200)
async def get_todos(username):
    return {username: _TODOS.get(username, [])}


@app.delete("/todos/{username}", status_code=200)
async def delete_todo(username, todo: Todo | None = None):
    if todo and todo.idx is not None:
        if 0 <= todo.idx < len(_TODOS[username]):
            popped = _TODOS[username].pop(todo.idx)
            return {"deleted": popped}


@app.get("/logo.png", response_class=FileResponse)
async def plugin_logo():
    filename = "logo.png"
    return FileResponse(filename, media_type="image/png")


@app.get("/.well-known/ai-plugin.json", response_class=Response, status_code=200)
async def plugin_manifest():
    # host = request.client.host
    with open("ai-plugin.json") as f:
        response = f.read()
    return Response(content=response, media_type="text/json")


@app.get("/openapi.yaml", response_class=Response, status_code=200)
async def openapi_spec(request: Request):
    host = request.client.host
    scheme = request.url.scheme
    port = request.url.port
    print(host)
    with open("openapi.yaml") as f:
        text = f.read()
        # This is a trick we do to populate the PLUGIN_HOSTNAME constant in the OpenAPI spec
        text = text.replace("PLUGIN_HOSTNAME", f"{scheme}://{host}:{port}")
    return Response(content=text, media_type="text/yaml")
