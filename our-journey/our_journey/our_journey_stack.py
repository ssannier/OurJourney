from aws_cdk import (
    Duration,
    Stack,
    aws_apigatewayv2 as apigwv2,
    aws_apigatewayv2_integrations as apigwv2_i,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
    CfnOutput,
)
from cdklabs.generative_ai_cdk_constructs import bedrock
from constructs import Construct

class OurJourneyStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Create an S3 bucket to store documents
        docBucket = s3.Bucket(self, 'DocBucket')

        # Deploy local files to the S3 bucket
        s3deploy.BucketDeployment(
            self, 'DeployDocs',
            sources=[s3deploy.Source.asset('../our-journey/S3')],  # Path relative to our_journey folder
            destination_bucket=docBucket,
        )

        # Create a Bedrock Vector Knowledge Base
        kb = bedrock.VectorKnowledgeBase(self, "knowledgebase",
                                     embeddings_model=bedrock.BedrockFoundationModel.TITAN_EMBED_TEXT_V2_256,
                                     )
        kb.add_s3_data_source(bucket=docBucket)
        kb.add_web_crawler_data_source(source_urls=["https://www.ourjourney2gether.com/home-plan-assistance",
                                                    "https://www.ourjourney2gether.com/find-a-job",
                                                    "https://www.ourjourney2gether.com/essential-services",
                                                    "https://www.ourjourney2gether.com/mat-assistance",
                                                    "https://www.ourjourney2gether.com/reentry-resource-guides"])



        # Create a WebSocket API
        web_socket_api = apigwv2.WebSocketApi(self, "web_socket_api",)
        apigwv2.WebSocketStage(
            self, 
            "stage",
            web_socket_api=web_socket_api,
            stage_name="dev",
            auto_deploy=True
        )


        bedrock_orchestration = _lambda.Function(
            self,
            "bedrock-orchestration-lambda",
            runtime = _lambda.Runtime.PYTHON_3_12,
            code = _lambda.Code.from_asset(
                "./lambdas/lambda_function",
            ),
            handler = "lambda_function.lambda_handler",
            timeout = Duration.minutes(15),
            environment={
                "API_GATEWAY_URL": web_socket_api.api_endpoint,
                "KNOWLEDGE_BASE_ID": kb.knowledge_base_id, 
            }
        )

        # Grant necessary permissions to the Lambda function
        bedrock_orchestration.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonBedrockFullAccess")
        )
        bedrock_orchestration.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonAPIGatewayInvokeFullAccess")
        )

        

        #api gateway integrations
        web_socket_api.add_route(
            "sendMessage",
            integration = apigwv2_i.WebSocketLambdaIntegration("bedrock-orchestration", bedrock_orchestration),
            return_response=True
        )

        CfnOutput(self, "websocket-url",
            value = web_socket_api.api_endpoint,
        )

        CfnOutput(self, "knowledge-base-id",
            value = kb.knowledge_base_id,
        )

        
