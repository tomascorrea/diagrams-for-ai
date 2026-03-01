# Connection Styles

diagrams_for_ai supports four line styles for connections between nodes. Each style can be combined with dash patterns (solid, dashed, dotted) and custom colors.

## LineStyle.CURVED (default)

Smooth cubic bezier curves that flow naturally between nodes. The control points are computed automatically based on the relative position of the source and target.

```python
from diagrams_for_ai import Diagram, Edge, LineStyle, Node

with Diagram("Curved", rows=2, cols=3, outformat="png", show=False):
    a = Node("Service A", icon="aws/compute/ec2", row=0, col=0)
    b = Node("Service B", icon="aws/compute/ec2", row=1, col=2)
    a >> b  # curved is the default
```

Best for: general-purpose connections, especially diagonal ones.

## LineStyle.STRAIGHT

Direct straight lines from source to target.

```python
with Diagram("Straight", rows=2, cols=3, outformat="png", show=False):
    a = Node("Service A", icon="aws/compute/ec2", row=0, col=0)
    b = Node("Service B", icon="aws/compute/ec2", row=1, col=2)
    a >> Edge(line_style=LineStyle.STRAIGHT) >> b
```

Best for: short connections between nearby nodes or when you want a clean, minimal look.

## LineStyle.ORTHO

Orthogonal (Manhattan) routing with right-angle turns. The path goes horizontally to the midpoint, then vertically, then horizontally again.

```python
with Diagram("Ortho", rows=2, cols=3, outformat="png", show=False):
    a = Node("Service A", icon="aws/compute/ec2", row=0, col=0)
    b = Node("Service B", icon="aws/compute/ec2", row=1, col=2)
    a >> Edge(line_style=LineStyle.ORTHO) >> b
```

Best for: technical diagrams where you want clean right-angle routing.

## LineStyle.STEP

Step function routing: goes horizontally first to the target's column, then drops vertically to the target.

```python
with Diagram("Step", rows=2, cols=3, outformat="png", show=False):
    a = Node("Service A", icon="aws/compute/ec2", row=0, col=0)
    b = Node("Service B", icon="aws/compute/ec2", row=1, col=2)
    a >> Edge(line_style=LineStyle.STEP) >> b
```

Best for: hierarchical flows where you want to emphasize the horizontal-then-vertical progression.

## Dash styles

Any line style can be combined with a dash pattern:

```python
# Solid line (default)
a >> b

# Dashed line
a >> Edge(style="dashed") >> b

# Dotted line
a >> Edge(style="dotted") >> b
```

## Custom colors

Override the default gray with any hex color:

```python
a >> Edge(color="#E74C3C") >> b   # red
a >> Edge(color="#2ECC71") >> b   # green
a >> Edge(color="#3498DB") >> b   # blue
```

## Edge labels

Add text labels to any connection:

```python
a >> Edge(label="HTTPS") >> b
a >> Edge(label="gRPC", style="dashed", color="#9B59B6") >> b
```

The label is rendered at the midpoint of the connection.

## Combining everything

```python
from diagrams_for_ai import Diagram, Edge, LineStyle, Node

with Diagram("All Styles", rows=3, cols=4, outformat="png", show=False):
    a = Node("A", icon="aws/compute/ec2", row=0, col=0)
    b = Node("B", icon="aws/compute/ec2", row=0, col=3)
    c = Node("C", icon="aws/compute/ec2", row=2, col=0)
    d = Node("D", icon="aws/compute/ec2", row=2, col=3)

    a >> b                                                           # curved, solid
    a >> Edge(line_style=LineStyle.STRAIGHT, color="#E74C3C") >> c   # straight, red
    b >> Edge(line_style=LineStyle.ORTHO, style="dashed") >> d       # ortho, dashed
    c >> Edge(line_style=LineStyle.STEP, label="async") >> d         # step, labeled
```
