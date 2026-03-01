"""Parser for annotated Mermaid flowchart text into DiagramModel."""

import re
import uuid
from dataclasses import dataclass, field
from typing import Optional

from diagrams_for_ai.model import (
    ClusterModel,
    DiagramModel,
    Direction,
    EdgeModel,
    LineStyle,
    NodeModel,
)

# ---------------------------------------------------------------------------
# Annotation patterns  (%% @config, %% @node, %% @cluster)
# ---------------------------------------------------------------------------

_RE_CONFIG = re.compile(r"^%%\s*@config\s+(.+)$")
_RE_NODE_ANNOTATION = re.compile(r"^%%\s*@node\s+(\S+)\s+(.+)$")
_RE_CLUSTER_ANNOTATION = re.compile(r"^%%\s*@cluster\s+(.+)$")

# ---------------------------------------------------------------------------
# Mermaid structural patterns
# ---------------------------------------------------------------------------

_RE_GRAPH_HEADER = re.compile(r"^(graph|flowchart)\s+(TD|TB|LR|RL|BT)\s*$")
_RE_SUBGRAPH_START = re.compile(r"^subgraph\s+(\w+)\s*(?:\[([^\]]*)\])?\s*$")
_RE_SUBGRAPH_END = re.compile(r"^end\s*$")

# ---------------------------------------------------------------------------
# Node shape patterns  (id[label], id(label), id{label}, id((label)))
# ---------------------------------------------------------------------------

_NODE_SHAPES = [
    (r"\(\((.+?)\)\)", "circle"),
    (r"\[(.+?)\]", "rect"),
    (r"\((.+?)\)", "rounded"),
    (r"\{(.+?)\}", "diamond"),
]

_RE_NODE_DEF = re.compile(
    r"(\w+)(?:"
    + "|".join(pat for pat, _ in _NODE_SHAPES)
    + r")"
)

# ---------------------------------------------------------------------------
# Edge arrow patterns (order matters: longest first)
# ---------------------------------------------------------------------------

_ARROW_SPECS = [
    (r"-\.->", Direction.FORWARD, "dashed"),
    (r"==>", Direction.FORWARD, "bold"),
    (r"-->", Direction.FORWARD, ""),
    (r"---", Direction.NONE, ""),
    (r"<-->", Direction.BOTH, ""),
]

_ARROW_RE_PARTS = "|".join(
    f"({re.escape(arrow) if not any(c in arrow for c in '.') else arrow})"
    for arrow, _, _ in _ARROW_SPECS
)

_RE_EDGE_LABEL_PIPE = re.compile(
    r"(\w+)(?:\[[^\]]*\]|\([^)]*\)|\{[^}]*\}|\(\([^)]*\)\))?\s*"
    r"(" + "|".join(a for a, _, _ in _ARROW_SPECS) + r")"
    r"\|([^|]+)\|\s*"
    r"(\w+)(?:\[[^\]]*\]|\([^)]*\)|\{[^}]*\}|\(\([^)]*\)\))?"
)

_RE_EDGE_LABEL_INLINE = re.compile(
    r"(\w+)(?:\[[^\]]*\]|\([^)]*\)|\{[^}]*\}|\(\([^)]*\)\))?\s*"
    r"--\s+(.+?)\s+"
    r"(-->|---)\s*"
    r"(\w+)(?:\[[^\]]*\]|\([^)]*\)|\{[^}]*\}|\(\([^)]*\)\))?"
)

_RE_EDGE_SIMPLE = re.compile(
    r"(\w+)(?:\[[^\]]*\]|\([^)]*\)|\{[^}]*\}|\(\([^)]*\)\))?\s*"
    r"(" + "|".join(re.escape(a) if "." not in a else a for a, _, _ in _ARROW_SPECS) + r")\s*"
    r"(\w+)(?:\[[^\]]*\]|\([^)]*\)|\{[^}]*\}|\(\([^)]*\)\))?"
)

