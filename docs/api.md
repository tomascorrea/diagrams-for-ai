# API Reference

## Diagram

The top-level context manager that collects nodes, edges, and clusters, then renders on exit.

```python
from diagrams_for_ai import Diagram

with Diagram(
    name="My Architecture",
    filename="my_arch",        # output filename without extension
    rows=4,                    # grid rows
    cols=6,                    # grid columns
    cell_size=180,             # pixel size of each grid cell
    padding=60,                # pixel padding around the canvas
    icon_size=64,              # base icon size in pixels
    scale=1,                   # uniform scale multiplier for hi-res output
    outformat="png",           # "png", "svg", "jpg", or a list like ["svg", "png"]
    show=True,                 # open the file after rendering
    bg_color="#FFFFFF",        # canvas background color
):
    ...
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | `""` | Diagram title, displayed at the top. Also used for the filename if `filename` is not set. |
| `filename` | `str` | `""` | Output filename (without extension). Defaults to a slugified version of `name`. |
| `rows` | `int` | `4` | Number of rows in the grid. |
| `cols` | `int` | `6` | Number of columns in the grid. |
| `cell_size` | `int` | `180` | Pixel size of each grid cell. |
| `padding` | `int` | `60` | Pixel padding around the entire canvas. |
| `icon_size` | `int` | `64` | Base icon size in pixels. Useful for diagrams that benefit from larger or smaller icons. |
| `scale` | `int` | `1` | Uniform scale multiplier. Multiplies all pixel dimensions (cell size, padding, icon size, label height, line widths, font sizes) to produce a higher-resolution output. For example, `scale=2` doubles the output dimensions while keeping the diagram visually identical -- ideal for PDF embedding or retina displays. |
| `outformat` | `str \| list[str]` | `"png"` | Output format(s). Supported: `"png"`, `"svg"`, `"jpg"`. |
| `show` | `bool` | `True` | Whether to open the rendered file in the system viewer. |
| `bg_color` | `str` | `"#FFFFFF"` | Canvas background color (hex). |

### Hi-res example

```python
with Diagram("Hi-Res", rows=2, cols=2, scale=2, outformat="png", show=False):
    a = Node("Service A", icon="aws/compute/ec2", row=0, col=0)
    b = Node("Service B", icon="aws/database/rds", row=1, col=1)
    a >> b
```

This produces a PNG that is 2x larger in pixel dimensions, with all icons, text, and lines scaled proportionally -- sharp when embedded in PDFs or displayed on retina screens.

### `Diagram.from_mermaid(text, *, outformat, show, filename)`

Create a `Diagram` by parsing annotated Mermaid flowchart text. Returns a `Diagram` instance — call `.render()` to produce output files.

```python
d = Diagram.from_mermaid("""\
    %% @config name="My Arch" rows=3 cols=4
    graph TD
        %% @node A pos=0,0 icon=aws/compute/ec2
        %% @node B pos=1,1 icon=aws/database/rds
        A[EC2] --> B[RDS]
""", outformat="svg", show=False)

d.render()
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `text` | `str` | — | Annotated Mermaid flowchart text. |
| `outformat` | `str \| list[str]` | `"png"` | Output format(s). |
| `show` | `bool` | `True` | Whether to open the file after rendering. |
| `filename` | `str` | `""` | Override the output filename. |

### `Diagram.from_mermaid_file(path, *, outformat, show, filename)`

Same as `from_mermaid`, but reads the Mermaid text from a `.mmd` file.

```python
d = Diagram.from_mermaid_file("architecture.mmd", show=False)
d.render()
```

See [Mermaid Import](mermaid-import.md) for the full annotation syntax reference.

---

## Node

A positioned element with an icon and a label.

```python
from diagrams_for_ai import Node

web = Node("Web Server", icon="aws/compute/ec2", row=0, col=2)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `label` | `str` | `""` | Text label displayed below the icon. |
| `icon` | `str` | `""` | Icon key, e.g. `"aws/compute/ec2"`. See [Available Icons](icons.md). |
| `row` | `int` | `0` | Grid row position (0-indexed from top). |
| `col` | `int` | `0` | Grid column position (0-indexed from left). |

### Connection operators

| Operator | Example | Description |
|----------|---------|-------------|
| `>>` | `a >> b` | Forward arrow from `a` to `b`. |
| `<<` | `a << b` | Reverse arrow (arrow points from `b` to `a`). |
| `-` | `a - b` | Undirected connection (no arrows). |

You can also connect to multiple nodes at once:

```python
lb >> [web1, web2, web3]
```

---

## Edge

Customizes a connection between two nodes. Insert an `Edge` between two `>>` or `<<` operators.

```python
from diagrams_for_ai import Edge, LineStyle

node1 >> Edge(label="HTTPS", color="#2ECC71", style="dashed", line_style=LineStyle.ORTHO) >> node2
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `label` | `str` | `""` | Text label displayed on the connection. |
| `color` | `str` | `""` | Line color (hex). Defaults to `"#495057"` if empty. |
| `style` | `str` | `""` | Line dash style: `""` (solid), `"dashed"`, or `"dotted"`. |
| `line_style` | `LineStyle` | `LineStyle.CURVED` | Path shape. See [Connection Styles](connection-styles.md). |
| `via` | `list[tuple[int, int]]` | `[]` | Waypoint grid positions `(row, col)` for the connection to pass through. Creates a polyline with corners at each waypoint. |

### Waypoint routing

Use `via` to route a connection through intermediate grid cells, creating as many corners as needed:

```python
a >> Edge(via=[(0, 2), (2, 2)]) >> b
```

This routes the connection from `a` through grid cell `(0, 2)`, then `(2, 2)`, and finally to `b`. The source node exits toward the first waypoint, and the target is approached from the last waypoint.

```python
# L-shaped route: go right, then down
a >> Edge(via=[(0, 3)]) >> b

# U-shaped route around an obstacle
a >> Edge(via=[(0, 4), (2, 4), (2, 0)]) >> b
```

---

## Cluster

A visual grouping that spans a region of the grid. Used as a context manager.

```python
from diagrams_for_ai import Cluster

with Cluster(
    "VPC",
    row=1, col=0,
    width=4, height=2,
    bg_color="#E8F4FD",
    border_color="#B0C4DE",
):
    # nodes created here are visually inside the cluster
    ...
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `label` | `str` | `""` | Cluster title, displayed in the top-left corner. |
| `row` | `int` | `0` | Top-left grid row of the cluster. |
| `col` | `int` | `0` | Top-left grid column of the cluster. |
| `width` | `int` | `2` | Number of grid columns the cluster spans. |
| `height` | `int` | `2` | Number of grid rows the cluster spans. |
| `bg_color` | `str` | `"#E8F4FD"` | Background fill color (hex). |
| `border_color` | `str` | `"#B0C4DE"` | Border stroke color (hex). |

Clusters can be nested:

```python
with Cluster("VPC", row=0, col=0, width=6, height=4):
    with Cluster("Private Subnet", row=1, col=0, width=3, height=2):
        ...
    with Cluster("Public Subnet", row=1, col=3, width=3, height=2):
        ...
```

---

## LineStyle

An enum that controls how connections are drawn between nodes.

```python
from diagrams_for_ai import LineStyle
```

| Value | Description |
|-------|-------------|
| `LineStyle.CURVED` | Smooth cubic bezier curve (default). |
| `LineStyle.STRAIGHT` | Direct straight line. |
| `LineStyle.ORTHO` | Orthogonal routing with right-angle turns. |
| `LineStyle.STEP` | Step function: horizontal first, then vertical. |

See [Connection Styles](connection-styles.md) for visual examples.
