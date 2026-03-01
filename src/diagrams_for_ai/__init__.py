"""diagrams_for_ai - AI-friendly architecture diagrams with grid-based positioning."""

import contextvars
import os
import uuid
from typing import Optional, Union

from diagrams_for_ai.model import (
    ClusterModel,
    DiagramModel,
    Direction,
    EdgeModel,
    LineStyle,
    NodeModel,
)
from diagrams_for_ai.ext.mermaid import parse_mermaid
from diagrams_for_ai.renderer_png import render_png
from diagrams_for_ai.renderer_svg import render_svg

__all__ = ["Diagram", "Node", "Edge", "Cluster", "LineStyle"]

_current_diagram: contextvars.ContextVar[Optional["Diagram"]] = contextvars.ContextVar(
    "current_diagram", default=None
)
_current_cluster: contextvars.ContextVar[Optional["Cluster"]] = (
    contextvars.ContextVar("current_cluster", default=None)
)


class Diagram:
    """Top-level diagram context.

    Usage::

        with Diagram("My Architecture", rows=4, cols=6) as d:
            ...
    """

    def __init__(
        self,
        name: str = "",
        *,
        filename: str = "",
        rows: int = 4,
        cols: int = 6,
        cell_size: int = 180,
        padding: int = 60,
        icon_size: int = 64,
        scale: int = 1,
        outformat: Union[str, list[str]] = "png",
        show: bool = True,
        bg_color: str = "#FFFFFF",
    ):
        if not filename:
            filename = "_".join(name.split()).lower() if name else "diagram"

        self._model = DiagramModel(
            name=name,
            filename=filename,
            rows=rows,
            cols=cols,
            cell_size=cell_size,
            padding=padding,
            icon_size=icon_size,
            scale=scale,
            bg_color=bg_color,
            show=show,
        )

        if isinstance(outformat, str):
            outformat = [outformat]
        self._outformats = outformat
        self._edges_pending: list[tuple["Node", "Node", "Edge"]] = []

    @classmethod
    def from_mermaid(
        cls,
        text: str,
        *,
        outformat: Union[str, list[str]] = "png",
        show: bool = True,
        filename: str = "",
    ) -> "Diagram":
        """Create a Diagram by parsing annotated Mermaid flowchart text.

        The Mermaid text should contain ``%% @node`` annotations with grid
        positions.  Call ``.render()`` on the returned instance to produce
        output files.
        """
        model = parse_mermaid(text)
        if filename:
            model.filename = filename
        model.show = show
        instance = cls.__new__(cls)
        instance._model = model
        instance._outformats = [outformat] if isinstance(outformat, str) else outformat
        instance._edges_pending = []
        return instance

    @classmethod
    def from_mermaid_file(
        cls,
        path: str,
        *,
        outformat: Union[str, list[str]] = "png",
        show: bool = True,
        filename: str = "",
    ) -> "Diagram":
        """Create a Diagram from an annotated Mermaid ``.mmd`` file.

        Reads the file at *path* and delegates to :meth:`from_mermaid`.
        """
        with open(path) as f:
            text = f.read()
        return cls.from_mermaid(
            text, outformat=outformat, show=show, filename=filename
        )

    @property
    def model(self) -> DiagramModel:
        return self._model

    def __enter__(self):
        _current_diagram.set(self)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self._flush_edges()
            self.render()
        _current_diagram.set(None)

    def _flush_edges(self):
        for src, tgt, edge in self._edges_pending:
            self._model.edges.append(
                EdgeModel(
                    source_id=src._id,
                    target_id=tgt._id,
                    label=edge.label,
                    color=edge.color,
                    style=edge.style,
                    line_style=edge.line_style,
                    direction=edge.direction,
                    via=edge.via,
                )
            )
        self._edges_pending.clear()

    def add_edge(self, src: "Node", tgt: "Node", edge: "Edge"):
        self._edges_pending.append((src, tgt, edge))

    def render(self):
        for fmt in self._outformats:
            if fmt == "svg":
                svg_str = render_svg(self._model)
                path = f"{self._model.filename}.svg"
                with open(path, "w") as f:
                    f.write(svg_str)
            elif fmt in ("png", "jpg"):
                img = render_png(self._model)
                path = f"{self._model.filename}.{fmt}"
                if fmt == "jpg":
                    img = img.convert("RGB")
                img.save(path)
            else:
                raise ValueError(f"Unsupported output format: {fmt}")

        if self._model.show and self._outformats:
            first_path = f"{self._model.filename}.{self._outformats[0]}"
            if os.path.isfile(first_path):
                _open_file(first_path)


