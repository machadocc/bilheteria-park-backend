import boto3

from .config import (
    AWS_REGION,
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_SESSION_TOKEN,
)


def get_sqs_client():
    """
        Cria um client SQS passando as credenciais explicitamente (em vez de
        depender da cadeia padrão do boto3, que dentro de containers Docker
        normalmente não encontra nada e gera "Unable to locate credentials").

        Suporta tanto credenciais "fixas" (access key + secret key) quanto
        credenciais temporárias via STS (quando AWS_SESSION_TOKEN é informado).
    """
    kwargs = {
        "region_name": AWS_REGION,
        "aws_access_key_id": AWS_ACCESS_KEY_ID,
        "aws_secret_access_key": AWS_SECRET_ACCESS_KEY,
    }
    if AWS_SESSION_TOKEN:
        kwargs["aws_session_token"] = AWS_SESSION_TOKEN

    return boto3.client("sqs", **kwargs)