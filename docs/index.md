# diagrams_for_ai

**AI-friendly architecture diagrams with grid-based positioning.**

diagrams_for_ai is a Python library that renders beautiful cloud architecture diagrams without Graphviz. Instead of relying on automatic layout algorithms, nodes are placed on a simple grid using `row` and `col` coordinates -- making it trivial for an AI to generate diagrams programmatically.

## Why diagrams_for_ai?

- **Grid-based positioning** -- Place nodes with `row` and `col`. No fighting with Graphviz layout.
- **AI-friendly** -- Explicit coordinates are easy for language models to produce and reason about.
- **Real icons** -- Leverages the `diagrams` package for hundreds of icons across AWS, GCP, Azure, Kubernetes, and more.
- **Beautiful connections** -- Four line styles: curved (bezier), straight, orthogonal, and step.
- **SVG & PNG output** -- Portable SVG with embedded icons, or raster PNG via Pillow.
- **Familiar syntax** -- Use `>>`, `<<`, and `-` operators to connect nodes, just like the original `diagrams` library.

## Quick example

```python
from diagrams_for_ai import Diagram, Node

with Diagram("Hello", rows=2, cols=2, show=False):
    a = Node("Service A", icon="aws/compute/ec2", row=0, col=0)
    b = Node("Service B", icon="aws/database/rds", row=1, col=1)
    a >> b
```

This produces an SVG/PNG diagram with the EC2 icon at grid position (0, 0) connected to the RDS icon at (1, 1) with a curved arrow.

## Installation

```bash
uv add diagrams-for-ai
```

Or with pip:

```bash
pip install diagrams-for-ai
```

!!! note
    The `diagrams` package (which provides the icons) will be installed automatically as a dependency.
