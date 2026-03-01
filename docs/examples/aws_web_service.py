"""Example: AWS Web Service Architecture using diagrams_for_ai."""

from diagrams_for_ai import Cluster, Diagram, Edge, LineStyle, Node

with Diagram(
    "AWS Web Service",
    rows=5,
    cols=7,
    cell_size=180,
    outformat=["svg", "png"],
    show=False,
) as d:

    with Cluster("Public Subnet", row=0, col=1, width=5, height=2, bg_color="#FFF3E0", border_color="#FFB74D"):
        users = Node("Users", icon="aws/general/users", row=0, col=3)
        dns = Node("Route 53", icon="aws/network/route-53", row=1, col=1)
        cdn = Node("CloudFront", icon="aws/network/cloudfront", row=1, col=3)
        waf = Node("WAF", icon="aws/security/waf", row=1, col=5)

    with Cluster("Private Subnet", row=2, col=0, width=7, height=3, bg_color="#E8F5E9", border_color="#81C784"):
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

print("Generated: aws_web_service.svg and aws_web_service.png")
