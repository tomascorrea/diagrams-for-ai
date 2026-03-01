from dataclasses import dataclass

from diagrams_for_ai.model import ClusterModel, DiagramModel, NodeModel


@dataclass(frozen=True)
class Point:
    x: float
    y: float


@dataclass(frozen=True)
class Rect:
    x: float
    y: float
    width: float
    height: float

    @property
    def center(self) -> Point:
        return Point(self.x + self.width / 2, self.y + self.height / 2)


ICON_SIZE = 64
LABEL_HEIGHT = 24


def node_center(node: NodeModel, diagram: DiagramModel) -> Point:
    """Return the pixel center of a node's grid cell."""
    x = diagram.padding + node.col * diagram.cell_size + diagram.cell_size / 2
    y = diagram.padding + node.row * diagram.cell_size + diagram.cell_size / 2
    return Point(x, y)


def node_icon_rect(node: NodeModel, diagram: DiagramModel) -> Rect:
    """Return the bounding rect for a node's icon (centered in its cell)."""
    center = node_center(node, diagram)
    return Rect(
        x=center.x - ICON_SIZE / 2,
        y=center.y - ICON_SIZE / 2 - LABEL_HEIGHT / 2,
        width=ICON_SIZE,
        height=ICON_SIZE,
    )


def node_label_position(node: NodeModel, diagram: DiagramModel) -> Point:
    """Return the position for drawing a node's label (centered below the icon)."""
    center = node_center(node, diagram)
    return Point(center.x, center.y + ICON_SIZE / 2 + LABEL_HEIGHT / 2)


def node_connection_point(
    node: NodeModel, diagram: DiagramModel, toward: Point
) -> Point:
    """Return the point on the node's icon border closest to `toward`.

    Uses a simple rectangular intersection approach.
    """
    icon = node_icon_rect(node, diagram)
    cx, cy = icon.center.x, icon.center.y
    dx = toward.x - cx
    dy = toward.y - cy

    if abs(dx) < 0.001 and abs(dy) < 0.001:
        return Point(cx, cy)

    half_w = icon.width / 2
    half_h = icon.height / 2

    if abs(dx) * half_h > abs(dy) * half_w:
        scale = half_w / abs(dx)
    else:
        scale = half_h / abs(dy)

    return Point(cx + dx * scale, cy + dy * scale)


def cluster_rect(cluster: ClusterModel, diagram: DiagramModel) -> Rect:
    """Return the pixel bounding rect for a cluster."""
    margin = 16
    x = diagram.padding + cluster.col * diagram.cell_size - margin
    y = diagram.padding + cluster.row * diagram.cell_size - margin
    width = cluster.width * diagram.cell_size + 2 * margin
    height = cluster.height * diagram.cell_size + 2 * margin
    return Rect(x, y, width, height)
