"""Tests for the Mermaid flowchart parser."""

import os
import textwrap

import pytest

from diagrams_for_ai import Diagram
from diagrams_for_ai.ext.mermaid import parse_mermaid
from diagrams_for_ai.model import Direction


# ---------------------------------------------------------------------------
# Minimal graphs
# ---------------------------------------------------------------------------


def test_minimal_two_nodes_one_edge():
    model = parse_mermaid(textwrap.dedent("""\
        graph TD
            %% @node A pos=0,0
            %% @node B pos=1,0
            A[Start] --> B[End]
    """))
    assert len(model.nodes) == 2
    assert len(model.edges) == 1
    assert model.nodes[0].label == "Start"
    assert model.nodes[1].label == "End"
    assert model.edges[0].direction == Direction.FORWARD


def test_node_without_label_uses_id():
    model = parse_mermaid(textwrap.dedent("""\
        graph LR
            %% @node A pos=0,0
            %% @node B pos=0,1
            A --> B
    """))
    assert model.nodes[0].label == "A"
    assert model.nodes[1].label == "B"


# ---------------------------------------------------------------------------
# @config annotation
# ---------------------------------------------------------------------------


def test_config_annotation():
    model = parse_mermaid(textwrap.dedent("""\
        %% @config name="My Diagram" rows=3 cols=4 cell_size=200 padding=40 bg=#F0F0F0
        graph TD
            %% @node A pos=0,0
            A[Only Node]
    """))
    assert model.name == "My Diagram"
    assert model.filename == "my_diagram"
    assert model.rows == 3
    assert model.cols == 4
    assert model.cell_size == 200
    assert model.padding == 40
    assert model.bg_color == "#F0F0F0"


def test_config_with_filename():
    model = parse_mermaid(textwrap.dedent("""\
        %% @config name="Test" filename=custom_output
        graph TD
            %% @node A pos=0,0
            A[Node]
    """))
    assert model.filename == "custom_output"


# ---------------------------------------------------------------------------
# @node annotations (pos, icon)
# ---------------------------------------------------------------------------


def test_node_positions():
    model = parse_mermaid(textwrap.dedent("""\
        graph TD
            %% @node A pos=2,3
            %% @node B pos=0,1
            A[Server] --> B[Client]
    """))
    node_a = next(n for n in model.nodes if n.label == "Server")
    node_b = next(n for n in model.nodes if n.label == "Client")
    assert node_a.row == 2
    assert node_a.col == 3
    assert node_b.row == 0
    assert node_b.col == 1


def test_node_icon():
    model = parse_mermaid(textwrap.dedent("""\
        graph TD
            %% @node A pos=0,0 icon=aws/compute/ec2
            A[EC2]
    """))
    assert model.nodes[0].icon == "aws/compute/ec2"


def test_node_without_icon_defaults_empty():
    model = parse_mermaid(textwrap.dedent("""\
        graph TD
            %% @node A pos=0,0
            A[Box]
    """))
    assert model.nodes[0].icon == ""


# ---------------------------------------------------------------------------
# Auto-compute rows/cols
# ---------------------------------------------------------------------------


def test_auto_compute_grid_size():
    model = parse_mermaid(textwrap.dedent("""\
        graph TD
            %% @node A pos=0,0
            %% @node B pos=2,3
            A --> B
    """))
    assert model.rows == 3
    assert model.cols == 4


def test_config_overrides_auto_grid():
    model = parse_mermaid(textwrap.dedent("""\
        %% @config rows=10 cols=10
        graph TD
            %% @node A pos=0,0
            %% @node B pos=1,1
            A --> B
    """))
    assert model.rows == 10
    assert model.cols == 10


# ---------------------------------------------------------------------------
# Edge types
# ---------------------------------------------------------------------------


def test_forward_arrow():
    model = parse_mermaid(textwrap.dedent("""\
        graph TD
            %% @node A pos=0,0
            %% @node B pos=1,0
            A --> B
    """))
    assert model.edges[0].direction == Direction.FORWARD
    assert model.edges[0].style == ""


def test_undirected_line():
    model = parse_mermaid(textwrap.dedent("""\
        graph TD
            %% @node A pos=0,0
            %% @node B pos=1,0
            A --- B
    """))
    assert model.edges[0].direction == Direction.NONE