# ---------------------------------------------------------------------------
# Key-value parsing for annotations
# ---------------------------------------------------------------------------

_RE_KV_QUOTED = re.compile(r'(\w+)="([^"]*)"')
_RE_KV_PLAIN = re.compile(r"(\w+)=(\S+)")


@dataclass
class _NodeAnnotation:
    row: int
    col: int
    icon: str = ""


@dataclass
class _ClusterAnnotation:
    row: int
    col: int
    width: int
    height: int
    bg_color: str = "#E8F4FD"
    border_color: str = "#B0C4DE"


@dataclass
class _ConfigAnnotation:
    name: str = ""
    filename: str = ""
    rows: int = 0
    cols: int = 0
    cell_size: int = 180
    padding: int = 60
    icon_size: int = 64
    scale: int = 1
    bg: str = "#FFFFFF"


def _parse_kv(text: str) -> dict[str, str]:
    """Parse key=value pairs from annotation text."""
    result: dict[str, str] = {}
    for match in _RE_KV_QUOTED.finditer(text):
        result[match.group(1)] = match.group(2)
    remaining = _RE_KV_QUOTED.sub("", text)
    for match in _RE_KV_PLAIN.finditer(remaining):
        result[match.group(1)] = match.group(2)
    return result


def _parse_config(text: str) -> _ConfigAnnotation:
    kv = _parse_kv(text)
    return _ConfigAnnotation(
        name=kv.get("name", ""),
        filename=kv.get("filename", ""),
        rows=int(kv["rows"]) if "rows" in kv else 0,
        cols=int(kv["cols"]) if "cols" in kv else 0,
        cell_size=int(kv["cell_size"]) if "cell_size" in kv else 180,
        padding=int(kv["padding"]) if "padding" in kv else 60,
        icon_size=int(kv["icon_size"]) if "icon_size" in kv else 64,
        scale=int(kv["scale"]) if "scale" in kv else 1,
        bg=kv.get("bg", "#FFFFFF"),
    )


def _parse_node_annotation(kv_text: str) -> _NodeAnnotation:
    kv = _parse_kv(kv_text)
    pos = kv.get("pos", "")
    if not pos:
        raise ValueError("@node annotation requires pos=row,col")
    parts = pos.split(",")
    if len(parts) != 2:
        raise ValueError(f"@node pos must be row,col — got '{pos}'")
    return _NodeAnnotation(
        row=int(parts[0]),
        col=int(parts[1]),
        icon=kv.get("icon", ""),
    )


def _parse_cluster_annotation(kv_text: str) -> _ClusterAnnotation:
    kv = _parse_kv(kv_text)
    pos = kv.get("pos", "")
    size = kv.get("size", "")
    if not pos:
        raise ValueError("@cluster annotation requires pos=row,col")
    if not size:
        raise ValueError("@cluster annotation requires size=width,height")
    pos_parts = pos.split(",")
    size_parts = size.split(",")
    if len(pos_parts) != 2:
        raise ValueError(f"@cluster pos must be row,col — got '{pos}'")
    if len(size_parts) != 2:
        raise ValueError(f"@cluster size must be width,height — got '{size}'")
    return _ClusterAnnotation(
        row=int(pos_parts[0]),
        col=int(pos_parts[1]),
        width=int(size_parts[0]),
        height=int(size_parts[1]),
        bg_color=kv.get("bg", "#E8F4FD"),
        border_color=kv.get("border", "#B0C4DE"),
    )


def _arrow_to_direction_style(arrow: str) -> tuple[Direction, str]:
    for pattern, direction, style in _ARROW_SPECS:
        if re.fullmatch(pattern if "." in pattern else re.escape(pattern), arrow):
            return direction, style
    return Direction.FORWARD, ""


def _extract_node_defs(line: str, known_labels: dict[str, str]) -> None:
    """Scan a line for node definitions (id[label]) and record labels."""
    for match in _RE_NODE_DEF.finditer(line):
        node_id = match.group(1)
        label = next(
            (match.group(i) for i in range(2, 2 + len(_NODE_SHAPES)) if match.group(i)),
            None,
        )
        if label and node_id not in known_labels:
            known_labels[node_id] = label


