from PIL import Image, ImageDraw, ImageFont

from diagrams_for_ai.icons import load_icon_image
from diagrams_for_ai.layout import (
    cluster_rect,
    node_center,
    node_connection_point,
    node_icon_rect,
    node_label_position,
)
from diagrams_for_ai.model import DiagramModel, Direction
from diagrams_for_ai.paths import compute_path


def render_png(diagram: DiagramModel) -> Image.Image:
    """Render a DiagramModel to a Pillow Image."""
    s = diagram.scale
    w = diagram.canvas_width
    h = diagram.canvas_height
    icon_size = diagram.icon_size * s

    font = _load_font(round(12 * s))
    title_font = _load_font(round(18 * s))
    edge_label_font = _load_font(round(11 * s))
    line_width = max(1, round(2 * s))
    arrow_size = 10.0 * s

    canvas = Image.new("RGBA", (w, h), diagram.bg_color)
    draw = ImageDraw.Draw(canvas)

    if diagram.name:
        bbox = draw.textbbox((0, 0), diagram.name, font=title_font)
        tw = bbox[2] - bbox[0]
        draw.text(
            ((w - tw) / 2, 12 * s),
            diagram.name,
            fill="#2D3436",
            font=title_font,
        )

    for cluster in diagram.clusters:
        _render_cluster_png(draw, cluster, diagram, font, line_width, s)

    for edge in diagram.edges:
        _render_edge_png(draw, edge, diagram, edge_label_font, line_width, arrow_size, s)

    for node in diagram.nodes:
        _render_node_png(canvas, draw, node, diagram, font, icon_size)

    return canvas


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.truetype("Arial", size)
    except (IOError, OSError):
        try:
            return ImageFont.truetype("DejaVuSans", size)
        except (IOError, OSError):
            return ImageFont.load_default()


def _render_cluster_png(draw, cluster, diagram, font, line_width, scale):
    rect = cluster_rect(cluster, diagram)
    draw.rounded_rectangle(
        [rect.x, rect.y, rect.x + rect.width, rect.y + rect.height],
        radius=round(12 * scale),
        fill=cluster.bg_color,
        outline=cluster.border_color,
        width=line_width,
    )
    draw.text(
        (rect.x + 12 * scale, rect.y + 6 * scale),
        cluster.label,
        fill="#495057",
        font=font,
    )


def _render_edge_png(draw, edge, diagram, font, line_width, arrow_size, scale):
    src = diagram.node_by_id(edge.source_id)
    tgt = diagram.node_by_id(edge.target_id)
    if not src or not tgt:
        return

    src_center = node_center(src, diagram)
    tgt_center = node_center(tgt, diagram)

    start = node_connection_point(src, diagram, tgt_center)
    end = node_connection_point(tgt, diagram, src_center)

    path = compute_path(start, end, edge.line_style, edge.direction, arrow_size=arrow_size)
    color = edge.color or "#495057"

    points = path.sample_points(60)
    xy = [(p.x, p.y) for p in points]

    if len(xy) >= 2:
        draw.line(xy, fill=color, width=line_width)

    if path.arrow:
        a = path.arrow
        draw.polygon(
            [(a.tip.x, a.tip.y), (a.left.x, a.left.y), (a.right.x, a.right.y)],
            fill=color,
        )

    if edge.direction == Direction.BOTH:
        reverse_path = compute_path(end, start, edge.line_style, Direction.FORWARD, arrow_size=arrow_size)
        if reverse_path.arrow:
            a = reverse_path.arrow
            draw.polygon(
                [(a.tip.x, a.tip.y), (a.left.x, a.left.y), (a.right.x, a.right.y)],
                fill=color,
            )

    if edge.label:
        mid_x = (start.x + end.x) / 2
        mid_y = (start.y + end.y) / 2
        draw.text(
            (mid_x, mid_y - 14 * scale),
            edge.label,
            fill="#6C757D",
            font=font,
            anchor="mm",
        )


def _render_node_png(canvas, draw, node, diagram, font, icon_size):
    icon_rect = node_icon_rect(node, diagram)
    label_pos = node_label_position(node, diagram)

    icon_img = load_icon_image(node.icon, size=icon_size)
    canvas.paste(icon_img, (int(icon_rect.x), int(icon_rect.y)), mask=icon_img)

    draw.text(
        (label_pos.x, label_pos.y),
        node.label,
        fill="#2D3436",
        font=font,
        anchor="mm",
    )
