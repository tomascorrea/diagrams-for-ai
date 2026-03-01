from xml.sax.saxutils import escape

from diagrams_for_ai.icons import load_icon_base64
from diagrams_for_ai.layout import (
    ICON_SIZE,
    cluster_rect,
    node_center,
    node_connection_point,
    node_icon_rect,
    node_label_position,
)
from diagrams_for_ai.model import DiagramModel, Direction
from diagrams_for_ai.paths import compute_path


def render_svg(diagram: DiagramModel) -> str:
    """Render a DiagramModel to an SVG string."""
    w = diagram.canvas_width
    h = diagram.canvas_height

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
        "<defs>",
        '  <filter id="shadow" x="-10%" y="-10%" width="140%" height="140%">',
        '    <feDropShadow dx="1" dy="2" stdDeviation="3" flood-opacity="0.15"/>',
        "  </filter>",
        "</defs>",
        f'<rect width="{w}" height="{h}" fill="{diagram.bg_color}"/>',
    ]

    if diagram.name:
        parts.append(
            f'<text x="{w / 2}" y="30" text-anchor="middle" '
            f'font-family="Sans-Serif" font-size="18" font-weight="bold" '
            f'fill="#2D3436">{escape(diagram.name)}</text>'
        )

    for cluster in diagram.clusters:
        _render_cluster_svg(parts, cluster, diagram)

    for edge in diagram.edges:
        _render_edge_svg(parts, edge, diagram)

    for node in diagram.nodes:
        _render_node_svg(parts, node, diagram)

    parts.append("</svg>")
    return "\n".join(parts)


def _render_cluster_svg(parts, cluster, diagram):
    rect = cluster_rect(cluster, diagram)
    rx = 12
    parts.append(
        f'<rect x="{rect.x:.1f}" y="{rect.y:.1f}" '
        f'width="{rect.width:.1f}" height="{rect.height:.1f}" '
        f'rx="{rx}" ry="{rx}" '
        f'fill="{cluster.bg_color}" stroke="{cluster.border_color}" '
        f'stroke-width="1.5" stroke-dasharray="6 3"/>'
    )
    parts.append(
        f'<text x="{rect.x + 12}" y="{rect.y + 20}" '
        f'font-family="Sans-Serif" font-size="13" font-weight="bold" '
        f'fill="#495057">{escape(cluster.label)}</text>'
    )


def _render_edge_svg(parts, edge, diagram):
    src = diagram.node_by_id(edge.source_id)
    tgt = diagram.node_by_id(edge.target_id)
    if not src or not tgt:
        return

    src_center = node_center(src, diagram)
    tgt_center = node_center(tgt, diagram)

    start = node_connection_point(src, diagram, tgt_center)
    end = node_connection_point(tgt, diagram, src_center)

    path = compute_path(start, end, edge.line_style, edge.direction)

    color = edge.color or "#495057"
    dash = ""
    if edge.style == "dashed":
        dash = ' stroke-dasharray="6 4"'
    elif edge.style == "dotted":
        dash = ' stroke-dasharray="2 3"'

    parts.append(
        f'<path d="{path.svg_path}" fill="none" '
        f'stroke="{color}" stroke-width="1.8"{dash}/>'
    )

    if path.arrow:
        a = path.arrow
        parts.append(
            f'<polygon points="{a.tip.x:.1f},{a.tip.y:.1f} '
            f'{a.left.x:.1f},{a.left.y:.1f} '
            f'{a.right.x:.1f},{a.right.y:.1f}" '
            f'fill="{color}"/>'
        )

    if edge.direction == Direction.BOTH:
        reverse_path = compute_path(end, start, edge.line_style, Direction.FORWARD)
        if reverse_path.arrow:
            a = reverse_path.arrow
            parts.append(
                f'<polygon points="{a.tip.x:.1f},{a.tip.y:.1f} '
                f'{a.left.x:.1f},{a.left.y:.1f} '
                f'{a.right.x:.1f},{a.right.y:.1f}" '
                f'fill="{color}"/>'
            )

    if edge.label:
        mid_x = (start.x + end.x) / 2
        mid_y = (start.y + end.y) / 2
        parts.append(
            f'<text x="{mid_x:.1f}" y="{mid_y - 6:.1f}" '
            f'text-anchor="middle" font-family="Sans-Serif" '
            f'font-size="11" fill="#6C757D">{escape(edge.label)}</text>'
        )


def _render_node_svg(parts, node, diagram):
    icon_rect = node_icon_rect(node, diagram)
    label_pos = node_label_position(node, diagram)

    data_uri = load_icon_base64(node.icon)
    parts.append(
        f'<image href="{data_uri}" '
        f'x="{icon_rect.x:.1f}" y="{icon_rect.y:.1f}" '
        f'width="{ICON_SIZE}" height="{ICON_SIZE}" '
        f'filter="url(#shadow)"/>'
    )

    parts.append(
        f'<text x="{label_pos.x:.1f}" y="{label_pos.y:.1f}" '
        f'text-anchor="middle" font-family="Sans-Serif" '
        f'font-size="12" fill="#2D3436">{escape(node.label)}</text>'
    )
