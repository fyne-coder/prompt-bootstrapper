import os

import pytest

from api.nodes.new_pipeline.save_artifact_node import SaveArtifactNode

def test_save_artifact_node_creates_file(tmp_path):
    # Prepare dummy PDF bytes
    pdf_data = b"%PDF-1.4 test"
    exports_dir = tmp_path / "exports"
    # Call SaveArtifactNode
    filepath = SaveArtifactNode(pdf_data, exports_dir=str(exports_dir))
    # Check returned path
    assert os.path.isfile(filepath)
    assert filepath.startswith(str(exports_dir))
    assert filepath.endswith('.pdf')
    # Check file contents
    with open(filepath, 'rb') as f:
        content = f.read()
    assert content == pdf_data

def test_save_artifact_node_multiple(tmp_path):
    pdf_data1 = b"%PDF-1.4 one"
    pdf_data2 = b"%PDF-1.4 two"
    exports_dir = tmp_path / "exports"
    path1 = SaveArtifactNode(pdf_data1, exports_dir=str(exports_dir))
    path2 = SaveArtifactNode(pdf_data2, exports_dir=str(exports_dir))
    # Ensure two distinct files
    assert path1 != path2
    assert os.path.exists(path1)
    assert os.path.exists(path2)