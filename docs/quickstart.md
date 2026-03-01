# Quick Start

## Installation

```bash
uv add diagrams-for-ai
```

Or with pip:

```bash
pip install diagrams-for-ai
```

## Your first diagram

Create a file called `my_diagram.py`:

```python
from diagrams_for_ai import Diagram, Node

with Diagram("My First Diagram", rows=2, cols=3, outformat="png", show=False):
    web = Node("Web Server", icon="aws/compute/ec2", row=0, col=1)
    db = Node("Database", icon="aws/database/rds", row=1, col=1)
    web >> db
```

Run it:

```bash
uv run python my_diagram.py
```

This generates `my_first_diagram.png` with an EC2 icon connected to an RDS icon by a curved arrow.

## A complete example

Here's a full AWS architecture with clusters, multiple connection styles, and edge labels:

```python
from diagrams_for_ai import Cluster, Diagram, Edge, LineStyle, Node

with Diagram(
    "AWS Web Service",
    rows=5,
    cols=7,
    cell_size=180,
    outformat=["svg", "png"],
    show=False,
):

    with Cluster(
        "Public Subnet",
        row=0, col=1, width=5, height=2,
        bg_color="#FFF3E0", border_color="#FFB74D",
    ):
        users = Node("Users", icon="aws/general/users", row=0, col=3)
        dns = Node("Route 53", icon="aws/network/route-53", row=1, col=1)
        cdn = Node("CloudFront", icon="aws/network/cloudfront", row=1, col=3)
        waf = Node("WAF", icon="aws/security/waf", row=1, col=5)

    with Cluster(
        "Private Subnet",
        row=2, col=0, width=7, height=3,
        bg_color="#E8F5E9", border_color="#81C784",
    ):
        lb = Node("ALB", icon="aws/network/elastic-load-balancing", row=2, col=3)
        web1 = Node("Web Server 1", icon="aws/compute/ec2", row=3, col=1)
        web2 = Node("Web Server 2", icon="aws/compute/ec2", row=3, col=3)
        web3 = Node("Web Server 3", icon="aws/compute/ec2", row=3, col=5)
        db = Node("Aurora DB", icon="aws/database/aurora", row=4, col=2)
        cache = Node("ElastiCache", icon="aws/database/elasticache", row=4, col=4)

    users >> dns
    users >> cdn
    cdn >> waf >> lb

    lb >> [web1, web2, web3]

    web1 >> db
    web2 >> db
    web3 >> Edge(label="sessions", style="dashed", line_style=LineStyle.ORTHO) >> cache

    web1 >> Edge(color="#E74C3C", line_style=LineStyle.STRAIGHT) >> cache
```

This produces both `aws_web_service.svg` and `aws_web_service.png`.

!!! tip
    You can find this example at `docs/examples/aws_web_service.py` in the repository.

## Key concepts

| Concept | Description |
|---------|-------------|
| `Diagram` | Top-level context manager. Defines the grid size and output format. |
| `Node` | A positioned element with an icon and label, placed at `(row, col)`. |
| `Edge` | Customizes a connection: label, color, dash style, line style. |
| `Cluster` | Visual grouping that spans a grid region. |
| `>>` | Connect nodes with a forward arrow. |
| `<<` | Connect nodes with a reverse arrow. |
| `-` | Connect nodes without arrows (undirected). |
