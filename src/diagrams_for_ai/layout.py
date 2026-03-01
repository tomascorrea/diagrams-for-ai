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


DEFAULT_ICON_SIZE = 64
DEFAULT_LABEL_HEIGHT = 24


def _effective(diagram: DiagramModel) -> tuple[int, int, int, int]:
    """Return (cell_size, padding, icon_size, label_height) scaled by diagram.scale."""
    s = diagram.scale
    return (
        diagram.cell_size * s,
        diagram.padding * s,
        diagram.icon_size * s,
        DEFAULT_LABEL_HEIGHT * s,
    )


def node_center(node: NodeModel, diagram: DiagramModel) -> Point:
    """Return the pixel center of a node's grid cell."""
    cell_size, padding, _, _ = _effective(diagram)
    x = padding + node.col * cell_size + cell_size / 2
    y = padding + node.row * cell_size + cell_size / 2
    return Point(x, y)


def node_icon_rect(node: NodeModel, diagram: DiagramModel) -> Rect:
    """Return the bounding rect for a node's icon (centered in its cell)."""
    _, _, icon_size, label_height = _effective(diagram)
    center = node_center(node, diagram)
    return Rect(
        x=center.x - icon_size / 2,
        y=center.y - icon_size / 2 - label_height / 2,
        width=icon_size,
        height=icon_size,
    )


def node_label_position(node: NodeModel, diagram: DiagramModel) -> Point:
    """Return the position for drawing a node's label (centered below the icon)."""
    _, _, icon_size, label_height = _effective(diagram)
    center = node_center(node, diagram)
    return Point(center.x, center.y + icon_size / 2 + label_height / 2)


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
    cell_size, padding, _, _ = _effective(diagram)
    margin = 16 * diagram.scale
    x = padding + cluster.col * cell_size - margin
    y = padding + cluster.row * cell_size - margin
    width = cluster.width * cell_size + 2 * margin
    height = cluster.height * cell_size + 2 * margin
    return Rect(x, y, width, height)
