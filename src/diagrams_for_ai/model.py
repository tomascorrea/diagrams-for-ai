from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class LineStyle(Enum):
    STRAIGHT = "straight"
    CURVED = "curved"
    ORTHO = "ortho"
    STEP = "step"


class Direction(Enum):
    FORWARD = "forward"
    REVERSE = "reverse"
    BOTH = "both"
    NONE = "none"


@dataclass
class NodeModel:
    id: str
    label: str
    icon: str
    row: int
    col: int
    cluster_id: Optional[str] = None


@dataclass
class EdgeModel:
    source_id: str
    target_id: str
    label: str = ""
    color: str = ""
    style: str = ""
    line_style: LineStyle = LineStyle.CURVED
    direction: Direction = Direction.FORWARD


@dataclass
class ClusterModel:
    id: str
    label: str
    row: int
    col: int
    width: int
    height: int
    bg_color: str = "#E8F4FD"
    border_color: str = "#B0C4DE"


@dataclass
class DiagramModel:
    name: str
    filename: str
    rows: int
    cols: int
    cell_size: int = 180
    padding: int = 60
    icon_size: int = 64
    scale: int = 1
    nodes: list[NodeModel] = field(default_factory=list)
    edges: list[EdgeModel] = field(default_factory=list)
    clusters: list[ClusterModel] = field(default_factory=list)
    bg_color: str = "#FFFFFF"
    show: bool = True

    @property
    def canvas_width(self) -> int:
        return self.cols * self.cell_size * self.scale + 2 * self.padding * self.scale

    @property
    def canvas_height(self) -> int:
        return self.rows * self.cell_size * self.scale + 2 * self.padding * self.scale

    def node_by_id(self, node_id: str) -> Optional[NodeModel]:
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None