def test_dashed_arrow():
    model = parse_mermaid(textwrap.dedent("""\
        graph TD
            %% @node A pos=0,0
            %% @node B pos=1,0
            A -.-> B
    """))
    assert model.edges[0].direction == Direction.FORWARD
    assert model.edges[0].style == "dashed"


def test_bold_arrow():
    model = parse_mermaid(textwrap.dedent("""\
        graph TD
            %% @node A pos=0,0
            %% @node B pos=1,0
            A ==> B
    """))
    assert model.edges[0].direction == Direction.FORWARD
    assert model.edges[0].style == "bold"


def test_edge_label_pipe_syntax():
    model = parse_mermaid(textwrap.dedent("""\
        graph TD
            %% @node A pos=0,0
            %% @node B pos=1,0
            A -->|HTTPS| B
    """))
    assert model.edges[0].label == "HTTPS"
    assert model.edges[0].direction == Direction.FORWARD


def test_edge_label_inline_syntax():
    model = parse_mermaid(textwrap.dedent("""\
        graph TD
            %% @node A pos=0,0
            %% @node B pos=1,0
            A -- data flow --> B
    """))
    assert model.edges[0].label == "data flow"
    assert model.edges[0].direction == Direction.FORWARD


# ---------------------------------------------------------------------------
# Subgraphs / clusters
# ---------------------------------------------------------------------------


def test_subgraph_creates_cluster():
    model = parse_mermaid(textwrap.dedent("""\
        graph TD
            %% @node A pos=0,0
            %% @node B pos=0,1
            subgraph vpc [VPC]
                %% @cluster pos=0,0 size=2,1
                A[Web] --> B[DB]
            end
    """))
    assert len(model.clusters) == 1
    cluster = model.clusters[0]
    assert cluster.label == "VPC"
    assert cluster.row == 0
    assert cluster.col == 0
    assert cluster.width == 2
    assert cluster.height == 1


def test_subgraph_cluster_colors():
    model = parse_mermaid(textwrap.dedent("""\
        graph TD
            %% @node A pos=0,0
            subgraph sg [Group]
                %% @cluster pos=0,0 size=2,2 bg=#FFF3E0 border=#FFB74D
                A[Item]
            end
    """))
    cluster = model.clusters[0]
    assert cluster.bg_color == "#FFF3E0"
    assert cluster.border_color == "#FFB74D"


def test_nodes_inside_subgraph_get_cluster_id():
    model = parse_mermaid(textwrap.dedent("""\
        graph TD
            %% @node A pos=0,0
            %% @node B pos=0,1
            %% @node C pos=1,0
            subgraph vpc [VPC]
                %% @cluster pos=0,0 size=2,2
                A[Web] --> B[DB]
            end
            C[External] --> A
    """))
    node_a = next(n for n in model.nodes if n.label == "Web")
    node_b = next(n for n in model.nodes if n.label == "DB")
    node_c = next(n for n in model.nodes if n.label == "External")
    assert node_a.cluster_id == "vpc"
    assert node_b.cluster_id == "vpc"
    assert node_c.cluster_id is None


# ---------------------------------------------------------------------------
# Node shapes (all should parse without error)
# ---------------------------------------------------------------------------


def test_node_shapes():
    model = parse_mermaid(textwrap.dedent("""\
        graph TD
            %% @node A pos=0,0
            %% @node B pos=0,1
            %% @node C pos=1,0
            %% @node D pos=1,1
            A[Rectangle] --> B(Rounded)
            C{Diamond} --> D((Circle))
    """))
    assert len(model.nodes) == 4
    labels = {n.label for n in model.nodes}
    assert labels == {"Rectangle", "Rounded", "Diamond", "Circle"}


# ---------------------------------------------------------------------------
# Multiple edges on one line / chained
# ---------------------------------------------------------------------------


def test_multiple_edges_same_line():
    model = parse_mermaid(textwrap.dedent("""\
        graph TD
            %% @node A pos=0,0
            %% @node B pos=0,1
            %% @node C pos=0,2
            A --> B --> C
    """))
    assert len(model.edges) == 2


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------


def test_missing_pos_annotation_raises():
    with pytest.raises(ValueError, match="no.*@node.*annotation"):
        parse_mermaid(textwrap.dedent("""\
            graph TD
                A[Orphan] --> B[Lost]
        """))


