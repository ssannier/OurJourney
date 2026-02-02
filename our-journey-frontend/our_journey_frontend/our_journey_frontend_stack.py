import os
import hashlib
import time
from aws_cdk import (
    Duration,
    Stack,
    RemovalPolicy,
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
    aws_lambda as _lambda,
    aws_iam as iam,
    CustomResource,
)
from constructs import Construct
import aws_cdk as cdk


class OurJourneyFrontendStack(Stack):
    """
    CDK Stack for Our Journey Frontend deployment using AWS Amplify.
    
    This stack creates:
    - S3 bucket for storing frontend build artifacts
    - Lambda function for Amplify deployment orchestration
    - Custom Resource to trigger deployment on stack lifecycle events
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # ======================================================================
        # 1. GENERATE RANDOM SUFFIX FOR RESOURCE UNIQUENESS
        # ======================================================================
        # Create a unique 8-character suffix from stack metadata
        raw_suffix = f"{self.stack_name}-{self.account}-{time.time()}"
        self.suffix = hashlib.md5(raw_suffix.encode()).hexdigest()[:8]
        
        # ======================================================================
        # 2. VALIDATE BUILD.ZIP EXISTS
        # ======================================================================
        # Construct path to build.zip (relative to this stack file)
        build_zip_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "build.zip"
        )
        
        # Fail fast if build.zip doesn't exist
        if not os.path.exists(build_zip_path):
            raise FileNotFoundError(
                f"build.zip not found at {build_zip_path}. "
                f"Please run frontend_build.sh before deploying this stack."
            )
        
        # ======================================================================
        # 3. CREATE S3 BUCKET FOR FRONTEND STORAGE
        # ======================================================================
        frontend_bucket = s3.Bucket(
            self,
            "FrontendStoreBucket",
            bucket_name=f"our-journey-frontend-store-{self.suffix}",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            versioned=False,
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=True,  # Deny non-HTTPS requests
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
        )
        
        # Add bucket policy to allow Amplify service access
        frontend_bucket.add_to_resource_policy(
            iam.PolicyStatement(
                sid="AllowAmplifyToListBucket",
                effect=iam.Effect.ALLOW,
                principals=[iam.ServicePrincipal("amplify.amazonaws.com")],
                actions=["s3:ListBucket"],
                resources=[frontend_bucket.bucket_arn],
                conditions={
                    "StringEquals": {
                        "aws:SourceAccount": self.account
                    }
                }
            )
        )
        
        frontend_bucket.add_to_resource_policy(
            iam.PolicyStatement(
                sid="AllowAmplifyToGetObjects",
                effect=iam.Effect.ALLOW,
                principals=[iam.ServicePrincipal("amplify.amazonaws.com")],
                actions=["s3:GetObject"],
                resources=[f"{frontend_bucket.bucket_arn}/*"],
                conditions={
                    "StringEquals": {
                        "aws:SourceAccount": self.account
                    }
                }
            )
        )
        
        # ======================================================================
        # 4. UPLOAD BUILD.ZIP TO S3 AS A FILE (NOT EXTRACTED)
        # ======================================================================
        # The Lambda expects build.zip to exist as a file in S3
        # We'll use an Asset to stage the file, then a custom resource to copy it
        
        from aws_cdk import aws_s3_assets as s3_assets
        from aws_cdk import custom_resources as cr
        
        # Create an asset from build.zip (this uploads to CDK's asset bucket)
        build_zip_asset = s3_assets.Asset(
            self,
            "BuildZipAsset",
            path=build_zip_path,
        )
        
        # Create a custom resource to copy build.zip from asset bucket to frontend bucket
        # This preserves the file as-is without extraction
        copy_build_zip = cr.AwsCustomResource(
            self,
            "CopyBuildZip",
            on_create=cr.AwsSdkCall(
                service="S3",
                action="copyObject",
                parameters={
                    "CopySource": f"{build_zip_asset.s3_bucket_name}/{build_zip_asset.s3_object_key}",
                    "Bucket": frontend_bucket.bucket_name,
                    "Key": "build.zip",
                },
                physical_resource_id=cr.PhysicalResourceId.of("build-zip-copy"),
            ),
            on_delete=cr.AwsSdkCall(
                service="S3",
                action="deleteObject",
                parameters={
                    "Bucket": frontend_bucket.bucket_name,
                    "Key": "build.zip",
                },
            ),
            policy=cr.AwsCustomResourcePolicy.from_statements([
                iam.PolicyStatement(
                    actions=["s3:GetObject"],
                    resources=[build_zip_asset.bucket.arn_for_objects(build_zip_asset.s3_object_key)],
                ),
                iam.PolicyStatement(
                    actions=["s3:PutObject", "s3:DeleteObject"],
                    resources=[f"{frontend_bucket.bucket_arn}/build.zip"],
                ),
            ]),
        )
        
        # ======================================================================
        # 5. CREATE IAM ROLE FOR LAMBDA FUNCTION
        # ======================================================================
        lambda_role = iam.Role(
            self,
            "AmplifyDeploymentLambdaRole",
            role_name=f"our-journey-amplify-lambda-role-{self.suffix}",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description="Execution role for Our Journey Amplify deployment Lambda",
        )
        
        # Add S3 access policy
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                sid="S3BucketAccess",
                effect=iam.Effect.ALLOW,
                actions=[
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:DeleteObject",
                    "s3:ListBucket",
                ],
                resources=[
                    frontend_bucket.bucket_arn,
                    f"{frontend_bucket.bucket_arn}/*",
                ],
            )
        )
        
        # Add Amplify access policy
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                sid="AmplifyAccess",
                effect=iam.Effect.ALLOW,
                actions=[
                    "amplify:CreateApp",
                    "amplify:UpdateApp",
                    "amplify:DeleteApp",
                    "amplify:CreateBranch",
                    "amplify:UpdateBranch",
                    "amplify:DeleteBranch",
                    "amplify:GetApp",
                    "amplify:GetBranch",
                    "amplify:ListApps",
                    "amplify:ListBranches",
                    "amplify:StartDeployment",
                ],
                resources=["*"],  # Amplify doesn't support resource-level permissions
            )
        )
        
        # Attach managed policy for CloudWatch Logs
        lambda_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSLambdaBasicExecutionRole"
            )
        )
        
        # ======================================================================
        # 6. CREATE LAMBDA FUNCTION
        # ======================================================================
        # Construct path to Lambda code directory
        lambda_code_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "lambdas",
            "amplify_deployment_lambda"
        )
        
        # Validate Lambda code directory exists
        if not os.path.exists(lambda_code_path):
            raise FileNotFoundError(
                f"Lambda code directory not found at {lambda_code_path}"
            )
        
        # Determine Python runtime (try 3.13 first, fallback to 3.12)
        try:
            lambda_runtime = _lambda.Runtime.PYTHON_3_13
        except AttributeError:
            lambda_runtime = _lambda.Runtime.PYTHON_3_12
        
        amplify_deployment_lambda = _lambda.Function(
            self,
            "AmplifyDeploymentLambda",
            function_name=f"our-journey-amplify-deployment-{self.suffix}",
            runtime=lambda_runtime,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset(lambda_code_path),
            role=lambda_role,
            timeout=Duration.seconds(60),
            environment={
                "FRONTEND_BUCKET_NAME": frontend_bucket.bucket_name,
                "FRONTEND_FOLDER_NAME": "/build/",
                "AMPLIFY_APP_NAME": f"OurJourneyApp-{self.suffix}",
            },
            description="Lambda function to manage Amplify app deployment for Our Journey",
        )
        
        # ======================================================================
        # 7. CREATE CUSTOM RESOURCE
        # ======================================================================
        # Custom Resource provider using the Lambda function
        custom_resource_provider = cdk.custom_resources.Provider(
            self,
            "AmplifyDeploymentProvider",
            on_event_handler=amplify_deployment_lambda,
        )
        
        # Create the Custom Resource
        amplify_custom_resource = CustomResource(
            self,
            "AmplifyDeploymentCustomResource",
            service_token=custom_resource_provider.service_token,
            properties={
                "ServiceTimeout": 60,
            },
        )
        
        # Ensure Custom Resource waits for build.zip to be copied to S3
        amplify_custom_resource.node.add_dependency(copy_build_zip)