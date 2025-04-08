"""An AWS Python Pulumi program"""

import pulumi
import pulumi_aws as aws

# Configuración
ami_name_filter = "Cloud9Ubuntu22-2025-03-25T05-29"  # Filter for Cloud9 AMI
key_name = "vockey"  # Existing Key Pair in AWS
instance_type = "t2.micro"  # You can change this based on your needs
volume_size = 20  # GiB

# Buscar la AMI más reciente de Cloud9 en la región actual
amis = aws.ec2.get_ami(
    most_recent=True,
    owners=["amazon"],  # Owner of the Cloud9 AMIs
    filters=[
        aws.ec2.GetAmiFilterArgs(
            name="name",
            values=[ami_name_filter],
        ),
        aws.ec2.GetAmiFilterArgs(
            name="architecture",
            values=["x86_64"],
        ),
        aws.ec2.GetAmiFilterArgs(
            name="virtualization-type",
            values=["hvm"],
        ),
    ],
)

# Crear un grupo de seguridad que permita el tráfico SSH (puerto 22) y HTTP (puerto 80)
security_group = aws.ec2.SecurityGroup(
    "web-sg",
    description="Enable SSH and HTTP access",
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=22,
            to_port=22,
            cidr_blocks=["0.0.0.0/0"],  # WARNING: This allows SSH from anywhere
            description="SSH Access",
        ),
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=80,
            to_port=80,
            cidr_blocks=["0.0.0.0/0"],  # HTTP from anywhere
            description="HTTP Access",
        ),
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            protocol="-1",
            from_port=0,
            to_port=0,
            cidr_blocks=["0.0.0.0/0"],
        ),
    ],
)

# Crear una instancia EC2
instance = aws.ec2.Instance(
    "web-server-www",
    ami=amis.id,
    instance_type=instance_type,
    key_name=key_name,
    vpc_security_group_ids=[security_group.id],
    root_block_device=aws.ec2.InstanceRootBlockDeviceArgs(
        volume_size=volume_size,
        volume_type="gp2",  # General Purpose SSD
        delete_on_termination=True,
    ),
    tags={
        "Name": "web-server",
    },
)

# Exportar la IP pública de la instancia
pulumi.export("public_ip", instance.public_ip)
pulumi.export("public_dns", instance.public_dns)
