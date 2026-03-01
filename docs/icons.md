# Available Icons

diagrams_for_ai uses icons from the [diagrams](https://diagrams.mingrammer.com/) package. This gives you access to hundreds of icons across all major cloud providers and technologies.

## Icon key format

Icons are referenced as strings in the format `"provider/category/name"`:

```python
Node("My Server", icon="aws/compute/ec2", row=0, col=0)
```

You can also use the shorter `"provider/name"` format -- the library will search all categories within the provider:

```python
Node("My Server", icon="aws/ec2", row=0, col=0)
```

## Providers

| Provider | Key prefix | Examples |
|----------|-----------|----------|
| AWS | `aws/` | `aws/compute/ec2`, `aws/database/rds`, `aws/network/elb` |
| GCP | `gcp/` | `gcp/compute/compute-engine`, `gcp/database/sql` |
| Azure | `azure/` | `azure/compute/virtual-machines`, `azure/database/sql-databases` |
| Kubernetes | `k8s/` | `k8s/compute/pod`, `k8s/network/service` |
| On-Premises | `onprem/` | `onprem/database/postgresql`, `onprem/queue/rabbitmq` |
| Programming | `programming/` | `programming/language/python`, `programming/language/go` |
| SaaS | `saas/` | `saas/chat/slack`, `saas/identity/auth0` |
| Generic | `generic/` | `generic/compute/rack`, `generic/database/sql` |
| Alibaba Cloud | `alibabacloud/` | `alibabacloud/compute/ecs` |
| Oracle Cloud | `oci/` | `oci/compute/vm` |
| DigitalOcean | `digitalocean/` | `digitalocean/compute/droplet` |
| Elastic | `elastic/` | `elastic/elasticsearch/elasticsearch` |
| Firebase | `firebase/` | `firebase/develop/authentication` |
| IBM | `ibm/` | `ibm/compute/bare-metal-server` |
| OpenStack | `openstack/` | `openstack/compute/nova` |
| Outscale | `outscale/` | `outscale/compute/compute` |

## Listing icons programmatically

You can discover available icons in code:

```python
from diagrams_for_ai.icons import list_providers, list_icons

# List all providers
print(list_providers())
# ['alibabacloud', 'aws', 'azure', 'digitalocean', 'elastic', ...]

# List all icons for a specific provider
for icon_key in list_icons("aws"):
    print(icon_key)
# aws/analytics/athena
# aws/analytics/cloudsearch
# aws/compute/batch
# aws/compute/ec2
# ...
```

## Custom icons

You can use any local PNG or SVG file as an icon by passing its file path:

```python
Node("Custom Service", icon="/path/to/my-icon.png", row=0, col=0)
Node("Another", icon="./local-icons/my-logo.png", row=0, col=1)
```

## Common AWS icons

Here are some frequently used AWS icon keys:

| Service | Icon key |
|---------|----------|
| EC2 | `aws/compute/ec2` |
| Lambda | `aws/compute/lambda-function` |
| ECS | `aws/compute/elastic-container-service` |
| RDS | `aws/database/rds` |
| Aurora | `aws/database/aurora` |
| DynamoDB | `aws/database/dynamodb` |
| S3 | `aws/storage/simple-storage-service-s3` |
| ELB | `aws/network/elastic-load-balancing` |
| CloudFront | `aws/network/cloudfront` |
| Route 53 | `aws/network/route-53` |
| API Gateway | `aws/network/api-gateway` |
| SQS | `aws/integration/simple-queue-service-sqs` |
| SNS | `aws/integration/simple-notification-service-sns` |
| CloudWatch | `aws/management/cloudwatch` |
| IAM | `aws/security/identity-and-access-management-iam` |
| WAF | `aws/security/waf` |

!!! tip
    If you're unsure of the exact icon key, use `list_icons("aws")` to get the full list, or try the short form like `"aws/ec2"` and the library will search for it.
