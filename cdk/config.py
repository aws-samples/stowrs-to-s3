"""
Config file for the soluiton deployment via CDK
SPDX-License-Identifier: MIT-0
"""


CDK_APP_NAME = "stowrs-to-s3"

VPC_CIDR = "10.10.0.0/22"

DICOM_BUCKET = "stowrstos3-dicom"

CERTIFICATE = {
    "certificate_auth_mode" : "anonymous",  #Can be 'anonymous' or 'clientauth' Using 'clientauth' will make nginx request a client certificate and verify it against the truststore.crt content.
    "certificate_mode" : "ACM", #Can be 'ACM' or 'FROMS3'. If selecting ACM, the certificate needs to be created or imported in ACM first, and the certificate ARN must be added in the parameter certiciate_arn below. Note the service does not support clientauth when the mode is set to ACM.
    "certificate_arn" : "arn:aws:acm:us-east-1:040911247727:certificate/2a063c88-06a2-4cc3-bd63-acc5c1ae7bcb", #This is only required when the certificate mode is set to 'ACM'.
    "certificate_bucket" : "stowrs-to-s3-certs", #this is only required when the certificate mode is set to 'FROMS3'.
}

ALLOWED_PEERS = {
    "peer_list" : {
        "0.0.0.0/0",  #By default, allows everyone to access from the internet. You may want to replace this entry by the CIDR [YOUR_PUBLIC_IPV4/32]. You can add as many other CIDR as wanted.
    }
}

FARGATE_TASK_DEF = {
    "memory" : 6144,
    "cpu" : 2048,
    "task_count" : 1,               #This defines the number of instances to run behind the load balancer.
    "nginx_container" : {
        "source_directory" : "../nginx",
        "memory" : 2048,
        "cpu" : 1024
    },
    "app_container" : {
        "source_directory" : "../app",
        "memory" : 4096,
        "cpu" : 1024,
        "envs" :{
            "PREFIX" : "STOWFG-1",
            "WADOURL" : "https://thisurldoesnotexist.com/wado",
            "LOGLEVEL" : "WARNING",
            "RESPONSEDELAY" : "0"
        }
    }
}

RESOURCE_TAGS = {
    "tag_list" : {
        "exampletag1" : "examplevalue1",
        "exampletag2" : "examplevalue2"
    }
}