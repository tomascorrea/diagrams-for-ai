# Clusters

Clusters are visual groupings that draw a labeled, rounded rectangle behind a region of the grid. They help organize your diagram into logical sections like VPCs, subnets, or service groups.

## Basic usage

Create a cluster with a context manager. Any nodes created inside the `with` block are visually associated with that cluster.

```python
from diagrams_for_ai import Cluster, Diagram, Node

with Diagram("Cluster Example", rows=3, cols=3, outformat="png", show=False):
    with Cluster("Backend", row=0, col=0, width=3, height=2):
        api = Node("API", icon="aws/compute/ec2", row=0, col=1)
        db = Node("Database", icon="aws/database/rds", row=1, col=1)
        api >> db
```

## Positioning and sizing

Clusters are positioned on the same grid as nodes. You specify the top-left corner (`row`, `col`) and the span (`width` in columns, `height` in rows).

```python
with Cluster("My Group", row=1, col=2, width=4, height=3):
    ...
```

This creates a rectangle starting at grid cell (1, 2) and spanning 4 columns by 3 rows.

!!! tip
    Make sure your cluster region is large enough to contain all the nodes you place inside it. The cluster background is drawn based on the grid coordinates, not the node positions.

## Custom colors

Customize the background and border colors with hex values:

```python
with Cluster(
    "Public Subnet",
    row=0, col=0, width=4, height=2,
    bg_color="#FFF3E0",
    border_color="#FFB74D",
):
    ...
```

The defaults are a light blue background (`#E8F4FD`) with a steel-blue border (`#B0C4DE`).

Some useful color combinations:

| Purpose | `bg_color` | `border_color` |
|---------|-----------|----------------|
| Blue (default) | `#E8F4FD` | `#B0C4DE` |
| Green (private) | `#E8F5E9` | `#81C784` |
| Orange (public) | `#FFF3E0` | `#FFB74D` |
| Red (danger zone) | `#FFEBEE` | `#E57373` |
| Purple (services) | `#F3E5F5` | `#BA68C8` |
| Gray (neutral) | `#F5F5F5` | `#BDBDBD` |

## Nesting clusters

Clusters can be nested to represent hierarchies like VPC > Subnet > Service Group:

```python
from diagrams_for_ai import Cluster, Diagram, Node

with Diagram("Nested Clusters", rows=4, cols=6, outformat="png", show=False):
    with Cluster("VPC", row=0, col=0, width=6, height=4, bg_color="#F5F5F5", border_color="#BDBDBD"):
        with Cluster("Public Subnet", row=0, col=0, width=3, height=4, bg_color="#FFF3E0", border_color="#FFB74D"):
            lb = Node("ALB", icon="aws/network/elastic-load-balancing", row=1, col=1)

        with Cluster("Private Subnet", row=0, col=3, width=3, height=4, bg_color="#E8F5E9", border_color="#81C784"):
            app = Node("App", icon="aws/compute/ec2", row=1, col=4)
            db = Node("Database", icon="aws/database/rds", row=2, col=4)

        lb >> app >> db
```

!!! note
    Nested clusters are rendered in the order they are created. The outermost cluster is drawn first (behind), and inner clusters are drawn on top.

## Connections across clusters

Nodes in different clusters can be connected normally. Connections are always drawn on top of cluster backgrounds.

```python
with Diagram("Cross-Cluster", rows=2, cols=4, outformat="png", show=False):
    with Cluster("Frontend", row=0, col=0, width=2, height=2, bg_color="#E3F2FD", border_color="#64B5F6"):
        web = Node("Web", icon="aws/compute/ec2", row=0, col=0)

    with Cluster("Backend", row=0, col=2, width=2, height=2, bg_color="#E8F5E9", border_color="#81C784"):
        api = Node("API", icon="aws/compute/ec2", row=0, col=2)
        db = Node("DB", icon="aws/database/rds", row=1, col=3)

    web >> api >> db
```