class Node:
    """A positioned node with an icon.

    Usage::

        lb = Node("Load Balancer", icon="aws/network/elb", row=0, col=2)
    """

    def __init__(
        self,
        label: str = "",
        *,
        icon: str = "",
        row: int = 0,
        col: int = 0,
    ):
        self._id = uuid.uuid4().hex
        self.label = label
        self.icon = icon
        self.row = row
        self.col = col

        diagram = _current_diagram.get()
        if diagram is None:
            raise RuntimeError("Node must be created inside a Diagram context")

        self._diagram = diagram
        cluster = _current_cluster.get()

        diagram.model.nodes.append(
            NodeModel(
                id=self._id,
                label=label,
                icon=icon,
                row=row,
                col=col,
                cluster_id=cluster._id if cluster else None,
            )
        )

    def __rshift__(self, other: Union["Node", list["Node"], "Edge"]):
        """self >> other (forward connection)."""
        if isinstance(other, list):
            for node in other:
                self._connect(node, Edge(), Direction.FORWARD)
            return other
        if isinstance(other, Edge):
            other._source = self
            other.direction = Direction.FORWARD
            return other
        self._connect(other, Edge(), Direction.FORWARD)
        return other

    def __lshift__(self, other: Union["Node", list["Node"], "Edge"]):
        """self << other (reverse connection)."""
        if isinstance(other, list):
            for node in other:
                node._connect(self, Edge(), Direction.FORWARD)
            return other
        if isinstance(other, Edge):
            other._source = self
            other.direction = Direction.REVERSE
            return other
        other._connect(self, Edge(), Direction.FORWARD)
        return other

    def __sub__(self, other: Union["Node", list["Node"], "Edge"]):
        """self - other (undirected connection)."""
        if isinstance(other, list):
            for node in other:
                self._connect(node, Edge(), Direction.NONE)
            return other
        if isinstance(other, Edge):
            other._source = self
            other.direction = Direction.NONE
            return other
        self._connect(other, Edge(), Direction.NONE)
        return other

    def __rrshift__(self, other: Union[list["Node"], list["Edge"]]):
        """[nodes] >> self."""
        for o in other:
            if isinstance(o, Node):
                o._connect(self, Edge(), Direction.FORWARD)
        return self

    def __rlshift__(self, other: Union[list["Node"], list["Edge"]]):
        """[nodes] << self."""
        for o in other:
            if isinstance(o, Node):
                self._connect(o, Edge(), Direction.FORWARD)
        return self

    def _connect(self, target: "Node", edge: "Edge", direction: Direction):
        edge.direction = direction
        self._diagram.add_edge(self, target, edge)


class Edge:
    """Customizes a connection between nodes.

    Usage::

        node1 >> Edge(label="HTTP", style="dashed", color="#E74C3C") >> node2
    """

    def __init__(
        self,
        *,
        label: str = "",
        color: str = "",
        style: str = "",
        line_style: LineStyle = LineStyle.CURVED,
        via: list[tuple[int, int]] | None = None,
    ):
        self.label = label
        self.color = color
        self.style = style
        self.line_style = line_style
        self.via: list[tuple[int, int]] = via or []
        self.direction = Direction.FORWARD
        self._source: Optional[Node] = None

    def __rshift__(self, other: Union["Node", list["Node"]]):
        """edge >> node (forward)."""
        if self.direction == Direction.NONE:
            pass
        elif self.direction == Direction.REVERSE:
            pass
        else:
            self.direction = Direction.FORWARD

        if isinstance(other, list):
            if self._source:
                for node in other:
                    self._source._connect(node, self._copy(), self.direction)
            return other

        if self._source:
            self._source._connect(other, self, self.direction)
        return other

    def __lshift__(self, other: Union["Node", list["Node"]]):
        """edge << node (reverse)."""
        self.direction = Direction.REVERSE
        if isinstance(other, list):
            if self._source:
                for node in other:
                    node._connect(self._source, self._copy(), Direction.FORWARD)
            return other

        if self._source:
            other._connect(self._source, self, Direction.FORWARD)
        return other

    def _copy(self) -> "Edge":
        return Edge(
            label=self.label,
            color=self.color,
            style=self.style,
            line_style=self.line_style,
            via=list(self.via),
        )


class Cluster:
    """A visual grouping of nodes spanning a grid region.

    Usage::

        with Cluster("VPC", row=1, col=0, width=4, height=2):
            ...
    """

    def __init__(
        self,
        label: str = "",
        *,
        row: int = 0,
        col: int = 0,
        width: int = 2,
        height: int = 2,
        bg_color: str = "#E8F4FD",
        border_color: str = "#B0C4DE",
    ):
        self._id = uuid.uuid4().hex
        self.label = label

        diagram = _current_diagram.get()
        if diagram is None:
            raise RuntimeError("Cluster must be created inside a Diagram context")

        self._diagram = diagram
        diagram.model.clusters.append(
            ClusterModel(
                id=self._id,
                label=label,
                row=row,
                col=col,
                width=width,
                height=height,
                bg_color=bg_color,
                border_color=border_color,
            )
        )

    def __enter__(self):
        self._prev = _current_cluster.get()
        _current_cluster.set(self)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        _current_cluster.set(self._prev)


def _open_file(path: str):
    """Open a file with the system default viewer."""
    import platform
    import subprocess

    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.Popen(["open", path])
        elif system == "Linux":
            subprocess.Popen(["xdg-open", path])
        elif system == "Windows":
            os.startfile(path)
    except OSError:
        pass
