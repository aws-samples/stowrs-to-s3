"""
Logic driving the task content based on the config settings passed as input.
SPDX-License-Identifier: Apache 2.0
"""

from typing import Any
from constructs import Construct
from aws_cdk import (
    Stack,
    CfnOutput,
    aws_iam as iam,
    aws_s3 as s3,
    aws_ec2 as ec2,
    Tags
)


from .storage import S3Bucket
from .network import Vpc
from .fargate import FargateService
from .nlb import StowNLB


from .roles import Roles


import time


class StowRStoS3Stack(Stack):
    def __init__(self,  scope: Construct, 
                        id: str, 
                        vpc_cidr, 
                        dicom_bucket_name,
                        certificate_config,
                        task_definition,
                        allowed_peers,
                        **kwargs
                ):
        super().__init__(scope, id, **kwargs)

        region = self.region
        account = self.account

        #VPC which will contain the Fargae containers.
        vpc = Vpc(self, "VPC", vpc_cidr)

        # S3 bucket to store DICOM files.
        S3bucket_dicom = S3Bucket(self, dicom_bucket_name)


        #Create the NLB
        lb = StowNLB(self, "nlb", vpc.getVpc(), certificate_config,  S3bucket_dicom.getS3Bucket())

    
        #If the value is anything else than ACM, we default to S3 mode.
        if(certificate_config["certificate_mode"].upper() != "ACM"):
            #S3 bucket to store certificates.
            S3bucket_certs = S3Bucket(self, certificate_config["certificate_bucket"])
            taskRole = Roles(self, "TaskRole", S3bucket_dicom.getBucketArn() , S3bucket_certs.getBucketArn() )




            if(certificate_config["certificate_auth_mode"].upper() == 'CLIENTAUTH'):
                authmode = 'clientauth'
            else:
                authmode = 'anonymous'
            fg=FargateService(self, "Fargate", vpc=vpc.getVpc(), task_role=taskRole.getRole() , task_definition=task_definition , dicom_bucket_name=S3bucket_dicom.getBucketName() , certificate_bucket_name=S3bucket_certs.getBucketName() ,  loadbalancer=lb , authentication_mode=authmode, certificate_mode="FROMS3" , allowed_peers=allowed_peers )
        else:
            #we do not need to create the certificate bucket in this mode, neither we need to add privilegs for it to the role.
            taskRole = Roles(self, "TaskRole", dicom_s3_arn=S3bucket_dicom.getBucketArn() , cert_s3_arn=None )
            fg=FargateService(self, "Fargate", vpc=vpc.getVpc(), task_role=taskRole.getRole() , task_definition=task_definition , dicom_bucket_name=S3bucket_dicom.getBucketName() , certificate_bucket_name=None , loadbalancer=lb , authentication_mode="anonymous" , certificate_mode="ACM" , allowed_peers=allowed_peers )


        # Creation for the Fargate Service
        
        