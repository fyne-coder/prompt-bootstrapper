import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Configure API keys
import openai
openai.api_key = os.getenv('OPENAI_API_KEY')

import io

# Import PocketFlow nodes
from api.nodes.fetch_summary_node import FetchSummaryNode
from api.nodes.summarise_node import SummariseNode
from api.nodes.assets_node import AssetsNode
from api.nodes.prompts_node import PromptsNode
from api.nodes.rank_node import RankNode
from api.nodes.guide_node import GuideNode
from api.nodes.pdf_builder_node import PdfBuilderNode
from api.nodes.new_pipeline.pipeline import Generate10Pipeline

import logging
app = FastAPI(title="Prompt Bootstrapper API")
logger = logging.getLogger("api.main")


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
        # Pipeline: fetch, summarise, assets, prompts, ranking, tips, PDF
        raw_text = FetchSummaryNode(url)
        master_prompt = SummariseNode(raw_text)
        assets = AssetsNode(url)
        groups = PromptsNode(master_prompt, assets.get('palette', []))
        bests = RankNode(groups)
        tips = GuideNode(bests)
        pdf_bytes = PdfBuilderNode(
            assets.get('logo_url'),
            assets.get('palette', []),
            bests,
            tips,
        )
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=\"prompts.pdf\""},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/generate10")
async def generate10(request: Request):
    data = await request.json()
    url = data.get('url')
    if not url:
        raise HTTPException(status_code=400, detail="Missing 'url' in request body")
    try:
        pdf_bytes = Generate10Pipeline(url)
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=\"prompts10.pdf\""},
        )
    except NotImplementedError as e:
        logger.exception("10-prompt pipeline not yet implemented")
        raise HTTPException(status_code=501, detail=str(e))
    except Exception as e:
        logger.exception("Unhandled error in /generate10 endpoint")
        raise HTTPException(status_code=500, detail=str(e))