import boto3
from botocore.exceptions import ClientError
import json


def get_secret():

    secret_name = "rds!db-0a86d054-f798-4a71-8392-a31237c6d2da"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    secret = get_secret_value_response['SecretString']
    secret_dict = json.loads(secret)
    username = secret_dict.get('username')  # Example key
    password = secret_dict.get('password')  # Example key
    
    return username, password


def main():
    username, password = get_secret()
    print(username)

if __name__ == '__main__':
    main()