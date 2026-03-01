import math
from dataclasses import dataclass

from diagrams_for_ai.layout import Point
from diagrams_for_ai.model import Direction, LineStyle


@dataclass(frozen=True)
class ArrowHead:
    tip: Point
    left: Point
    right: Point


@dataclass
class ConnectionPath:
    """Describes a visual path between two nodes."""

    start: Point
    end: Point
    line_style: LineStyle
    direction: Direction

    control_points: list[Point]
    segments: list[Point]
    arrow: ArrowHead | None

    @property
    def svg_path(self) -> str:
        """Return an SVG path data string for this connection."""
        if self.segments:
            return self._svg_polyline()
        if self.line_style == LineStyle.CURVED:
            return self._svg_cubic_bezier()
        return self._svg_straight()

    def _svg_straight(self) -> str:
        return f"M {self.start.x:.1f} {self.start.y:.1f} L {self.end.x:.1f} {self.end.y:.1f}"

    def _svg_cubic_bezier(self) -> str:
        if len(self.control_points) >= 2:
            cp1, cp2 = self.control_points[0], self.control_points[1]
            return (
                f"M {self.start.x:.1f} {self.start.y:.1f} "
                f"C {cp1.x:.1f} {cp1.y:.1f}, "
                f"{cp2.x:.1f} {cp2.y:.1f}, "
                f"{self.end.x:.1f} {self.end.y:.1f}"
            )
        return self._svg_straight()

    def _svg_polyline(self) -> str:
        parts = [f"M {self.start.x:.1f} {self.start.y:.1f}"]
        for pt in self.segments:
            parts.append(f"L {pt.x:.1f} {pt.y:.1f}")
        parts.append(f"L {self.end.x:.1f} {self.end.y:.1f}")
        return " ".join(parts)

    def sample_points(self, num_points: int = 50) -> list[Point]:
        """Sample points along the path for raster rendering."""
        if self.segments:
            return [self.start] + self.segments + [self.end]
        if self.line_style == LineStyle.CURVED and len(self.control_points) >= 2:
            return _sample_cubic_bezier(
                self.start,
                self.control_points[0],
                self.control_points[1],
                self.end,
                num_points,
            )
        return [self.start, self.end]


def compute_path(
    start: Point,
    end: Point,
    line_style: LineStyle,
    direction: Direction,
    *,
    arrow_size: float = 10.0,
    via_points: list[Point] | None = None,
) -> ConnectionPath:
    """Compute a connection path between two points."""
    if via_points:
        control_points: list[Point] = []
        segments = list(via_points)
        effective_style = LineStyle.STRAIGHT
    else:
        builders = {
            LineStyle.STRAIGHT: _build_straight,
            LineStyle.CURVED: _build_curved,
            LineStyle.ORTHO: _build_ortho,
            LineStyle.STEP: _build_step,
        }
        builder = builders[line_style]
        control_points, segments = builder(start, end)
        effective_style = line_style

    arrow = None
    if direction in (Direction.FORWARD, Direction.BOTH):
        arrow = _compute_arrowhead(
            start, end, control_points, segments, effective_style, size=arrow_size
        )

    return ConnectionPath(
        start=start,
        end=end,
        line_style=effective_style,
        direction=direction,
        control_points=control_points,
        segments=segments,
        arrow=arrow,
    )


def _build_straight(start: Point, end: Point) -> tuple[list[Point], list[Point]]:
    return [], []


def _build_curved(start: Point, end: Point) -> tuple[list[Point], list[Point]]:
    dx = end.x - start.x
    dy = end.y - start.y

    tension = 0.4
    if abs(dy) > abs(dx):
        cp1 = Point(start.x, start.y + dy * tension)
        cp2 = Point(end.x, end.y - dy * tension)
    else:
        cp1 = Point(start.x + dx * tension, start.y)
        cp2 = Point(end.x - dx * tension, end.y)

    return [cp1, cp2], []


def _build_ortho(start: Point, end: Point) -> tuple[list[Point], list[Point]]:
    """Manhattan routing: horizontal, then vertical, then horizontal."""
    mid_x = (start.x + end.x) / 2
    segments = [
        Point(mid_x, start.y),
        Point(mid_x, end.y),
    ]
    return [], segments


def _build_step(start: Point, end: Point) -> tuple[list[Point], list[Point]]:
    """Step routing: go horizontal first, then vertical."""
    segments = [Point(end.x, start.y)]
    return [], segments


def _compute_arrowhead(
    start: Point,
    end: Point,
    control_points: list[Point],
    segments: list[Point],
    line_style: LineStyle,
    size: float = 10.0,
    angle_deg: float = 25.0,
) -> ArrowHead:
    """Compute arrowhead triangle at the end of the path."""
    if segments:
        prev = segments[-1]
    elif control_points:
        prev = control_points[-1]
    else:
        prev = start

    dx = end.x - prev.x
    dy = end.y - prev.y
    length = math.hypot(dx, dy)
    if length < 0.001:
        dx, dy = 0, -1
        length = 1

    ux, uy = dx / length, dy / length
    angle = math.radians(angle_deg)

    left = Point(
        end.x - size * (ux * math.cos(angle) - uy * math.sin(angle)),
        end.y - size * (uy * math.cos(angle) + ux * math.sin(angle)),
    )
    right = Point(
        end.x - size * (ux * math.cos(angle) + uy * math.sin(angle)),
        end.y - size * (uy * math.cos(angle) - ux * math.sin(angle)),
    )

    return ArrowHead(tip=end, left=left, right=right)


def _sample_cubic_bezier(
    p0: Point, p1: Point, p2: Point, p3: Point, n: int
) -> list[Point]:
    """Sample n points along a cubic bezier curve."""
    points = []
    for i in range(n + 1):
        t = i / n
        t2 = t * t
        t3 = t2 * t
        mt = 1 - t
        mt2 = mt * mt
        mt3 = mt2 * mt

        x = mt3 * p0.x + 3 * mt2 * t * p1.x + 3 * mt * t2 * p2.x + t3 * p3.x
        y = mt3 * p0.y + 3 * mt2 * t * p1.y + 3 * mt * t2 * p2.y + t3 * p3.y
        points.append(Point(x, y))
    return points
