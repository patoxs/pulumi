"""An AWS Python Pulumi program"""

import pulumi
import pulumi_aws as aws

config = pulumi.Config()
region = aws.get_region().id
vpc = config.require('nombre_vpc')

def crear_subnet(nombre, cidr, zona, ip_lunch):
    subnet = aws.ec2.Subnet(
        nombre,
        vpc_id=vpc_principal.id,
        cidr_block=cidr,
        tags={
            "Name": nombre,
        },
        availability_zone=region+zona,
        map_public_ip_on_launch=ip_lunch,
        opts = pulumi.ResourceOptions(depends_on=[vpc_principal])
    )
    return subnet

vpc_principal = aws.ec2.Vpc(
    "vpc_principal",
    cidr_block="10.0.0.0/16",
    tags = {'Name':'VPC Principal'}
)

subnet_publica = config.require_object("subnet_publica")
nombre = subnet_publica.get("nombre")
cidr = subnet_publica.get("cidr")
zona = subnet_publica.get("zona")
ip_lunch = subnet_publica.get("ip_lunch")
subnet_publica = crear_subnet(nombre, cidr, zona, ip_lunch)

subnet_privada = config.require_object("subnet_privada")
nombre = subnet_privada.get("nombre")
cidr = subnet_privada.get("cidr")
zona = subnet_privada.get("zona")
ip_lunch = subnet_privada.get("ip_lunch")
subnet_privada = crear_subnet(nombre, cidr, zona, ip_lunch)


gw = aws.ec2.InternetGateway(
    "internet_gateway",
    vpc_id=vpc_principal.id,
    tags={
        "Name": "internet_gateway",
    },
    opts = pulumi.ResourceOptions(depends_on=[vpc_principal])
)

elastic_ip = aws.ec2.Eip(
    "elastic_ip",
    vpc=True,
    tags={
        "Name": "elastic_ip",
    },
)

ng = aws.ec2.NatGateway(
    "nat_gateway",
    allocation_id=elastic_ip.id,
    subnet_id=subnet_publica.id,
    tags={
        "Name": "nat_gateway",
    },
    opts=pulumi.ResourceOptions(depends_on=[vpc_principal])
)


### tablas de rutas ###
route_table_public = aws.ec2.RouteTable("public",
    vpc_id=vpc_principal.id,
    routes=[
        aws.ec2.RouteTableRouteArgs(
            cidr_block= "0.0.0.0/0",
            gateway_id=gw.id,
        )
    ],
    tags={
        "Name": "rt_public",
    },
    opts=pulumi.ResourceOptions(depends_on=[gw, vpc_principal])
)

route_table_nat = aws.ec2.RouteTable("nat",
    vpc_id=vpc_principal.id,
    routes=[
        aws.ec2.RouteTableRouteArgs(
            cidr_block= "0.0.0.0/0",
            gateway_id=ng.id,
        )
    ],
    tags={
        "Name": "rt_nat", 
    },
    opts=pulumi.ResourceOptions(depends_on=[gw, vpc_principal])
)

route_table_private = aws.ec2.RouteTable("privada",
    vpc_id=vpc_principal.id,
    routes=[],
    tags={
        "Name": "rt_privada",
    },
    opts=pulumi.ResourceOptions(depends_on=[gw, vpc_principal])
)


pulumi.export('vpc_arn', vpc_principal.arn)
pulumi.export('vpc_id', vpc_principal.id)
pulumi.export('subnet_publica', subnet_publica.id)
pulumi.export('subnet_privada', subnet_privada.id)
pulumi.export('internet_gateway', gw.id)
pulumi.export('nat_gateway', ng.id)