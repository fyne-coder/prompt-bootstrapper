import os
import uuid
from api.nodes.fetch_summary_node import Node

@Node(retries=1)
def SaveArtifactNode(pdf_bytes: bytes, exports_dir: str = "exports") -> str:
    """
    Save PDF bytes to local exports directory with a unique job ID.
    Returns the file path.
    """
    # Ensure exports directory exists
    os.makedirs(exports_dir, exist_ok=True)
    # Generate a unique job ID
    job_id = uuid.uuid4().hex
    filename = f"{job_id}.pdf"
    filepath = os.path.join(exports_dir, filename)
    # Write PDF bytes to file
    with open(filepath, 'wb') as f:
        f.write(pdf_bytes)
    return filepath