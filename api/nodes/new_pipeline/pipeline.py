"""
Orchestrates the 10-prompt pipeline according to the PRD v2 DAG.
"""
import io
import logging

from api.nodes.new_pipeline.web_fetch_node import WebFetchNode
from api.nodes.new_pipeline.local_fetch_node import LocalFetchNode
from api.nodes.new_pipeline.clean_node import CleanNode
from api.nodes.new_pipeline.mini_master_prompt_node import MiniMasterPromptNode
from api.nodes.new_pipeline.framework_select_node import FrameworkSelectNode
from api.nodes.new_pipeline.prompt_draft_node import PromptDraftNode
from api.nodes.new_pipeline.deduplicate_node import DeduplicateNode
from api.nodes.new_pipeline.business_anchor_guard import BusinessAnchorGuard
from api.nodes.new_pipeline.quota_enforce_node import QuotaEnforceNode
# from api.nodes.new_pipeline.explanation_node import ExplanationNode  # removed: tips no longer used
from api.nodes.pdf_builder_node import PdfBuilderNode
from api.nodes.assets_node import AssetsNode
from api.nodes.new_pipeline.save_artifact_node import SaveArtifactNode

# Pipeline logger
logger = logging.getLogger(__name__)

def Generate10Pipeline(url: str) -> bytes:
    """
    Full pipeline: fetch → clean → keyphrases → framework plan → draft → dedupe
    → anchor → quota enforce → explain → PDF build → save.
    Returns raw PDF bytes.
    """
    # Step 1: fetch
    # Step 1: fetch via OpenAI web tool, else fallback
    html = WebFetchNode(url)
    logger.info("Fetched HTML via web tool, length=%d", len(html))
    if not html or len(html) < 500:
        logger.info("WebFetchNode returned insufficient content, falling back to LocalFetchNode")
        html = LocalFetchNode(url)
        logger.info("Fetched HTML via local fetch, length=%d", len(html))
    # If still too short, abort with error for fallback flow
    if not html or len(html) < 500:
        raise ValueError("Fetched content too short (<500 characters); please provide raw text or a richer URL.")
    # Step 2: clean
    text = CleanNode(html)
    logger.info("CleanNode output text length=%d", len(text))
    # Step 3: generate business capsule
    capsule = MiniMasterPromptNode(html)
    logger.info("MiniMasterPromptNode capsule length=%d", len(capsule))
    # Step 4: framework plan (static quotas)
    plan = FrameworkSelectNode([])
    logger.info("FrameworkSelectNode plan: %r", plan)
    # Step 5: draft prompts based on capsule
    raw_prompts = PromptDraftNode(capsule, plan)
    logger.info("PromptDraftNode output: %r", raw_prompts)
    # Step 6: dedupe
    unique_prompts = DeduplicateNode(raw_prompts)
    logger.info("DeduplicateNode output: %r", unique_prompts)
    # Step 7: business anchor using capsule nouns
    anchored_prompts = BusinessAnchorGuard(unique_prompts, capsule)
    logger.info("BusinessAnchorGuard output: %r", anchored_prompts)
    # Step 8: enforce quota
    final_prompts = QuotaEnforceNode(anchored_prompts, plan)
    logger.info("QuotaEnforceNode output: %r", final_prompts)
    # Step 9: Extract assets for branding
    assets = AssetsNode(url)
    logo_url = assets.get('logo_url')
    palette = assets.get('palette', [])
    # Step 10: PDF build (no tips)
    logger.info("Generating PDF with logo_url=%s, palette=%r, categories=%s", logo_url, palette, list(final_prompts.keys()))
    pdf_bytes = PdfBuilderNode(logo_url, palette, final_prompts)
    # Step 12: save artifact (side-effect)
    SaveArtifactNode(pdf_bytes)
    return pdf_bytes