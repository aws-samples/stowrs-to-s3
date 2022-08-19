"""
Generate S3 Buckets.
SPDX-License-Identifier: Apache 2.0
"""

from constructs import Construct
from aws_cdk import RemovalPolicy, aws_s3 as s3


class S3Bucket(Construct):

    _S3bucket = None

    def __init__(self, scope: Construct, id: str, **kwargs) -> None :
        super().__init__(scope, id, **kwargs)

        self._S3bucket = s3.Bucket(
            self,
            "S3Bucket",
            encryption=s3.BucketEncryption.S3_MANAGED,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            enforce_ssl=True,
            server_access_logs_prefix="AccessLogs/"
        )


    
    def getBucketArn(self):
        return self._S3bucket.bucket_arn
    
    def getBucketName(self):
        return self._S3bucket.bucket_name

    def getS3Bucket(self):
        return self._S3bucket


