import os
import uuid
from api.nodes.fetch_summary_node import Node

@Node(retries=1)
def SaveArtifactNode(pdf_bytes: bytes, exports_dir: str = "exports") -> str:
    """
    Save PDF bytes to local exports directory with a unique job ID.
    Returns the file path.
    """
    raise NotImplementedError("SaveArtifactNode is not implemented")