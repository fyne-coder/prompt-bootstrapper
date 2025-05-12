import os

from dotenv import load_dotenv
load_dotenv()
from api.nodes.new_pipeline.save_artifact_node import SaveArtifactNode
path = SaveArtifactNode(b"%PDF-fake", exports_dir="test_exports")
print("Saved to", path)
print("Exists?", os.path.isfile(path))