def _extract_edges(
    line: str,
    known_nodes: set[str],
) -> list[tuple[str, str, str, Direction, str]]:
    """Extract edges from a line. Returns list of (src, tgt, label, direction, style)."""
    edges: list[tuple[str, str, str, Direction, str]] = []

    m = _RE_EDGE_LABEL_PIPE.search(line)
    if m:
        src, arrow, label, tgt = m.group(1), m.group(2), m.group(3), m.group(4)
        direction, style = _arrow_to_direction_style(arrow)
        edges.append((src, tgt, label.strip(), direction, style))
        known_nodes.add(src)
        known_nodes.add(tgt)
        remaining = line[:m.start()] + tgt + line[m.end():]
        edges.extend(_extract_edges(remaining, known_nodes))
        return edges

    m = _RE_EDGE_LABEL_INLINE.search(line)
    if m:
        src, label, arrow, tgt = m.group(1), m.group(2), m.group(3), m.group(4)
        direction, style = _arrow_to_direction_style(arrow)
        edges.append((src, tgt, label.strip(), direction, style))
        known_nodes.add(src)
        known_nodes.add(tgt)
        remaining = line[:m.start()] + tgt + line[m.end():]
        edges.extend(_extract_edges(remaining, known_nodes))
        return edges

    m = _RE_EDGE_SIMPLE.search(line)
    if m:
        src, arrow, tgt = m.group(1), m.group(2), m.group(3)
        direction, style = _arrow_to_direction_style(arrow)
        edges.append((src, tgt, "", direction, style))
        known_nodes.add(src)
        known_nodes.add(tgt)
        remaining = line[:m.start()] + tgt + line[m.end():]
        edges.extend(_extract_edges(remaining, known_nodes))
        return edges

    return edges


# ---------------------------------------------------------------------------
# Main parse function
# ---------------------------------------------------------------------------


