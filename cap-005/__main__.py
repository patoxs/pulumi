import pulumi
import pulumi_aws as aws

region = aws.get_region().id
current = aws.get_caller_identity()

custom_stage_name = "calculator"
resource_path_name = "postCalculator"

iam_for_lambda = aws.iam.Role(
    "iamCalculatorHook", 
    assume_role_policy="""{
        "Version": "2012-10-17",
        "Statement": [
            {
            "Action": "sts:AssumeRole",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Effect": "Allow",
            "Sid": ""
            }
        ]
    }
""")

test_lambda = aws.lambda_.Function(
    "testCalculator",
    name="Calculator",
    code=pulumi.FileArchive("./lambda/function.zip"),
    role=iam_for_lambda.arn,
    handler="lambda_function.lambda_handler",
    runtime="python3.9",
    # environment=aws.lambda_.FunctionEnvironmentArgs(
    #     variables={
    #         "example_environ": "False",
    #     },
    # )
)

rest_api = aws.apigateway.RestApi(
    "Calculator",
    name="testCalculator",
    description="Test plus, minus, times, divided"
)
resource_Calculator = aws.apigateway.Resource(
    "postCalculator",
    parent_id=rest_api.root_resource_id,
    path_part=resource_path_name,
    rest_api=rest_api.id
)
method_Calculator = aws.apigateway.Method(
    "/calculate",
    authorization="NONE",
    http_method="GET",
    resource_id=resource_Calculator.id,
    rest_api=rest_api.id
)

integration_request = aws.apigateway.Integration(
    "integrationRequest",
    rest_api=rest_api.id,
    resource_id=resource_Calculator.id,
    http_method=method_Calculator.http_method,
    integration_http_method="POST",
    type="AWS",
    uri=test_lambda.invoke_arn
)

# Lambda
permission_lambda = aws.lambda_.Permission(
    "permissionLambda",
    action="lambda:InvokeFunction",
    function=test_lambda.name,
    principal="apigateway.amazonaws.com",
    source_arn=pulumi.Output.all(
        rest_api.id, 
        method_Calculator.http_method, 
        resource_Calculator.path).apply(
            lambda args: f"arn:aws:execute-api:{region}:{current.account_id}:{args[0]}/*/{args[1]}{args[2]}"
        ),
)

response200 = aws.apigateway.MethodResponse(
    "response200",
    rest_api=rest_api.id,
    resource_id=resource_Calculator.id,
    http_method=method_Calculator.http_method,
    status_code="200"
)

integration_response = aws.apigateway.IntegrationResponse("integrationResponseCalculator",
    rest_api=rest_api.id,
    resource_id=resource_Calculator.id,
    http_method=method_Calculator.http_method,
    status_code=response200.status_code,
    response_templates={
        "application/json": """{
            "ip" : "$context.identity.sourceIp",
            "userAgent" : "$context.identity.userAgent",
            "time" : "$context.requestTime",
            "epochTime" : "$context.requestTimeEpoch"
        }
        """,
    }
)

# Create a deployment of the Rest API.
deployment = aws.apigateway.Deployment(
    "api-deployment",
    rest_api=rest_api.id,
    # Note: Set to empty to avoid creating an implicit stage, we'll create it
    # explicitly below instead.
    opts=pulumi.ResourceOptions(depends_on=[method_Calculator])
)

# Create a stage, which is an addressable instance of the Rest API. Set it to point at the latest deployment.
stage = aws.apigateway.Stage("api-stage",
    rest_api=rest_api.id,
    deployment=deployment.id,
    stage_name=custom_stage_name,
)

# Export the https endpoint of the running Rest API
pulumi.export(
    "apigateway-rest-endpoint", 
    deployment.invoke_url.apply(
        lambda args: f"{args[0]}/{custom_stage_name}/{resource_path_name}"
    )
)
