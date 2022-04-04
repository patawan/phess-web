from aws_cdk import (
    # Duration,
    Stack,
    aws_s3 as s3,
    aws_route53 as route53
    # aws_sqs as sqs,
)
from constructs import Construct
import configparser


class PhessWebStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        config = configparser.ConfigParser()
        config.read("phess_web/config.ini")
        domain = config["prod"]["domain"]
        subdomain = config["prod"]["subdomain"]
        # The code that defines your stack goes here

        # Create S3 bucket for Domain patrickhess.dev
        # block public access until ready to go live
        domain_bucket = s3.Bucket(
            scope=self,
            id="domain-bucket",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            bucket_name=domain,
            enforce_ssl=True,
            versioned=True
        )

        # Create S3 bucket for subdomain www.patrickhess.dev
        subdomain_bucket = s3.Bucket(
            scope=self,
            id="subdomain-bucket",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            bucket_name=subdomain,
            enforce_ssl=True,
            versioned=True
        )

        # amplify

        # cloudfront distribution

        # route 53

        hosted_zone = route53.HostedZone(
            scope=self,
            id="phess-web-hosted-zone",
            zone_name=domain
        )

        # API gateway

        # example resource
        # queue = sqs.Queue(
        #     self, "PhessWebQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )
