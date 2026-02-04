from aws_cdk import (
    Duration,
    Stack,
    aws_apigatewayv2 as apigwv2,
    aws_apigatewayv2_integrations as apigwv2_i,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_s3 as s3,
    aws_events as events,
    aws_events_targets as targets,
    CfnOutput,
    CustomResource,
)
import aws_cdk as cdk
from cdklabs.generative_ai_cdk_constructs import bedrock, s3vectors
from constructs import Construct

class OurJourneyStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Create an S3 bucket to store documents
        doc_bucket = s3.Bucket(
            self, 
            'DocBucket',
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # Create a Bedrock Vector Knowledge Base
        kb = bedrock.VectorKnowledgeBase(
            self, 
            "knowledgebase",
            embeddings_model=bedrock.BedrockFoundationModel.TITAN_EMBED_TEXT_V2_256,
            vector_store=s3vectors.VectorIndex(
                self, 
                "vectorstore",
                dimension=256,
                vector_bucket=s3vectors.VectorBucket(
                    self, 
                    "vector-bucket",
                    removal_policy=cdk.RemovalPolicy.DESTROY,
                    auto_delete_objects=True
                ),
                non_filterable_metadata_keys=[
                    "AMAZON_BEDROCK_TEXT", 
                    "AMAZON_BEDROCK_METADATA"
                ]
            )
        )

        kb.add_s3_data_source(
            bucket=doc_bucket,
            data_deletion_policy=bedrock.DataDeletionPolicy.RETAIN
        )

        # Create bedrock guardrails
        guardrail = bedrock.Guardrail(
            self,
            "guardrail",
            name=f"our-journey-guardrail-{self.stack_name}",
            blocked_input_messaging="Your request cannot be processed as it violates our content policies. (Su solicitud no puede ser procesada ya que viola nuestras políticas de contenido.)",
            blocked_outputs_messaging="Your request cannot be processed as it violates our content policies. (Su solicitud no puede ser procesada ya que viola nuestras políticas de contenido.)",
            content_filters=[
                bedrock.ContentFilter(
                    input_strength=bedrock.ContentFilterStrength.MEDIUM,
                    output_strength=bedrock.ContentFilterStrength.MEDIUM,
                    type=bedrock.ContentFilterType.SEXUAL,
                    input_action=bedrock.GuardrailAction.BLOCK,
                    input_enabled=True,
                    output_action=bedrock.GuardrailAction.BLOCK,
                    output_enabled=True
                ),
                bedrock.ContentFilter(
                    input_strength=bedrock.ContentFilterStrength.MEDIUM,
                    output_strength=bedrock.ContentFilterStrength.MEDIUM,
                    type=bedrock.ContentFilterType.VIOLENCE,
                    input_action=bedrock.GuardrailAction.BLOCK,
                    input_enabled=True,
                    output_action=bedrock.GuardrailAction.BLOCK,
                    output_enabled=True
                ),
                bedrock.ContentFilter(
                    input_strength=bedrock.ContentFilterStrength.MEDIUM,
                    output_strength=bedrock.ContentFilterStrength.MEDIUM,
                    type=bedrock.ContentFilterType.HATE,
                    input_action=bedrock.GuardrailAction.BLOCK,
                    input_enabled=True,
                    output_action=bedrock.GuardrailAction.BLOCK,
                    output_enabled=True
                ),
                bedrock.ContentFilter(
                    input_strength=bedrock.ContentFilterStrength.MEDIUM,
                    output_strength=bedrock.ContentFilterStrength.MEDIUM,
                    type=bedrock.ContentFilterType.INSULTS,
                    input_action=bedrock.GuardrailAction.BLOCK,
                    input_enabled=True,
                    output_action=bedrock.GuardrailAction.BLOCK,
                    output_enabled=True
                ),
                bedrock.ContentFilter(
                    input_strength=bedrock.ContentFilterStrength.MEDIUM,
                    output_strength=bedrock.ContentFilterStrength.MEDIUM,
                    type=bedrock.ContentFilterType.MISCONDUCT,
                    input_action=bedrock.GuardrailAction.BLOCK,
                    input_enabled=True,
                    output_action=bedrock.GuardrailAction.BLOCK,
                    output_enabled=True
                ),
                bedrock.ContentFilter(
                    input_strength=bedrock.ContentFilterStrength.MEDIUM,
                    output_strength=bedrock.ContentFilterStrength.NONE,
                    type=bedrock.ContentFilterType.PROMPT_ATTACK,
                    input_action=bedrock.GuardrailAction.BLOCK,
                    input_enabled=True,
                )
            ]
        )


        # Create a WebSocket API
        web_socket_api = apigwv2.WebSocketApi(self, "web_socket_api",)
        apigwv2.WebSocketStage(
            self, 
            "stage",
            web_socket_api=web_socket_api,
            stage_name="prod",
            auto_deploy=True
        )


        bedrock_orchestration = _lambda.Function(
            self,
            "bedrock-orchestration-lambda",
            runtime = _lambda.Runtime.PYTHON_3_12,
            code = _lambda.Code.from_asset(
                "./lambdas/bedrock_orchestration",
            ),
            handler = "lambda_function.lambda_handler",
            timeout = Duration.minutes(15),
            environment={
                "API_GATEWAY_URL": web_socket_api.api_endpoint,
                "KNOWLEDGE_BASE_ID": kb.knowledge_base_id,
                "NUM_KB_RESULTS": "5",
                "GUARDRAIL_ID": guardrail.guardrail_id,
                "GUARDRAIL_VERSION": guardrail.guardrail_version,
            }
        )

        # Grant necessary permissions to the Lambda function
        bedrock_orchestration.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonBedrockFullAccess")
        )
        bedrock_orchestration.role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonAPIGatewayInvokeFullAccess")
        )
        bedrock_orchestration.add_to_role_policy(
            iam.PolicyStatement(
                actions=["lambda:InvokeFunction"],
                resources=[f"arn:aws:lambda:{self.region}:{self.account}:function:OurJourneyStack-*"]
            )
        )

        

        #api gateway integrations
        web_socket_api.add_route(
            "sendMessage",
            integration = apigwv2_i.WebSocketLambdaIntegration("bedrock-orchestration", bedrock_orchestration),
            return_response=True
        )

        # ======================================================================
        # SCRAPER LAMBDA LAYER
        # ======================================================================
        scraper_layer = _lambda.LayerVersion(
            self,
            "ScraperLayer",
            code=_lambda.Code.from_asset("./lambdas/layers/scraper-layer.zip"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_12],
            description="Web scraping dependencies (requests, BeautifulSoup4)"
        )

        # ======================================================================
        # SCRAPER LAMBDA IAM ROLE
        # ======================================================================
        scraper_role = iam.Role(
            self,
            "ScraperLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description="Execution role for OurJourney scraper and sync Lambda"
        )

        # S3 permissions for doc bucket
        scraper_role.add_to_policy(
            iam.PolicyStatement(
                sid="S3BucketAccess",
                effect=iam.Effect.ALLOW,
                actions=[
                    "s3:ListBucket",
                    "s3:DeleteObject",
                    "s3:PutObject",
                ],
                resources=[
                    doc_bucket.bucket_arn,
                    f"{doc_bucket.bucket_arn}/*"
                ]
            )
        )

        # Bedrock Agent permissions for knowledge base sync
        scraper_role.add_to_policy(
            iam.PolicyStatement(
                sid="BedrockAgentAccess",
                effect=iam.Effect.ALLOW,
                actions=[
                    "bedrock:ListDataSources",
                    "bedrock:StartIngestionJob",
                    "bedrock:GetIngestionJob",
                ],
                resources=[
                    f"arn:aws:bedrock:{self.region}:{self.account}:knowledge-base/{kb.knowledge_base_id}",
                    f"arn:aws:bedrock:{self.region}:{self.account}:knowledge-base/{kb.knowledge_base_id}/*"
                ]
            )
        )

        # CloudWatch Logs permissions
        scraper_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSLambdaBasicExecutionRole"
            )
        )

        # ======================================================================
        # SCRAPER LAMBDA FUNCTION
        # ======================================================================
        scraper_lambda = _lambda.Function(
            self,
            "ScraperLambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset("./lambdas/scraper_lambda"),
            role=scraper_role,
            timeout=Duration.minutes(15),  # Maximum timeout for scraping and ingestion
            memory_size=512,  # Extra memory for faster processing
            layers=[scraper_layer],
            environment={
                "DOC_BUCKET_NAME": doc_bucket.bucket_name,
                "KNOWLEDGE_BASE_ID": kb.knowledge_base_id
            },
            description="Scrapes OurJourney website and syncs Knowledge Base"
        )

        # ======================================================================
        # CUSTOM RESOURCE FOR INITIAL SCRAPE
        # ======================================================================
        # Custom resource to trigger initial scrape on stack creation
        scraper_custom_resource = CustomResource(
            self,
            "ScraperCustomResource",
            service_token=scraper_lambda.function_arn,
            properties={
                "Trigger": "StackDeploy"
            }
        )

        # Ensure custom resource runs after knowledge base is created
        scraper_custom_resource.node.add_dependency(kb)
        scraper_custom_resource.node.add_dependency(doc_bucket)

        # ======================================================================
        # EVENTBRIDGE RULE FOR WEEKLY SCRAPING
        # ======================================================================
        # Schedule: Every Sunday at midnight EST (5 AM UTC)
        scraper_schedule_rule = events.Rule(
            self,
            "ScraperScheduleRule",
            rule_name="ourjourney-weekly-scraper",
            description="Weekly web scraping and Knowledge Base sync for OurJourney",
            schedule=events.Schedule.cron(
                minute="0",
                hour="5",  # 5 AM UTC = midnight EST
                week_day="SUN"
            ),
        )

        # Add Lambda as target
        scraper_schedule_rule.add_target(
            targets.LambdaFunction(scraper_lambda)
        )

        CfnOutput(self, "websocket-url",
            value = web_socket_api.api_endpoint,
        )

        CfnOutput(self, "doc-bucket-name",
            value = doc_bucket.bucket_name,
        )


        CfnOutput(self, "knowledge-base-id",
            value = kb.knowledge_base_id,
        )

        CfnOutput(self, "scraper-lambda-arn",
            value = scraper_lambda.function_arn,
            description="ARN of the scraper Lambda function"
        )

        CfnOutput(self, "scraper-schedule-rule",
            value = scraper_schedule_rule.rule_name,
            description="EventBridge rule for weekly scraping"
        )