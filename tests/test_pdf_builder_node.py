import pytest

from api.nodes.pdf_builder_node import PdfBuilderNode

def test_pdf_without_logo():
    # Should produce a valid PDF even without logo or palette
    pdf = PdfBuilderNode(None, [], ["Prompt A", "Prompt B"], ["Tip A", "Tip B"])
    assert isinstance(pdf, (bytes, bytearray))
    # PDF files start with %PDF
    assert pdf[:4] == b"%PDF"

def test_pdf_with_logo(monkeypatch):
    # Monkey-patch httpx.get to return dummy PNG data
    import api.nodes.pdf_builder_node as pb

    class DummyResp:
        def __init__(self):
            # PNG header bytes + dummy content
            self.content = b"\x89PNG\r\n\x1a\nPNGDATA"
            self.headers = {'Content-Type': 'image/png'}
        def raise_for_status(self):
            pass

    monkeypatch.setattr(pb.httpx, 'get', lambda url, timeout: DummyResp())
    pdf = PdfBuilderNode("http://example.com/logo.png", ["#FF0000", "#00FF00"], ["P1"], ["T1"])
    assert isinstance(pdf, (bytes, bytearray))
    assert pdf[:4] == b"%PDF"