def parse_mermaid(text: str) -> DiagramModel:
    """Parse annotated Mermaid flowchart text into a DiagramModel.

    Annotations are embedded as Mermaid comments (``%% @...``) so standard
    Mermaid renderers ignore them while this parser extracts grid positions,
    icons, and diagram configuration.

    Raises ``ValueError`` for malformed annotations or missing node positions.
    """
    lines = text.strip().splitlines()

    config = _ConfigAnnotation()
    node_annotations: dict[str, _NodeAnnotation] = {}
    cluster_annotations: dict[str, _ClusterAnnotation] = {}

    known_labels: dict[str, str] = {}
    known_nodes: set[str] = set()
    raw_edges: list[tuple[str, str, str, Direction, str]] = []

    subgraph_stack: list[str] = []
    subgraph_labels: dict[str, str] = {}
    node_to_subgraph: dict[str, str] = {}
    pending_cluster_id: Optional[str] = None

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        # Strip trailing Mermaid comments (but not annotation lines)
        if not line.startswith("%%"):
            comment_idx = line.find("%%")
            if comment_idx > 0:
                line = line[:comment_idx].strip()

        # --- Annotations ---
        m = _RE_CONFIG.match(line)
        if m:
            config = _parse_config(m.group(1))
            continue

        m = _RE_NODE_ANNOTATION.match(line)
        if m:
            node_id = m.group(1)
            node_annotations[node_id] = _parse_node_annotation(m.group(2))
            continue

        m = _RE_CLUSTER_ANNOTATION.match(line)
        if m:
            if pending_cluster_id:
                cluster_annotations[pending_cluster_id] = _parse_cluster_annotation(
                    m.group(1)
                )
                pending_cluster_id = None
            continue

        # Skip other comments
        if line.startswith("%%"):
            continue

        # --- Graph header ---
        if _RE_GRAPH_HEADER.match(line):
            continue

        # --- Subgraph ---
        m = _RE_SUBGRAPH_START.match(line)
        if m:
            sg_id = m.group(1)
            sg_label = m.group(2) if m.group(2) else sg_id
            subgraph_stack.append(sg_id)
            subgraph_labels[sg_id] = sg_label
            pending_cluster_id = sg_id
            continue

        if _RE_SUBGRAPH_END.match(line):
            if subgraph_stack:
                subgraph_stack.pop()
            continue

        # --- Semicollon separated statements ---
        statements = [s.strip() for s in line.split(";") if s.strip()]

        for stmt in statements:
            _extract_node_defs(stmt, known_labels)

            found_edges = _extract_edges(stmt, known_nodes)
            if found_edges:
                for src, tgt, label, direction, style in found_edges:
                    if subgraph_stack:
                        if src not in node_to_subgraph:
                            node_to_subgraph[src] = subgraph_stack[-1]
                        if tgt not in node_to_subgraph:
                            node_to_subgraph[tgt] = subgraph_stack[-1]
                    raw_edges.append((src, tgt, label, direction, style))
            else:
                m_node = _RE_NODE_DEF.match(stmt)
                if m_node:
                    node_id = m_node.group(1)
                    known_nodes.add(node_id)
                    if subgraph_stack and node_id not in node_to_subgraph:
                        node_to_subgraph[node_id] = subgraph_stack[-1]

    # Merge known_nodes from edges
    all_node_ids = known_nodes | set(known_labels.keys())

    # Validate: every node must have a @node annotation with pos
    for node_id in all_node_ids:
        if node_id not in node_annotations:
            raise ValueError(
                f"Node '{node_id}' found in Mermaid text but has no "
                f"'%% @node {node_id} pos=row,col' annotation"
            )

    # Auto-compute rows/cols from node positions if not in @config
    max_row = 0
    max_col = 0
    for ann in node_annotations.values():
        max_row = max(max_row, ann.row)
        max_col = max(max_col, ann.col)

    rows = config.rows if config.rows > 0 else max_row + 1
    cols = config.cols if config.cols > 0 else max_col + 1

    # Derive filename
    name = config.name
    filename = config.filename
    if not filename:
        filename = "_".join(name.split()).lower() if name else "diagram"

    # Build nodes
    nodes: list[NodeModel] = []
    id_map: dict[str, str] = {}
    for node_id in sorted(all_node_ids):
        ann = node_annotations[node_id]
        internal_id = uuid.uuid4().hex
        id_map[node_id] = internal_id
        cluster_id = None
        sg = node_to_subgraph.get(node_id)
        if sg and sg in cluster_annotations:
            cluster_id = sg
        nodes.append(
            NodeModel(
                id=internal_id,
                label=known_labels.get(node_id, node_id),
                icon=ann.icon,
                row=ann.row,
                col=ann.col,
                cluster_id=cluster_id,
            )
        )

    # Build edges
    edges: list[EdgeModel] = []
    for src, tgt, label, direction, style in raw_edges:
        edges.append(
            EdgeModel(
                source_id=id_map[src],
                target_id=id_map[tgt],
                label=label,
                style=style,
                direction=direction,
            )
        )

    # Build clusters
    clusters: list[ClusterModel] = []
    for sg_id, ann in cluster_annotations.items():
        clusters.append(
            ClusterModel(
                id=sg_id,
                label=subgraph_labels.get(sg_id, sg_id),
                row=ann.row,
                col=ann.col,
                width=ann.width,
                height=ann.height,
                bg_color=ann.bg_color,
                border_color=ann.border_color,
            )
        )

    return DiagramModel(
        name=name,
        filename=filename,
        rows=rows,
        cols=cols,
        cell_size=config.cell_size,
        padding=config.padding,
        icon_size=config.icon_size,
        scale=config.scale,
        nodes=nodes,
        edges=edges,
        clusters=clusters,
        bg_color=config.bg,
    )
