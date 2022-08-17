import json
import boto3
import markovify as mk


def get_lines(event, context):

    try:
        s3 = boto3.client("s3")
        bucket_name = "office-model-bucket"

        character = event["queryStringParameters"]["character"]

        recon_model = get_json_model(character, bucket_name, s3)

        line = make_line(recon_model)

        output_json = {f"{character} line": line}

        return {
            "isBase64Encoded": False,
            "statusCode": 200,
            "body": json.dumps(output_json),
            "headers": {
                "Content-Type": "application/json"
                },
            }

    except Exception as e:
        return {
            "isBase64Encoded": False,
            "statusCode": 400,
            "body": json.dumps(e),
            "headers": {
                "Content-Type": "application/json"
                },
            }


def get_json_model(character, bucket, s3_client):
    object_key = f"{character}_model_json.json"
    file_content = s3_client.get_object(
        Bucket=bucket, Key=object_key)["Body"].read().decode("utf-8")
    model_json = json.loads(file_content)
    model = mk.Text.from_json(model_json)

    return model


def make_line(rebuilt_model):
    line = rebuilt_model.make_sentence(tries=50)

    return line
