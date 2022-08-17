from aws_cdk import (
    Duration,
    Stack,
    aws_s3 as s3,
    aws_iam as iam,
    aws_certificatemanager as cert,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_cloudfront as cf,
    aws_cloudfront_origins as origins,
    aws_lambda as _lambda,
    aws_events as events,
    aws_events_targets as event_targets,
    aws_apigateway as gateway,
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
            public_read_access=True,
            bucket_name=domain,
            enforce_ssl=True,
            versioned=True,
            website_error_document="404.html",
            website_index_document="index.html",
        )

        domain_bucket.add_to_resource_policy(
            iam.PolicyStatement(
                sid="PublicReadGetObject",
                principals=[iam.AnyPrincipal()],
                actions=["s3:GetObject"],
                resources=[
                    f"{domain_bucket.bucket_arn}",
                    f"{domain_bucket.bucket_arn}/*",
                ],
            )
        )

        # Create S3 bucket for subdomain www.patrickhess.dev
        subdomain_bucket = s3.Bucket(
            scope=self,
            id="subdomain-bucket",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            bucket_name=subdomain,
            enforce_ssl=True,
            versioned=True,
            website_redirect=s3.RedirectTarget(host_name=domain),
        )

        logging_bucket = s3.Bucket(
            scope=self,
            id="phess-web-logging-bucket",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            bucket_name=f"logs.{domain}",
        )

        # route 53
        hosted_zone = route53.HostedZone(
            scope=self, id="phess-web-hosted-zone", zone_name=domain
        )

        # Add TLS certificate
        domain_cert = cert.Certificate(
            scope=self,
            id="phess-domain-cert",
            domain_name=f"*.{domain}",
            subject_alternative_names=[domain],
            validation=cert.CertificateValidation.from_dns(hosted_zone),
        )

        # cloudfront distribution
        phess_web_distribution = cf.Distribution(
            scope=self,
            id="phess-web-cf-dist",
            default_behavior=cf.BehaviorOptions(
                origin=origins.S3Origin(bucket=domain_bucket),
                viewer_protocol_policy=cf.ViewerProtocolPolicy.HTTPS_ONLY,
            ),
            domain_names=[domain, f"*.{domain}"],
            certificate=domain_cert,
            default_root_object="index.html",
            enable_logging=True,
            log_bucket=logging_bucket,
            price_class=cf.PriceClass.PRICE_CLASS_100,
            geo_restriction=cf.GeoRestriction.allowlist("US"),
        )

        domain_a_record = route53.ARecord(
            scope=self,
            id="phess-web-arecord",
            target=route53.RecordTarget.from_alias(
                targets.CloudFrontTarget(phess_web_distribution)
            ),
            zone=hosted_zone,
        )

        subdomain_a_record = route53.ARecord(
            scope=self,
            id="phess-subdomain-arecord",
            target=route53.RecordTarget.from_alias(
                targets.CloudFrontTarget(phess_web_distribution)
            ),
            zone=hosted_zone,
            record_name=f"*.{domain}",
        )

        # create s3 bucket for dumps of markov models
        # no encryption needed - not sensitive data
        model_dump_bucket = s3.Bucket(
            scope=self,
            id="office-model-bucket",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            bucket_name="office-model-bucket",
        )

        # create iam role for running lambdas
        phess_web_lambda_role = iam.Role(
            scope=self,
            id="phess-web-lambda-role",
            role_name="phess-web-lambda-role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AWSLambda_FullAccess"),
            ],
        )

        # lambda function to ingest the json dumps
        # Generates a line of text from the dumps
        markov_modeling_lambda = _lambda.DockerImageFunction(
            scope=self,
            id="office-markov-lambda",
            code=_lambda.DockerImageCode.from_image_asset(
                directory="phess_web/lambda/data_ingestion_model_build/"
            ),
            role=phess_web_lambda_role,
            memory_size=(1024),
            timeout=Duration.minutes(15),
        )

        # lambda on cron to create new json dumps daily
        modeling_lambda_rule = events.Rule(
            scope=self,
            id="modeling-lambda-rule",
            schedule=events.Schedule.cron(minute="0", hour="0"),
            targets=[event_targets.LambdaFunction(handler=markov_modeling_lambda)],
        )

        # text_gen_lambda
        text_gen_lambda = _lambda.DockerImageFunction(
            scope=self,
            id="get-office-line-lambda",
            code=_lambda.DockerImageCode.from_image_asset(
                directory="phess_web/lambda/get_lines/"
            ),
            role=phess_web_lambda_role,
            memory_size=(1024),
            timeout=Duration.minutes(3),
        )

        # API gateway
        api = gateway.RestApi(
            scope=self,
            id="phess-textgen-api",
            deploy=True,
            deploy_options=gateway.StageOptions(
                throttling_burst_limit=50,
                throttling_rate_limit=10,
                stage_name="prod"
                )
        )
        api.root.add_method(
            http_method="GET",
            integration=gateway.LambdaIntegration(
                handler=text_gen_lambda,
                proxy=True,
                request_parameters={"integration.request.querystring.character": "method.request.querystring.character"}
            ),
            request_parameters={"method.request.querystring.character": True}
        )
