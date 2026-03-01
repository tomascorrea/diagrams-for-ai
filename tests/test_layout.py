import pytest

from diagrams_for_ai.layout import (
    Point,
    cluster_rect,
    grid_center,
    node_center,
    node_connection_point,
    node_icon_rect,
    node_label_position,
)
from diagrams_for_ai.model import ClusterModel, DiagramModel, NodeModel


@pytest.fixture
def diagram():
    return DiagramModel(
        name="test", filename="test", rows=4, cols=6, cell_size=180, padding=60
    )


@pytest.fixture
def origin_node():
    return NodeModel(id="n1", label="Test", icon="aws/compute/ec2", row=0, col=0)


@pytest.fixture
def offset_node():
    return NodeModel(id="n2", label="Test", icon="aws/compute/ec2", row=2, col=3)


def test_node_center_at_origin(diagram, origin_node):
    center = node_center(origin_node, diagram)
    assert center.x == 60 + 90  # padding + half cell
    assert center.y == 60 + 90


def test_node_center_at_offset(diagram, offset_node):
    center = node_center(offset_node, diagram)
    assert center.x == 60 + 3 * 180 + 90
    assert center.y == 60 + 2 * 180 + 90


def test_icon_rect_centered_in_cell(diagram, origin_node):
    rect = node_icon_rect(origin_node, diagram)
    assert rect.width == 64
    assert rect.height == 64
    center = node_center(origin_node, diagram)
    assert abs(rect.x + 32 - center.x) < 0.01


def test_label_below_icon(diagram, origin_node):
    label_pos = node_label_position(origin_node, diagram)
    center = node_center(origin_node, diagram)
    assert label_pos.y > center.y
    assert label_pos.x == center.x


def test_horizontal_connection_point(diagram, origin_node):
    target = Point(1000, node_center(origin_node, diagram).y)
    conn = node_connection_point(origin_node, diagram, target)
    icon_rect = node_icon_rect(origin_node, diagram)
    assert abs(conn.x - (icon_rect.x + icon_rect.width)) < 0.01


def test_vertical_connection_point(diagram, origin_node):
    center = node_center(origin_node, diagram)
    target = Point(center.x, 1000)
    conn = node_connection_point(origin_node, diagram, target)
    icon_rect = node_icon_rect(origin_node, diagram)
    assert abs(conn.y - (icon_rect.y + icon_rect.height)) < 0.01


def test_cluster_rect_spans_cells(diagram):
    cluster = ClusterModel(id="c1", label="Test", row=0, col=0, width=3, height=2)
    rect = cluster_rect(cluster, diagram)
    assert rect.width > 3 * 180
    assert rect.height > 2 * 180


def test_canvas_dimensions():
    diagram = DiagramModel(
        name="test", filename="test", rows=4, cols=6, cell_size=180, padding=60
    )
    assert diagram.canvas_width == 6 * 180 + 2 * 60
    assert diagram.canvas_height == 4 * 180 + 2 * 60


# ---------------------------------------------------------------------------
# scale parameter
# ---------------------------------------------------------------------------


@pytest.fixture
def diagram_2x():
    return DiagramModel(
        name="test", filename="test", rows=4, cols=6, cell_size=180, padding=60,
        scale=2,
    )


def test_canvas_dimensions_scale_2():
    d = DiagramModel(
        name="test", filename="test", rows=4, cols=6, cell_size=180, padding=60,
        scale=2,
    )
    assert d.canvas_width == (6 * 180 + 2 * 60) * 2
    assert d.canvas_height == (4 * 180 + 2 * 60) * 2


def test_node_center_scales(origin_node, diagram, diagram_2x):
    c1 = node_center(origin_node, diagram)
    c2 = node_center(origin_node, diagram_2x)
    assert abs(c2.x - c1.x * 2) < 0.01
    assert abs(c2.y - c1.y * 2) < 0.01


def test_icon_rect_scales(origin_node, diagram, diagram_2x):
    r1 = node_icon_rect(origin_node, diagram)
    r2 = node_icon_rect(origin_node, diagram_2x)
    assert r2.width == r1.width * 2
    assert r2.height == r1.height * 2


def test_label_position_scales(origin_node, diagram, diagram_2x):
    l1 = node_label_position(origin_node, diagram)
    l2 = node_label_position(origin_node, diagram_2x)
    assert abs(l2.x - l1.x * 2) < 0.01
    assert abs(l2.y - l1.y * 2) < 0.01


def test_cluster_rect_scales(diagram, diagram_2x):
    cluster = ClusterModel(id="c1", label="Test", row=0, col=0, width=3, height=2)
    r1 = cluster_rect(cluster, diagram)
    r2 = cluster_rect(cluster, diagram_2x)
    assert abs(r2.width - r1.width * 2) < 0.01
    assert abs(r2.height - r1.height * 2) < 0.01


# ---------------------------------------------------------------------------
# icon_size parameter
# ---------------------------------------------------------------------------


def test_custom_icon_size():
    d = DiagramModel(
        name="test", filename="test", rows=4, cols=6, cell_size=180, padding=60,
        icon_size=80,
    )
    node = NodeModel(id="n1", label="Test", icon="aws/compute/ec2", row=0, col=0)
    rect = node_icon_rect(node, d)
    assert rect.width == 80
    assert rect.height == 80


def test_icon_size_and_scale_combine():
    d = DiagramModel(
        name="test", filename="test", rows=4, cols=6, cell_size=180, padding=60,
        icon_size=80, scale=2,
    )
    node = NodeModel(id="n1", label="Test", icon="aws/compute/ec2", row=0, col=0)
    rect = node_icon_rect(node, d)
    assert rect.width == 160
    assert rect.height == 160


# ---------------------------------------------------------------------------
# grid_center
# ---------------------------------------------------------------------------


def test_grid_center_matches_node_center(diagram, origin_node, offset_node):
    assert grid_center(0, 0, diagram) == node_center(origin_node, diagram)
    assert grid_center(2, 3, diagram) == node_center(offset_node, diagram)


def test_grid_center_at_origin(diagram):
    center = grid_center(0, 0, diagram)
    assert center.x == 60 + 90
    assert center.y == 60 + 90


def test_grid_center_scales(diagram, diagram_2x):
    c1 = grid_center(1, 2, diagram)
    c2 = grid_center(1, 2, diagram_2x)
    assert abs(c2.x - c1.x * 2) < 0.01
    assert abs(c2.y - c1.y * 2) < 0.01
