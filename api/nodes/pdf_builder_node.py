import functools
import io
import base64
from typing import List, Optional

# Core imports
import httpx
import logging

# Monkey-patch PyDyf PDF constructor to accept version and identifier args and set version attribute
try:
    import pydyf
    _orig_pdf_init = pydyf.PDF.__init__
    def _patched_pdf_init(self, version=b'1.7', identifier=None, *args, **kwargs):
        # Store PDF version for compatibility
        try:
            self.version = version if isinstance(version, (bytes, bytearray)) else str(version).encode()
        except Exception:
            self.version = b'1.7'
        # Call original initializer
        _orig_pdf_init(self)
    pydyf.PDF.__init__ = _patched_pdf_init
    logging.getLogger(__name__).info("Patched pydyf.PDF.__init__ to accept version and identifier args")
except ImportError:
    logging.getLogger(__name__).warning("pydyf not installed; cannot patch PDF constructor")
except Exception as e:
    logging.getLogger(__name__).error(f"Error patching pydyf.PDF.__init__: {e}")

from weasyprint import HTML
# Node decorator with retry logic
class Node:
    def __init__(self, retries: int = 0):
        self.retries = retries

    def __call__(self, fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            last_exc = None
            for _ in range(self.retries):
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    last_exc = e
            if last_exc is not None:
                raise last_exc
            return fn(*args, **kwargs)

        wrapper.__wrapped__ = fn
        return wrapper

@Node(retries=0)
def PdfBuilderNode(
    logo_url: Optional[str],
    palette: List[str],
    prompts_by_cat: dict[str, list[str]]
) -> bytes:
    """
    Build a branded PDF containing prompts and usage tips.
    Embeds logo if available and applies color palette to headings.
    Returns raw PDF bytes.
    """
    # Fetch and embed logo as data URI
    img_data = None
    if logo_url:
        try:
            resp = httpx.get(logo_url, timeout=10.0)
            resp.raise_for_status()
            ct = resp.headers.get("Content-Type", "image/png")
            b64 = base64.b64encode(resp.content).decode()
            img_data = f"data:{ct};base64,{b64}"
        except Exception:
            img_data = None

    # Determine primary and accent colors
    primary = palette[0] if len(palette) > 0 else "#000000"
    accent = palette[1] if len(palette) > 1 else primary

    # Build HTML content with grouped prompts
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset=\"utf-8\"> 
<title>AI Prompt Pack</title>
<style>
  body {{ font-family: Arial, sans-serif; margin: 2em; }}
  .header {{ display: flex; align-items: center; border-bottom: 2px solid {primary}; padding-bottom: 1em; margin-bottom: 2em; }}
  .header img {{ max-height: 50px; margin-right: 1em; }}
  .header h1 {{ color: {primary}; margin: 0; }}
  ol {{ padding-left: 1em; }}
  li {{ margin-bottom: 1.5em; }}
  .prompt {{ font-size: 1.1em; color: #333; }}
  .tip {{ font-size: 0.9em; color: {accent}; margin-top: 0.5em; }}
</style>
</head>
<body>
<div class=\"header\">"""
    if img_data:
        html += f"<img src=\"{img_data}\" alt=\"logo\"/>"
    html += f"<h1>AI Prompt Pack</h1></div>"  # header end
    # Render grouped prompts by category
    for category, items in prompts_by_cat.items():
        html += f"<section><h2>{category}</h2><ol>"
        for prmpt in items:
            safe_prompt = prmpt.replace('<', '&lt;').replace('>', '&gt;')
            html += f"<li class=\"prompt\">{safe_prompt}</li>"
        html += "</ol></section>"
    html += "</body></html>"

    # Generate PDF, with detailed logging on failure
    try:
        # Log WeasyPrint/PyDyf versions for debugging
        try:
            import pkg_resources
            wp_ver = pkg_resources.get_distribution('weasyprint').version
            pd_ver = pkg_resources.get_distribution('pydyf').version
            logging.getLogger(__name__).info(
                f"PdfBuilderNode using WeasyPrint {wp_ver}, PyDyf {pd_ver}")
        except Exception:
            pass
        pdf_bytes = HTML(string=html).write_pdf()
        return pdf_bytes
    except Exception as e:
        logger = logging.getLogger(__name__)
        # Log context: counts and html size
        logger.error(
            f"PdfBuilderNode error: logo_url={logo_url}, "
            f"palette={palette}, prompts={len(prompts)}, tips={len(tips)}, html_length={len(html)}"
        )
        logger.exception("Exception stack trace:")
        # Re-raise to be caught by FastAPI and returned as HTTP 500
        raise