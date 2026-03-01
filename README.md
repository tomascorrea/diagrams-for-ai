# diagrams-for-ai

[![CI](https://github.com/tomascorrea/diagrams-for-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/tomascorrea/diagrams-for-ai/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/diagrams-for-ai)](https://pypi.org/project/diagrams-for-ai/)

**AI-friendly architecture diagrams with grid-based positioning.**

diagrams-for-ai is a Python library that renders beautiful cloud architecture diagrams without Graphviz. Nodes are placed on a simple grid using `row` and `col` coordinates, making it trivial for an AI to generate diagrams programmatically.

## Why diagrams-for-ai?

- **Grid-based positioning** -- Place nodes with `row` and `col`. No fighting with Graphviz layout.
- **AI-friendly** -- Explicit coordinates are easy for language models to produce and reason about.
- **Real icons** -- Leverages the [diagrams](https://diagrams.mingrammer.com/) package for hundreds of icons across AWS, GCP, Azure, Kubernetes, and more.
- **Beautiful connections** -- Four line styles: curved (bezier), straight, orthogonal, and step.
- **SVG & PNG output** -- Portable SVG with embedded icons, or raster PNG via Pillow.
- **Familiar syntax** -- Use `>>`, `<<`, and `-` operators to connect nodes, just like the original `diagrams` library.

## Installation

```bash
uv add diagrams-for-ai
```

Or with pip:

```bash
pip install diagrams-for-ai
```

> The `diagrams` package (which provides the icons) is installed automatically as a dependency.

## Quick example

```python
from diagrams_for_ai import Diagram, Node

with Diagram("Hello", rows=2, cols=2, outformat="png", show=False):
    a = Node("Service A", icon="aws/compute/ec2", row=0, col=0)
    b = Node("Service B", icon="aws/database/rds", row=1, col=1)
    a >> b
```

## Full example

```python
from diagrams_for_ai import Cluster, Diagram, Edge, LineStyle, Node

with Diagram("AWS Web Service", rows=5, cols=7, outformat=["svg", "png"], show=False):

    with Cluster("Public Subnet", row=0, col=1, width=5, height=2,
                 bg_color="#FFF3E0", border_color="#FFB74D"):
        users = Node("Users", icon="aws/general/users", row=0, col=3)
        cdn = Node("CloudFront", icon="aws/network/cloudfront", row=1, col=3)

    with Cluster("Private Subnet", row=2, col=0, width=7, height=3,
                 bg_color="#E8F5E9", border_color="#81C784"):
        lb = Node("ALB", icon="aws/network/elastic-load-balancing", row=2, col=3)
        web1 = Node("Web 1", icon="aws/compute/ec2", row=3, col=1)
        web2 = Node("Web 2", icon="aws/compute/ec2", row=3, col=5)
        db = Node("Aurora", icon="aws/database/aurora", row=4, col=3)

    users >> cdn >> lb
    lb >> [web1, web2]
    web1 >> db
    web2 >> Edge(style="dashed", line_style=LineStyle.ORTHO) >> db
```

## Features

### Connection styles

| Style | Usage | Description |
|-------|-------|-------------|
| Curved | `a >> b` | Smooth bezier curves (default) |
| Straight | `a >> Edge(line_style=LineStyle.STRAIGHT) >> b` | Direct lines |
| Orthogonal | `a >> Edge(line_style=LineStyle.ORTHO) >> b` | Right-angle routing |
| Step | `a >> Edge(line_style=LineStyle.STEP) >> b` | Horizontal-then-vertical |

### Edge customization

```python
a >> Edge(label="HTTPS", color="#2ECC71", style="dashed") >> b
```

### Clusters

```python
with Cluster("VPC", row=0, col=0, width=4, height=3,
             bg_color="#E8F4FD", border_color="#B0C4DE"):
    # nodes inside the cluster
    ...
```

### Icon providers

AWS, GCP, Azure, Kubernetes, on-premises, and [13 more providers](https://diagrams.mingrammer.com/docs/nodes/aws) -- all from the `diagrams` package.

```python
Node("Server", icon="aws/compute/ec2", row=0, col=0)
Node("Pod", icon="k8s/compute/pod", row=0, col=1)
Node("Postgres", icon="onprem/database/postgresql", row=0, col=2)
```

## Development

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Serve docs locally
uv run mkdocs serve
```

## License

MIT -- see [LICENSE](LICENSE) for details.
