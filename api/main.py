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
from api.nodes.page_llm_profile_node import PageLLMProfileNode
from api.nodes.new_pipeline.pipeline import Generate10Pipeline
from api.nodes.new_pipeline.web_fetch_node import WebFetchNode
from api.nodes.new_pipeline.local_fetch_node import LocalFetchNode
from api.nodes.new_pipeline.clean_node import CleanNode
from api.nodes.new_pipeline.keyphrase_node import KeyphraseNode
from api.nodes.new_pipeline.framework_select_node import FrameworkSelectNode
from api.nodes.new_pipeline.prompt_draft_node import PromptDraftNode
from api.nodes.new_pipeline.deduplicate_node import DeduplicateNode
from api.nodes.new_pipeline.business_anchor_guard import BusinessAnchorGuard
from api.nodes.new_pipeline.quota_enforce_node import QuotaEnforceNode
# ExplanationNode and tips removed
from api.nodes.assets_node import AssetsNode

import logging
logging.basicConfig(level=logging.INFO)
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title="Prompt Bootstrapper API")
# Enable CORS so the static front-end can call API from a different origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
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
        # Pipeline: one-shot profile, prompts, ranking, tips, assets, PDF
        profile = PageLLMProfileNode(url)
        framework_plan = {
            "key_phrases": profile["keywords"],
            "sector":       profile["sector"],
            "services":     profile["services"],
            "geo":          profile["geo"],
            "brand_tone":   profile["brand_tone"],
        }
        prompts = PromptDraftNode(
            text=" ".join(profile["value_props"]),
            framework_plan=framework_plan,
        )
        bests = RankNode(prompts)
        tips = GuideNode(bests)
        # branding assets
        assets = AssetsNode(url)
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
    except ValueError as e:
        # Fallback validation errors
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.exception("Unhandled error in /generate10 endpoint")
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/generate10/json")
async def generate10_json(request: Request):
    data = await request.json()
    url = data.get('url')
    raw_text = data.get('text')
    if not url and not raw_text:
        raise HTTPException(status_code=400, detail="Missing 'url' or 'text' in request body")
    try:
        # Determine input text: either user-supplied or fetched+cleaned
        # Determine input text: from user or fetched+cleaned
        if raw_text:
            text = raw_text
        else:
            # Step 1: fetch raw HTML and fallback
            html = WebFetchNode(url)
            if not html or len(html) < 500:
                html = LocalFetchNode(url)
            # Validate content length after fallback
            if not html or len(html) < 500:
                raise ValueError("Fetched content too short (<500 characters); please provide raw text or a richer URL.")
            # Step 2: clean text
            text = CleanNode(html)
        # Step 3: extract keyphrases
        keyphrases = KeyphraseNode(text)
        # Step 4: framework plan
        plan = FrameworkSelectNode(keyphrases)
        # Step 5: draft prompts
        raw_prompts = PromptDraftNode(text, plan)
        # Step 6: dedupe
        unique_prompts = DeduplicateNode(raw_prompts)
        # Step 7: anchor
        anchored = BusinessAnchorGuard(unique_prompts, keyphrases)
        # Step 8: enforce quota
        final_prompts = QuotaEnforceNode(anchored, plan)
        # Step 9: skip explanations (tips removed)
        # Step 10: assets for branding
        assets = AssetsNode(url)
        return JSONResponse(content={
            "prompts": final_prompts,
            "logo_url": assets.get('logo_url'),
            "palette": assets.get('palette', [])
        })
    except Exception as e:
        logger.exception("Error in /generate10/json endpoint")
        # Distinguish client vs server
        status = 422 if isinstance(e, ValueError) else 500
        raise HTTPException(status_code=status, detail=str(e))

@app.post("/generate10/pdf")
async def generate10_pdf(request: Request):
    data = await request.json()
    prompts_by_cat = data.get("prompts")
    logo_url = data.get("logo_url")
    palette = data.get("palette", [])
    if not isinstance(prompts_by_cat, dict):
        raise HTTPException(status_code=400, detail="Invalid prompts payload; expected object mapping categories to arrays")
    try:
        pdf_bytes = PdfBuilderNode(logo_url, palette, prompts_by_cat)
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=\"prompts10.pdf\""},
        )
    except Exception as e:
        logger.exception("Error in /generate10/pdf endpoint")
        raise HTTPException(status_code=500, detail=str(e))