import os, random
from pprint import pprint
import uvicorn, json
import schemas
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from a2a.utils import new_agent_text_message

app = FastAPI()

RAW_AGENT_CARD_DATA = {
  "name": "PingPongAgent",
  "description": "An agent that responds 'pong' to 'ping'.",
  "url": "http://localhost:4000",
  "provider": {
      "organization": "Telex Org.",
      "url": "https://telex.im"
    },
  "version": "1.0.0",
  "capabilities": {
    "streaming": False,
    "pushNotifications": False
  },
  "defaultInputModes": ["text/plain"],
  "defaultOutputModes": ["text/plain"],
  "skills": [
    {
      "id": "ping",
      "name": "Ping-Pong",
      "description": "Responds with 'pong' when given 'ping'.",
      "inputModes": ["text"],
      "outputModes": ["text"],
      "examples": [
        {
          "input": { "parts": [{ "text": "ping", "contentType": "text/plain" }] },
          "output": { "parts": [{ "text": "pong", "contentType": "text/plain" }] }
        }
      ]
    }
  ]
}


@app.get("/", response_class=HTMLResponse)
def read_root():
    return '<p style="font-size:30px">Ping Pong Agent</p>'


@app.get("/.well-known/agent.json")
def agent_card(request: Request):
    current_base_url = str(request.base_url).rstrip("/")

    response_agent_card = RAW_AGENT_CARD_DATA.copy()
    # new_name = f"{response_agent_card['name']}{random.randint(1, 1000)}"
    # print(new_name)
    # response_agent_card["name"] = new_name
    response_agent_card["url"] = current_base_url
    response_agent_card["provider"]["url"] = current_base_url

    return response_agent_card



@app.post("/")
async def handle_task(request: Request):
    body = await request.json()

    request_id = body.get("id")
    message = body["params"]["message"]["parts"][0].get("text", None)

    if message and message.lower() == "ping":
        text = "pong"

    else:
        text = "I only understand 'ping'"

    message = new_agent_text_message(text=text)


    response = {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": message.model_dump()
    }

    response = schemas.JSONRPCResponse.model_validate(response).model_dump()

    pprint(response)
    return response


if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=4000, reload=True)