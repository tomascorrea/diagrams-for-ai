import os
import tempfile

import pytest
from PIL import Image

from diagrams_for_ai import Cluster, Diagram, Edge, LineStyle, Node


@pytest.fixture
def output_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


def test_generates_svg_file(output_dir):
    filepath = os.path.join(output_dir, "test_diagram")
    with Diagram("Test", filename=filepath, rows=3, cols=3, outformat="svg", show=False):
        n1 = Node("A", icon="aws/compute/ec2", row=0, col=0)
        n2 = Node("B", icon="aws/compute/ec2", row=1, col=1)
        n1 >> n2

    svg_path = filepath + ".svg"
    assert os.path.isfile(svg_path)
    with open(svg_path) as f:
        content = f.read()
    assert "<svg" in content
    assert "data:image/png;base64," in content


def test_svg_contains_cluster(output_dir):
    filepath = os.path.join(output_dir, "cluster_test")
    with Diagram("Cluster Test", filename=filepath, rows=3, cols=3, outformat="svg", show=False):
        with Cluster("Group", row=0, col=0, width=2, height=2):
            Node("Inside", icon="aws/compute/ec2", row=0, col=0)

    with open(filepath + ".svg") as f:
        content = f.read()
    assert "Group" in content


def test_generates_png_file(output_dir):
    filepath = os.path.join(output_dir, "test_diagram")
    with Diagram("Test", filename=filepath, rows=3, cols=3, outformat="png", show=False):
        n1 = Node("A", icon="aws/compute/ec2", row=0, col=0)
        n2 = Node("B", icon="aws/database/rds", row=2, col=2)
        n1 >> n2

    png_path = filepath + ".png"
    assert os.path.isfile(png_path)
    img = Image.open(png_path)
    assert img.size[0] > 0
    assert img.size[1] > 0


def test_generates_both_svg_and_png(output_dir):
    filepath = os.path.join(output_dir, "multi_format")
    with Diagram("Multi", filename=filepath, rows=2, cols=2, outformat=["svg", "png"], show=False):
        Node("X", icon="aws/compute/ec2", row=0, col=0)

    assert os.path.isfile(filepath + ".svg")
    assert os.path.isfile(filepath + ".png")


def test_all_line_styles_render(output_dir):
    filepath = os.path.join(output_dir, "edges")
    with Diagram("Edges", filename=filepath, rows=3, cols=4, outformat="svg", show=False):
        a = Node("A", icon="aws/compute/ec2", row=0, col=0)
        b = Node("B", icon="aws/compute/ec2", row=0, col=2)
        c = Node("C", icon="aws/compute/ec2", row=2, col=0)
        e = Node("E", icon="aws/compute/ec2", row=2, col=2)

        a >> b
        a >> Edge(line_style=LineStyle.STRAIGHT) >> c
        b >> Edge(line_style=LineStyle.ORTHO) >> e
        c >> Edge(line_style=LineStyle.STEP) >> e

    assert os.path.isfile(filepath + ".svg")
    with open(filepath + ".svg") as f:
        content = f.read()
    assert content.count("<path") >= 4
