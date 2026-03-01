# Mermaid Import

diagrams-for-ai can parse annotated Mermaid flowchart text and produce the same rich output (SVG/PNG with icons, clusters, and styled connections).

The key idea: embed grid positions and icon keys as Mermaid comments (`%% ...`). Standard Mermaid renderers ignore these comments, so the same `.mmd` file works everywhere — GitHub previews, documentation sites, IDE plugins — **and** can be converted to a full diagrams-for-ai diagram.

## Quick start

```python
from diagrams_for_ai import Diagram

d = Diagram.from_mermaid("""\
    %% @config name="Hello" rows=2 cols=2
    graph TD
        %% @node A pos=0,0 icon=aws/compute/ec2
        %% @node B pos=1,1 icon=aws/database/rds
        A[Service A] --> B[Service B]
""", outformat="png", show=False)

d.render()
```

Or load from a file:

```python
d = Diagram.from_mermaid_file("docs/examples/aws_web_service.mmd", show=False)
d.render()
```

## Annotation syntax

All annotations use Mermaid comment lines (`%%`) so they are invisible to standard renderers.

### `@config` — diagram settings

Place at the top of the file, before the `graph` declaration.

```
%% @config name="AWS Web Service" rows=5 cols=7 cell_size=180 padding=60 bg=#FFFFFF
```

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `name` | `str` | `""` | Diagram title. |
| `filename` | `str` | slugified name | Output filename (without extension). |
| `rows` | `int` | auto-computed | Grid rows. If omitted, derived from node positions. |
| `cols` | `int` | auto-computed | Grid columns. If omitted, derived from node positions. |
| `cell_size` | `int` | `180` | Pixel size of each grid cell. |
| `padding` | `int` | `60` | Pixel padding around the canvas. |
| `icon_size` | `int` | `64` | Base icon size in pixels. |
| `scale` | `int` | `1` | Uniform scale multiplier for hi-res output (e.g. `scale=2` doubles all dimensions). |
| `bg` | `str` | `"#FFFFFF"` | Canvas background color (hex). |

**Hi-res example:**

```
%% @config name="Hi-Res Diagram" rows=3 cols=3 cell_size=180 scale=2
```

### `@node` — node positions and icons

One annotation per node. The `<id>` must match the node ID used in Mermaid edges.

```
%% @node <id> pos=<row>,<col> [icon=<icon_key>]
```

| Key | Required | Description |
|-----|----------|-------------|
| `pos` | yes | Grid position as `row,col` (0-indexed). |
| `icon` | no | Icon key, e.g. `aws/compute/ec2`. Defaults to empty (no icon). |

### `@cluster` — subgraph grid mapping

Place immediately inside a `subgraph` block (first line after `subgraph ... [Label]`).

```
subgraph vpc [VPC]
    %% @cluster pos=0,0 size=4,2 bg=#E8F4FD border=#B0C4DE
    ...
end
```

| Key | Required | Default | Description |
|-----|----------|---------|-------------|
| `pos` | yes | — | Top-left grid position as `row,col`. |
| `size` | yes | — | Span as `width,height` in grid cells. |
| `bg` | no | `"#E8F4FD"` | Background fill color (hex). |
| `border` | no | `"#B0C4DE"` | Border stroke color (hex). |

## Supported Mermaid syntax

### Graph header

```
graph TD
flowchart LR
```

Directions `TD`, `TB`, `LR`, `RL`, and `BT` are accepted (the direction is parsed but layout is determined by `@node pos` annotations).

### Node shapes

| Syntax | Shape |
|--------|-------|
| `A[Label]` | Rectangle |
| `A(Label)` | Rounded |
| `A{Label}` | Diamond |
| `A((Label))` | Circle |

### Edge types

| Syntax | Direction | Style |
|--------|-----------|-------|
| `A --> B` | Forward arrow | solid |
| `A --- B` | No arrow | solid |
| `A -.-> B` | Forward arrow | dashed |
| `A ==> B` | Forward arrow | bold |
| `A <--> B` | Bidirectional | solid |
| `A -->\|label\| B` | Forward + label | solid |
| `A -- label --> B` | Forward + label | solid |

Chained edges are supported: `A --> B --> C` creates two edges.

### Subgraphs

Map to diagrams-for-ai clusters when paired with a `@cluster` annotation.

```
subgraph id [Label]
    %% @cluster pos=... size=...
    ...
end
```

## Limitations

- Only `graph` / `flowchart` diagrams are supported (no sequence, class, or other types).
- `classDef`, `style`, `click`, and `linkStyle` are not parsed.
- Semicolon-separated statements on one line are supported, but mixing with annotations on the same line is not.

## Full example

See [docs/examples/aws_web_service.mmd](examples/aws_web_service.mmd) for a complete annotated Mermaid file that produces the same diagram as the [Python API example](examples/aws_web_service.py).
