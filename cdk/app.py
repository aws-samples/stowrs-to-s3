"""
Entrypoint for stack creation.
SPDX-License-Identifier: Apache 2.0
"""

#!/usr/bin/env python3
import os
import aws_cdk as cdk
from cdk_nag import NagPackSuppression
import config as config
import cdk.infrastructure as stack
from aws_cdk import Tags , Aspects




app = cdk.App()

app_name = config.CDK_APP_NAME
vpc_cidr = config.VPC_CIDR
dicom_bucket_name=config.DICOM_BUCKET
certificate_config=config.CERTIFICATE
task_definition = config.FARGATE_TASK_DEF
allowed_peers = config.ALLOWED_PEERS
tag_list = config.RESOURCE_TAGS


env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION'))

stowrstos3 = stack.StowRStoS3Stack( app, app_name, 
                                    vpc_cidr=vpc_cidr, 
                                    dicom_bucket_name=dicom_bucket_name,
                                    certificate_config=certificate_config, 
                                    task_definition= task_definition,
                                    allowed_peers=allowed_peers, 
                                    env=env
                                    )

#Adding the Tags to all the resources of the stack.
Tags.of(stowrstos3).add("deployment", app_name)
for envkey in tag_list["tag_list"]:
    Tags.of(stowrstos3).add(envkey , tag_list["tag_list"][envkey])


app.synth()


    # If you don't specify 'env', this stack will be environment-agnostic.
    # Account/Region-dependent features and context lookups will not work,
    # but a single synthesized template can be deployed anywhere.

    # Uncomment the next line to specialize this stack for the AWS Account
    # and Region that are implied by the current CLI configuration.

    #env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),

    # Uncomment the next line if you know exactly what Account and Region you
    # want to deploy the stack to. */

    #env=cdk.Environment(account='123456789012', region='us-east-1'),

    # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html