import aws_cdk as core
import aws_cdk.assertions as assertions

from our_journey_frontend.our_journey_frontend_stack import OurJourneyFrontendStack

# example tests. To run these tests, uncomment this file along with the example
# resource in our_journey_frontend/our_journey_frontend_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = OurJourneyFrontendStack(app, "our-journey-frontend")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
