from diagrams_for_ai.layout import Point
from diagrams_for_ai.model import Direction, LineStyle
from diagrams_for_ai.paths import compute_path


def test_straight_svg_path():
    path = compute_path(Point(0, 0), Point(100, 100), LineStyle.STRAIGHT, Direction.FORWARD)
    assert path.svg_path.startswith("M ")
    assert "L " in path.svg_path


def test_straight_sample_points():
    path = compute_path(Point(10, 20), Point(90, 80), LineStyle.STRAIGHT, Direction.NONE)
    points = path.sample_points()
    assert len(points) == 2
    assert points[0] == Point(10, 20)
    assert points[1] == Point(90, 80)


def test_curved_has_control_points():
    path = compute_path(Point(0, 0), Point(100, 200), LineStyle.CURVED, Direction.FORWARD)
    assert len(path.control_points) == 2


def test_curved_svg_contains_bezier():
    path = compute_path(Point(0, 0), Point(100, 200), LineStyle.CURVED, Direction.FORWARD)
    assert "C " in path.svg_path


def test_curved_sample_points_smooth():
    path = compute_path(Point(0, 0), Point(300, 300), LineStyle.CURVED, Direction.FORWARD)
    points = path.sample_points(20)
    assert len(points) == 21
    assert abs(points[0].x) < 0.01
    assert abs(points[-1].x - 300) < 0.01


def test_ortho_has_segments():
    path = compute_path(Point(0, 0), Point(200, 100), LineStyle.ORTHO, Direction.FORWARD)
    assert len(path.segments) == 2


def test_ortho_segments_axis_aligned():
    path = compute_path(Point(0, 0), Point(200, 100), LineStyle.ORTHO, Direction.FORWARD)
    mid_x = 100.0
    assert abs(path.segments[0].x - mid_x) < 0.01
    assert abs(path.segments[0].y - 0) < 0.01
    assert abs(path.segments[1].x - mid_x) < 0.01
    assert abs(path.segments[1].y - 100) < 0.01


def test_step_has_one_segment():
    path = compute_path(Point(0, 0), Point(200, 100), LineStyle.STEP, Direction.FORWARD)
    assert len(path.segments) == 1


def test_step_goes_horizontal_first():
    path = compute_path(Point(0, 0), Point(200, 100), LineStyle.STEP, Direction.FORWARD)
    assert abs(path.segments[0].x - 200) < 0.01
    assert abs(path.segments[0].y - 0) < 0.01


def test_forward_has_arrow():
    path = compute_path(Point(0, 0), Point(100, 0), LineStyle.STRAIGHT, Direction.FORWARD)
    assert path.arrow is not None
    assert abs(path.arrow.tip.x - 100) < 0.01


def test_none_direction_no_arrow():
    path = compute_path(Point(0, 0), Point(100, 0), LineStyle.STRAIGHT, Direction.NONE)
    assert path.arrow is None


def test_arrow_triangle_shape():
    path = compute_path(Point(0, 0), Point(100, 0), LineStyle.STRAIGHT, Direction.FORWARD)
    a = path.arrow
    assert a.left.x < a.tip.x
    assert a.right.x < a.tip.x
    assert a.left.y != a.right.y
