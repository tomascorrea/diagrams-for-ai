import pytest

from diagrams_for_ai.layout import (
    Point,
    cluster_rect,
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
