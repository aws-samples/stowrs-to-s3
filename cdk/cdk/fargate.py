"""
Classes creating Fargate tasks and service.
SPDX-License-Identifier: Apache 2.0
"""

from constructs import Construct
from aws_cdk import (aws_ec2 as ec2, aws_ecs as ecs, aws_ecs_patterns as ecs_patterns , aws_ecr as ecr , aws_iam as iam)
from aws_cdk.aws_ecr_assets import DockerImageAsset
from aws_cdk.aws_ecs import PortMapping , Protocol
from .nlb import StowNLB

import cdk_nag


class FargateService(Construct):

    def __init__(self, scope: Construct, id: str,  vpc: ec2.Vpc , task_role: iam.IRole , task_definition , dicom_bucket_name: str , certificate_bucket_name: str ,  allowed_peers , loadbalancer: StowNLB , authentication_mode: str, certificate_mode: str , **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        cluster = ecs.Cluster(scope, "FargateService", vpc=vpc)


        nginx_container_dir = task_definition["nginx_container"]["source_directory"]
        nginx_container = DockerImageAsset(self, "stowrstos3-nginx", directory=nginx_container_dir )

        app_container_dir = task_definition["app_container"]["source_directory"]
        app_container = DockerImageAsset(self, "stowrstos3-app", directory=app_container_dir )

        task_def = FargateTaskDefinition(self, "task_definition" , task_definition=task_definition , nginx_container=nginx_container , app_container=app_container , dicom_bucket_name=dicom_bucket_name , certificate_bucket_name=certificate_bucket_name ,  task_role=task_role , authentication_mode=authentication_mode , certificate_mode=certificate_mode )
        
        
        security_grp = ec2.SecurityGroup(self, "Task-SG" , vpc=vpc , allow_all_outbound=True, description="stowrstos3 security group." , security_group_name="stowrstos3-SG" )

        #This allows everyone to connect to the endpoint from the internet.
        for peer in allowed_peers["peer_list"]:
            security_grp.add_ingress_rule(peer= ec2.Peer.ipv4(peer) ,connection=ec2.Port.tcp(443) , description=f"Allows HTTPS from CIDR {peer}")

        #this allows the Network Load balancer private IP to health checks the nginx-container.
        for subnet in vpc.isolated_subnets:
            security_grp.add_ingress_rule(peer= ec2.Peer.ipv4(subnet.ipv4_cidr_block) ,connection=ec2.Port.tcp(443) , description=f"DOT NOT DELETE - Allows NLB monitoring from IPs in subnet {subnet.ipv4_cidr_block}.")

        task_count = task_definition["task_count"]
        FGservice = ecs.FargateService(self, id="service", cluster=cluster, task_definition=task_def.getTaskDefinition() , assign_public_ip=True , desired_count=task_count , vpc_subnets=vpc.private_subnets , security_groups=[security_grp]  )
        FGservice.attach_to_network_target_group(loadbalancer.getTargetGroup())

    

class FargateTaskDefinition(Construct):

    _fargate_task_definition = None
    def __init__(self, scope: Construct, id: str, task_definition , nginx_container , app_container , dicom_bucket_name: str , certificate_bucket_name: str ,  task_role: iam.IRole , authentication_mode: str , certificate_mode ,**kwargs) -> None :
        super().__init__(scope, id, **kwargs)

        task_memory = task_definition["memory"]
        task_cpu = task_definition["cpu"]

        nginx_container_memory = task_definition["nginx_container"]["memory"]
        nginx_container_cpu = task_definition["nginx_container"]["cpu"]

        app_container_memory = task_definition["app_container"]["memory"]
        app_container_cpu = task_definition["app_container"]["cpu"]

        self._fargate_task_definition = ecs.FargateTaskDefinition(self, id, memory_limit_mib=task_memory, cpu=task_cpu , task_role=task_role)
        nginxContainer = self._fargate_task_definition.add_container("nginx-container",image=ecs.ContainerImage.from_docker_image_asset(nginx_container) , logging=ecs.LogDrivers.aws_logs(stream_prefix="nginx-container" ) )
        nginxContainer.add_port_mappings(ecs.PortMapping(container_port=443, host_port=443))
        nginxContainer.add_environment("AUTH_MODE", authentication_mode)
        nginxContainer.add_environment("CERT_MODE", certificate_mode)
        if(certificate_mode.upper() == "FROMS3"):
            nginxContainer.add_environment("CERT_BUCKETNAME", certificate_bucket_name)

        appContainer = self._fargate_task_definition.add_container("app-container",image=ecs.ContainerImage.from_docker_image_asset(app_container) , logging=ecs.LogDrivers.aws_logs(stream_prefix="app-container" ) )
        appContainer.add_port_mappings(ecs.PortMapping(container_port=8080, host_port=8080))
        #Add all the env variables found in the container config.
        for envkey in task_definition["app_container"]["envs"]:
            appContainer.add_environment(envkey , task_definition["app_container"]["envs"][envkey])
        #Add the last env variable correpsonding to the bucket name where to store DICOM images.
        appContainer.add_environment("BUCKETNAME", dicom_bucket_name )
           
    def getTaskDefinition(self):
        return self._fargate_task_definition