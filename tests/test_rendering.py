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


def test_png_scale_doubles_dimensions(output_dir):
    filepath_1x = os.path.join(output_dir, "scale1")
    with Diagram("S1", filename=filepath_1x, rows=2, cols=2, outformat="png", show=False):
        Node("A", icon="aws/compute/ec2", row=0, col=0)

    filepath_2x = os.path.join(output_dir, "scale2")
    with Diagram("S2", filename=filepath_2x, rows=2, cols=2, scale=2, outformat="png", show=False):
        Node("A", icon="aws/compute/ec2", row=0, col=0)

    img_1x = Image.open(filepath_1x + ".png")
    img_2x = Image.open(filepath_2x + ".png")
    assert img_2x.size[0] == img_1x.size[0] * 2
    assert img_2x.size[1] == img_1x.size[1] * 2


def test_svg_scale_doubles_viewbox(output_dir):
    filepath_1x = os.path.join(output_dir, "svgscale1")
    with Diagram("S1", filename=filepath_1x, rows=2, cols=2, outformat="svg", show=False):
        Node("A", icon="aws/compute/ec2", row=0, col=0)

    filepath_2x = os.path.join(output_dir, "svgscale2")
    with Diagram("S2", filename=filepath_2x, rows=2, cols=2, scale=2, outformat="svg", show=False):
        Node("A", icon="aws/compute/ec2", row=0, col=0)

    with open(filepath_1x + ".svg") as f:
        svg_1x = f.read()
    with open(filepath_2x + ".svg") as f:
        svg_2x = f.read()

    import re
    vb_1x = re.search(r'viewBox="0 0 (\d+) (\d+)"', svg_1x)
    vb_2x = re.search(r'viewBox="0 0 (\d+) (\d+)"', svg_2x)
    assert vb_1x and vb_2x
    assert int(vb_2x.group(1)) == int(vb_1x.group(1)) * 2
    assert int(vb_2x.group(2)) == int(vb_1x.group(2)) * 2


def test_png_custom_icon_size(output_dir):
    filepath = os.path.join(output_dir, "icon_size")
    with Diagram("Icon", filename=filepath, rows=2, cols=2, icon_size=80, outformat="png", show=False):
        Node("A", icon="aws/compute/ec2", row=0, col=0)

    assert os.path.isfile(filepath + ".png")
    img = Image.open(filepath + ".png")
    assert img.size[0] > 0


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


def test_edge_via_renders_svg(output_dir):
    filepath = os.path.join(output_dir, "via_svg")
    with Diagram("Via", filename=filepath, rows=3, cols=3, outformat="svg", show=False):
        a = Node("A", icon="aws/compute/ec2", row=0, col=0)
        b = Node("B", icon="aws/compute/ec2", row=2, col=2)
        a >> Edge(via=[(0, 2), (2, 2)]) >> b

    svg_path = filepath + ".svg"
    assert os.path.isfile(svg_path)
    with open(svg_path) as f:
        content = f.read()
    assert "<path" in content


def test_edge_via_renders_png(output_dir):
    filepath = os.path.join(output_dir, "via_png")
    with Diagram("Via", filename=filepath, rows=3, cols=3, outformat="png", show=False):
        a = Node("A", icon="aws/compute/ec2", row=0, col=0)
        b = Node("B", icon="aws/compute/ec2", row=2, col=2)
        a >> Edge(via=[(0, 2)]) >> b

    png_path = filepath + ".png"
    assert os.path.isfile(png_path)
    img = Image.open(png_path)
    assert img.size[0] > 0


def test_edge_via_multiple_waypoints_svg(output_dir):
    filepath = os.path.join(output_dir, "via_multi")
    with Diagram("Via Multi", filename=filepath, rows=4, cols=4, outformat="svg", show=False):
        a = Node("A", icon="aws/compute/ec2", row=0, col=0)
        b = Node("B", icon="aws/compute/ec2", row=3, col=3)
        a >> Edge(via=[(0, 3), (1, 3), (1, 0), (3, 0)]) >> b

    with open(filepath + ".svg") as f:
        content = f.read()
    assert "<path" in content
    path_count = content.count("L ")
    assert path_count >= 4
