from aws_cdk import (
    # Duration,
    Stack,
    aws_s3 as s3,
    aws_certificatemanager as cert,
    aws_route53 as route53,
    aws_cloudfront as cf,
    aws_cloudfront_origins as origins
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
        # first create static web logging bucket

        domain_bucket = s3.Bucket(
            scope=self,
            id="domain-bucket",
            #block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            public_read_access=True,
            bucket_name=domain,
            enforce_ssl=True,
            versioned=True,
            website_error_document="404.css",
            website_index_document="index.html",
        )

        domain_bucket.grant_public_access

        # Create S3 bucket for subdomain www.patrickhess.dev
        subdomain_bucket = s3.Bucket(
            scope=self,
            id="subdomain-bucket",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            bucket_name=subdomain,
            enforce_ssl=True,
            versioned=True,
            website_redirect=s3.RedirectTarget(
                host_name=domain
            )
        )

        logging_bucket = s3.Bucket(
            scope=self,
            id="phess-web-logging-bucket",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            bucket_name=f"logs.{domain}"
        )

        # cloudfront distribution
        phess_web_distribution = cf.Distribution(
            scope=self,
            id="phess-web-cf-dist",
            default_behavior=cf.BehaviorOptions(
                origin=origins.S3Origin(
                    bucket=domain_bucket
                ),
                viewer_protocol_policy=cf.ViewerProtocolPolicy.HTTPS_ONLY
            ),
            default_root_object="index.html",
            enable_logging=True,
            log_bucket=logging_bucket,
            price_class=cf.PriceClass.PRICE_CLASS_100,
            geo_restriction=cf.GeoRestriction.allowlist("US")
        )

        # route 53

        hosted_zone = route53.HostedZone(
            scope=self,
            id="phess-web-hosted-zone",
            zone_name=domain
        )

        # Add TLS certificate
        domain_cert = cert.Certificate(
            scope=self,
            id="phess-domain-cert",
            domain_name=f"*.{domain}",
            validation=cert.CertificateValidation.from_dns(hosted_zone)
        )

        # API gateway

        # example resource
        # queue = sqs.Queue(
        #     self, "PhessWebQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )
