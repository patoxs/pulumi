import pulumi
import pulumi_aws as aws

def crear_vpc(nombre_vpc, cidr_block):
    vpc = aws.ec2.Vpc(
        nombre_vpc,
        cidr_block=cidr_block,
        enable_dns_hostnames=True,
        tags = {'Name':nombre_vpc}
    )
    return vpc

def crear_subnet(vpc, nombre, cidr, region, zona):
    subnet = aws.ec2.Subnet(
        nombre,
        vpc_id=vpc.id,
        cidr_block=cidr,
        tags={
            "Name": nombre,
        },
        availability_zone=region+zona,
        map_public_ip_on_launch=True,
        opts = pulumi.ResourceOptions(depends_on=[vpc])
    )
    return subnet

def crear_internet_gateway(nombre_ig, vpc):
    ig = aws.ec2.InternetGateway(
        nombre_ig,
        vpc_id=vpc.id,
        tags={
            "Name": nombre_ig,
        },
        opts = pulumi.ResourceOptions(depends_on=[vpc])
    )
    return ig

def crear_eip(nombre_eip):
    eip = aws.ec2.Eip(
        nombre_eip,
        vpc=True,
        tags={
            "Name": nombre_eip,
        },
    )
    return eip

def crear_nat_gateway(nombre_ng, eip, subnet, vpc):
    ng = aws.ec2.NatGateway(
        nombre_ng,
        allocation_id=eip.id,
        subnet_id=subnet.id,
        tags={
            "Name": nombre_ng,
        },
        opts=pulumi.ResourceOptions(depends_on=[vpc])
    )
    return ng

def crear_route_table_publica(nombre_rt_public, vpc, ig):
    route_table_public = aws.ec2.RouteTable(
        nombre_rt_public,
        vpc_id=vpc.id,
        routes=[
            aws.ec2.RouteTableRouteArgs(
                cidr_block= "0.0.0.0/0",
                gateway_id=ig.id,
            )
        ],
        tags={
            "Name": nombre_rt_public,
        },
        opts=pulumi.ResourceOptions(depends_on=[ig, vpc])
    )
    return route_table_public

def crear_route_table_nat(nombre_rt_nat, vpc, ng):
    route_table_nat = aws.ec2.RouteTable(
        nombre_rt_nat,
        vpc_id=vpc.id,
        routes=[
            aws.ec2.RouteTableRouteArgs(
                cidr_block= "0.0.0.0/0",
                gateway_id=ng.id,
            )
        ],
        tags={
            "Name": nombre_rt_nat, 
        },
        opts=pulumi.ResourceOptions(depends_on=[ng, vpc])
    )
    return route_table_nat

def crear_route_table_privada(nombre_rt_privada, vpc):
    route_table_privada = aws.ec2.RouteTable(
        nombre_rt_privada,
        vpc_id=vpc.id,
        routes=[],
        tags={
            "Name": nombre_rt_privada,
        },
        opts=pulumi.ResourceOptions(depends_on=[vpc])
    )
    return route_table_privada

def crear_route_table_association(nombre_route_table_association, route_table, subnet):
    route_table_association = aws.ec2.RouteTableAssociation(
        nombre_route_table_association,
        subnet_id=subnet.id,
        route_table_id=route_table.id,
        opts=pulumi.ResourceOptions(depends_on=[route_table])
    )
    return route_table_association