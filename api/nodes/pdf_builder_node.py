import functools
import io
import base64
import logging
from typing import List, Optional

import httpx
from weasyprint import HTML

# Monkey-patch PyDyf PDF constructor to accept version and identifier args
try:
    import pydyf

    _orig_pdf_init = pydyf.PDF.__init__

    def _patched_pdf_init(self, version: bytes = b"1.7", identifier=None, *args, **kwargs):
        try:
            self.version = (
                version
                if isinstance(version, (bytes, bytearray))
                else str(version).encode()
            )
        except Exception:
            self.version = b"1.7"
        _orig_pdf_init(self)

    pydyf.PDF.__init__ = _patched_pdf_init
    logging.getLogger(__name__).info(
        "Patched pydyf.PDF.__init__ to accept version and identifier args"
    )
except ImportError:
    logging.getLogger(__name__).warning(
        "pydyf not installed; cannot patch PDF constructor"
    )
except Exception as e:
    logging.getLogger(__name__).error(f"Error patching pydyf.PDF.__init__: {e}")


# Node decorator with retry logic
class Node:
    def __init__(self, retries: int = 0):
        self.retries = retries

    def __call__(self, fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            last_exc = None
            for _ in range(self.retries + 1):
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    last_exc = e
            raise last_exc

        wrapper.__wrapped__ = fn
        return wrapper


@Node(retries=0)
def PdfBuilderNode(
    logo_url: Optional[str],
    palette: List[str],
    prompts_by_cat: dict[str, list[str]],
) -> bytes:
    """
    Build a branded PDF containing AI shortcuts (prompts).
    Embeds logo if available, applies brand colors, and adds footer.
    Returns raw PDF bytes.
    """
    logger = logging.getLogger(__name__)

    # Fetch and embed logo as data URI
    img_data = None
    if logo_url:
        try:
            resp = httpx.get(logo_url, timeout=10.0)
            resp.raise_for_status()
            content_type = resp.headers.get("Content-Type", "image/png")
            b64 = base64.b64encode(resp.content).decode()
            img_data = f"data:{content_type};base64,{b64}"
        except Exception:
            img_data = None

    # Determine colors
    primary = palette[0] if palette else "#1c1c1c"
    accent = palette[1] if len(palette) > 1 else primary

    # Build HTML
    html_parts = [
        "<!DOCTYPE html>",
        "<html><head><meta charset='utf-8'>",
        "<title>AI Shortcuts Kit</title>",
        "<style>",
        "  body { font-family: Arial, sans-serif; font-size: 16px; line-height: 1.5; color: #1c1c1c; margin: 2em; }",
        f"  .header {{ display: flex; align-items: center; border-bottom: 2px solid {primary}; padding-bottom: 1em; margin-bottom: 2em; }}",
        "  .header img { max-height: 50px; margin-right: 1em; }",
        f"  .header h1 {{ color: {primary}; margin: 0; font-size: 1.75rem; }}",
        "  section h2 { font-size: 1.25rem; margin-top: 1.5em; color: #333; }",
        "  ol { padding-left: 1.25em; }",
        "  li.prompt { margin-bottom: 1.5em; }",
        "  .prompt { white-space: pre-wrap; font-size: 1rem; color: #333; }",
        f"  footer {{ margin-top: 3em; border-top: 1px solid {accent}; padding-top: 1em; font-size: 0.875rem; color: #555; text-align: center; }}",
        "  footer a { color: inherit; text-decoration: none; }",
        "</style></head><body>",
    ]

    # Header
    header = "<div class='header'>"
    if img_data:
        header += f"<img src='{img_data}' alt='Fyne LLC logo'/>"
    header += "<h1>AI Shortcuts Kit</h1></div>"
    html_parts.append(header)

    # Prompts by category
    for category, prompts in prompts_by_cat.items():
        html_parts.append(f"<section><h2>{category}</h2><ol>")
        for prompt in prompts:
            escaped = (
                prompt.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )
            html_parts.append(f"<li class='prompt'>{escaped}</li>")
        html_parts.append("</ol></section>")

    # Footer
    html_parts.append(
        "<footer>"
        "© 2025 FYNE LLC. "
        "<a href='https://bizassistant.fyne-llc.com' target='_blank'>bizassistant.fyne-llc.com</a>"
        "</footer>"
    )

    html_parts.append("</body></html>")
    html_content = "\n".join(html_parts)

    # Generate PDF
    try:
        pdf_bytes = HTML(string=html_content).write_pdf()
        logger.info("PdfBuilderNode generated PDF, size=%d bytes", len(pdf_bytes))
        return pdf_bytes
    except Exception as e:
        logger.error(
            "PdfBuilderNode error: logo_url=%s, palette=%s, categories=%d, html_length=%d",
            logo_url,
            palette,
            len(prompts_by_cat),
            len(html_content),
        )
        logger.exception("Exception during PDF generation")
        raise