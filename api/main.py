import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Configure API keys
import openai
openai.api_key = os.getenv('OPENAI_API_KEY')

# Import PocketFlow nodes
from api.nodes.fetch_summary_node import FetchSummaryNode
from api.nodes.summarise_node import SummariseNode
from api.nodes.assets_node import AssetsNode

app = FastAPI(title="Prompt Bootstrapper API")


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.post("/generate")
async def generate(request: Request):
    data = await request.json()
    url = data.get('url')
    if not url:
        raise HTTPException(status_code=400, detail="Missing 'url' in request body")
    try:
        # Step 1: fetch and summarise content
        raw_text = FetchSummaryNode(url)
        master_prompt = SummariseNode(raw_text)
        # Step 2: extract assets
        assets = AssetsNode(url)
        response = {
            "master_prompt": master_prompt,
            "logo_url": assets.get('logo_url'),
            "palette": assets.get('palette'),
        }
        return JSONResponse(content=response)
    except Exception as e:
        # Surface errors as HTTP 500
        raise HTTPException(status_code=500, detail=str(e))