def test_malformed_pos_raises():
    with pytest.raises(ValueError, match="row,col"):
        parse_mermaid(textwrap.dedent("""\
            graph TD
                %% @node A pos=bad
                A[Node]
        """))


def test_missing_cluster_size_raises():
    with pytest.raises(ValueError, match="size"):
        parse_mermaid(textwrap.dedent("""\
            graph TD
                %% @node A pos=0,0
                subgraph sg [Group]
                    %% @cluster pos=0,0
                    A[Node]
                end
        """))


# ---------------------------------------------------------------------------
# Diagram.from_mermaid integration
# ---------------------------------------------------------------------------


def test_from_mermaid_returns_diagram():
    d = Diagram.from_mermaid(textwrap.dedent("""\
        %% @config name="Test"
        graph TD
            %% @node A pos=0,0
            %% @node B pos=1,0
            A[Hello] --> B[World]
    """), show=False)
    assert d.model.name == "Test"
    assert len(d.model.nodes) == 2
    assert len(d.model.edges) == 1


def test_from_mermaid_file(tmp_path):
    mmd = tmp_path / "test.mmd"
    mmd.write_text(textwrap.dedent("""\
        %% @config name="File Test"
        graph LR
            %% @node X pos=0,0
            %% @node Y pos=0,1
            X[Src] --> Y[Dst]
    """))
    d = Diagram.from_mermaid_file(str(mmd), show=False)
    assert d.model.name == "File Test"
    assert len(d.model.nodes) == 2


# ---------------------------------------------------------------------------
# Full integration: AWS-style diagram
# ---------------------------------------------------------------------------


def test_full_aws_style_diagram():
    text = textwrap.dedent("""\
        %% @config name="AWS Web Service" rows=5 cols=7 cell_size=180
        graph TD
            %% @node users pos=0,3 icon=aws/general/users
            %% @node dns pos=1,1 icon=aws/network/route-53
            %% @node cdn pos=1,3 icon=aws/network/cloudfront
            %% @node waf pos=1,5 icon=aws/security/waf
            %% @node lb pos=2,3 icon=aws/network/elastic-load-balancing
            %% @node web1 pos=3,1 icon=aws/compute/ec2
            %% @node web2 pos=3,3 icon=aws/compute/ec2
            %% @node web3 pos=3,5 icon=aws/compute/ec2
            %% @node db pos=4,2 icon=aws/database/aurora
            %% @node cache pos=4,4 icon=aws/database/elasticache

            subgraph public_subnet [Public Subnet]
                %% @cluster pos=0,1 size=5,2 bg=#FFF3E0 border=#FFB74D
                users[Users] --> dns[Route 53]
                users --> cdn[CloudFront]
                cdn --> waf[WAF]
            end

            subgraph private_subnet [Private Subnet]
                %% @cluster pos=2,0 size=7,3 bg=#E8F5E9 border=#81C784
                waf --> lb[ALB]
                lb --> web1[Web Server 1]
                lb --> web2[Web Server 2]
                lb --> web3[Web Server 3]
                web1 --> db[Aurora DB]
                web2 --> db
                web3 -.->|sessions| cache[ElastiCache]
                web1 --> cache
            end
    """)
    model = parse_mermaid(text)

    assert model.name == "AWS Web Service"
    assert model.rows == 5
    assert model.cols == 7
    assert model.cell_size == 180

    assert len(model.nodes) == 10
    assert len(model.clusters) == 2

    node_users = next(n for n in model.nodes if n.label == "Users")
    assert node_users.row == 0
    assert node_users.col == 3
    assert node_users.icon == "aws/general/users"
    assert node_users.cluster_id == "public_subnet"

    node_lb = next(n for n in model.nodes if n.label == "ALB")
    assert node_lb.row == 2
    assert node_lb.col == 3
    assert node_lb.cluster_id == "private_subnet"

    sessions_edge = next(e for e in model.edges if e.label == "sessions")
    assert sessions_edge.style == "dashed"
    assert sessions_edge.direction == Direction.FORWARD

    public = next(c for c in model.clusters if c.id == "public_subnet")
    assert public.label == "Public Subnet"
    assert public.bg_color == "#FFF3E0"

    private = next(c for c in model.clusters if c.id == "private_subnet")
    assert private.row == 2
    assert private.width == 7
    assert private.height == 3
