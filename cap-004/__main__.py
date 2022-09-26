import pulumi
import pulumi_aws as aws
import pulumi_command as command
import json
import uuid

import network

config = pulumi.Config()
region = aws.get_region().id

# get config network
vpc_cidr = config.require('vpc_cidr')
subnet_publica_cidr = config.require('subnet_publica')
subnet_privada_cidr = config.require('subnet_privada')

# create network
vpc = network.crear_vpc("vpc_test", vpc_cidr)
subnet_publica = network.crear_subnet(vpc, "subnet_publica_test", subnet_publica_cidr, region, 'a')
subnet_private = network.crear_subnet(vpc, "subnet_private_test", subnet_privada_cidr, region, 'b')
ig = network.crear_internet_gateway("ig_test", vpc)
eip = network.crear_eip("eip_test")
ng = network.crear_nat_gateway("ng_test", eip, subnet_publica, vpc)
rtpub = network.crear_route_table_publica("rt_publica_test", vpc, ig)
rtnat = network.crear_route_table_nat("rt_nat_test", vpc, ng)
rtpri = network.crear_route_table_privada("rt_privada_test",vpc)
rt_asoc_pub = network.crear_route_table_association("rta_publica_test", rtpub, subnet_publica)
rt_asoc_pri = network.crear_route_table_association("rta_privada_test", rtpri, subnet_private)


# db_instance_size = config.require("db_instance_size")
# ec2_instance = config.require("ec2_instance")
# db_name = config.require("db_name")
# db_username = config.require("db_username")
# db_password = config.require("db_password")

# # # A path to the EC2 keypair's public key:
# public_key_path = config.require("publicKeyPath")
# # # A path to the EC2 keypair's private key:
# private_key_path = config.require("privateKeyPath")
# # # Read in the public key for easy use below.
# public_key = open(public_key_path).read()
# # # Read in the private key for easy use below (and to ensure it's marked a secret!)
# private_key = pulumi.Output.secret(open(private_key_path).read())

# wordpress_keypair = aws.ec2.KeyPair("wordpress-keypair", public_key=public_key)

# aws_linux_ami = aws.ec2.get_ami(
#     owners=["136693071363"],
#     filters=[aws.ec2.GetAmiFilterArgs(
#         name="name",
#         values=["debian-11-amd64-*"],
#     )],
#     most_recent=True
# )

# # #Security group for ec2
# ec2_allow_rule = aws.ec2.SecurityGroup("ec2-allow-rule",
#     vpc_id=vpc.id,
#     ingress=[
#         aws.ec2.SecurityGroupIngressArgs(
#             description="HTTPS",
#             from_port=443,
#             to_port=443,
#             protocol="tcp",
#             cidr_blocks=["0.0.0.0/0"],
#         ),
#         aws.ec2.SecurityGroupIngressArgs(
#             description="HTTP",
#             from_port=80,
#             to_port=80,
#             protocol="tcp",
#             cidr_blocks=["0.0.0.0/0"],
#         ),
#         aws.ec2.SecurityGroupIngressArgs(
#             description="SSH",
#             from_port=22,
#             to_port=22,
#             protocol="tcp",
#             cidr_blocks=["0.0.0.0/0"],
#         ),
#     ],
#     egress=[aws.ec2.SecurityGroupEgressArgs(
#         from_port=0,
#         to_port=0,
#         protocol="-1",
#         cidr_blocks=["0.0.0.0/0"],
#     )],
#     tags={
#         "Name": "allow ssh,http,https",
#     }
# )

# # # Security group for RDS:
# rds_allow_rule = aws.ec2.SecurityGroup("rds-allow-rule",
#     vpc_id=vpc.id,
#     ingress=[aws.ec2.SecurityGroupIngressArgs(
#         description="MySQL",
#         from_port=3306,
#         to_port=3306,
#         protocol="tcp",
#         security_groups=[ec2_allow_rule.id],
#     )],
#     tags={
#         "Name": "allow port 3306",
#     }
# )

# rds_subnet_grp = aws.rds.SubnetGroup(
#     "rds-subnet-grp", 
#     subnet_ids=[
#         subnet_private.id,
#         subnet_publica.id,
#     ]
# )


# # # Create the RDS instance:
# wordpressdb = aws.rds.Instance(
#     "wordpressdb",
#     identifier="wordpressdb",
#     allocated_storage=10,
#     engine="mysql",
#     engine_version="5.7",
#     instance_class=db_instance_size,
#     db_subnet_group_name=rds_subnet_grp.id,
#     vpc_security_group_ids=[rds_allow_rule.id],
#     db_name=db_name,
#     username=db_username,
#     password=db_password,
#     skip_final_snapshot=True,
#     tags={
#         "Name": "Wordpress Database",
#     }
# )

# # ###
# ec2_role = aws.iam.Role(
#     "role_ec2", 
#     assume_role_policy="""{
#         "Version": "2012-10-17",
#         "Statement": [
#             {
#                 "Effect": "Allow",
#                 "Action": "sts:AssumeRole",
#                 "Principal": {"Service":  "ec2.amazonaws.com"}
#             }
#         ]
#     }""",
#     tags={
#         "Name": "Role Wordpress server",
#     }
# )

# ec2_policy = aws.iam.Policy("policy_ec2",
#     description="Policy ec2 to RDS",
#     policy=pulumi.Output.all(wordpressdb.arn).apply(
#         lambda args: json.dumps({
#             "Version": "2012-10-17",
#             "Statement": [{
#                 "Sid": "VisualEditor0",
#                 "Effect": "Allow",
#                 "Action": [
#                     "rds-data:ExecuteSql",
#                     "rds-data:ExecuteStatement",
#                     "rds-data:BatchExecuteStatement",
#                     "rds-data:BeginTransaction",
#                     "rds-data:CommitTransaction",
#                     "rds-data:RollbackTransaction"
#                 ],
#                 "Resource": args[0]
#             },
#             {
#                 "Sid": "VisualEditor1",
#                 "Effect": "Allow",
#                 "Action": [
#                     "rds:Describe*",
#                     "rds:ListTagsForResource"
#                 ],
#                 "Resource": "*"
#             }]
#         })
#     )
# )


# ec2_attach = aws.iam.RolePolicyAttachment(
#     "ec2-attach",
#     role=ec2_role.name,
#     policy_arn=ec2_policy.arn
# )

# ec2_profile = aws.iam.InstanceProfile(
#     "ec2_profile", 
#     role=ec2_role.name
# )


# # Create server wordpress
# ec2 = aws.ec2.Instance(
#     "ec2_wordpress",
#     ami=aws_linux_ami.id,
#     instance_type=ec2_instance,
#     associate_public_ip_address=True,
#     key_name=wordpress_keypair.key_name,
#     vpc_security_group_ids=[ec2_allow_rule.id],
#     subnet_id=subnet_publica.id,
#     iam_instance_profile=ec2_profile.name,
#     tags={
#         "Name": "Wordpress server",
#     },
#     opts=pulumi.ResourceOptions(depends_on=[wordpressdb])
# )

# update = command.remote.Command("update_system",
#     connection=command.remote.ConnectionArgs(
#         host=ec2.public_ip,
#         port=22,
#         user="admin",
#         private_key=private_key,
#     ),
#     create="""(sudo apt update)""",
#     opts=pulumi.ResourceOptions(depends_on=[ec2])
# )

# # Install NGINX
# install_nginx = command.remote.Command("installNGINX",
#     connection=command.remote.ConnectionArgs(
#         host=ec2.public_ip,
#         port=22,
#         user="admin",
#         private_key=private_key,
#     ),
#     create="""(sudo apt update);
#         (sudo apt install nginx -y);
#         (sudo systemctl start nginx);
#         (sudo systemctl enable nginx);
#         (sudo nginx -v)
#         """,
#     opts=pulumi.ResourceOptions(depends_on=[ec2])
# )

# # Install PHP 
# install_php = command.remote.Command("installPHP",
#     connection=command.remote.ConnectionArgs(
#         host=ec2.public_ip,
#         port=22,
#         user="admin",
#         private_key=private_key,
#     ),
#     create="""(sudo apt update);
#         (sudo apt install php php-fpm php-curl php-cli php-zip php-mysql php-xml -y)
#         """,
#     opts=pulumi.ResourceOptions(depends_on=[install_nginx])
# )


# # Run a script to download Wordpress.
# download_wordpress = command.remote.Command("downloadWordpress",
#     connection=command.remote.ConnectionArgs(
#         host=ec2.public_ip,
#         port=22,
#         user="admin",
#         private_key=private_key,
#     ),
#     create="""(wget https://wordpress.org/latest.tar.gz -O wordpress.tar.gz);
#         (tar -xzvf wordpress.tar.gz);
#         (sudo mv wordpress /var/www/wordpress);
#         """,
#     opts=pulumi.ResourceOptions(depends_on=[install_php])
# )

# # Run a script to install PHP 7.4.
# enable_php = command.remote.Command("restartPHP",
#     connection=command.remote.ConnectionArgs(
#         host=ec2.public_ip,
#         port=22,
#         user="admin",
#         private_key=private_key,
#     ),
#     create="""(sudo systemctl enable php7.4-fpm);
#         (sudo systemctl status php7.4-fpm)
#         """,
#     opts=pulumi.ResourceOptions(depends_on=[download_wordpress])
# )



# #create wp-config from sample config file
# copy_wp_config = command.local.Command("copySampleConfig",
#     create="""(cp wp-config.sample wp-config.php)""",
#     opts=pulumi.ResourceOptions(depends_on=[enable_php])
# )

# # Render wordpress config.
# render_wp_config = command.local.Command("renderWpConfig",
#     create=pulumi.Output.all(wordpressdb.address).apply(
#         lambda args: f"""(sed -i 's/database_name_here/{db_name}/g' ./wp-config.php);
#         (sed -i 's/username_here/{db_username}/g' ./wp-config.php);
#         (sed -i 's/password_here/{db_password}/g' ./wp-config.php);
#         (sed -i 's/localhost/{args[0]}/g' ./wp-config.php);
#         (sed -i 's/hash_wp_1/{uuid.uuid4()}/g' ./wp-config.php);
#         (sed -i 's/hash_wp_2/{uuid.uuid4()}/g' ./wp-config.php);
#         (sed -i 's/hash_wp_3/{uuid.uuid4()}/g' ./wp-config.php);
#         (sed -i 's/hash_wp_4/{uuid.uuid4()}/g' ./wp-config.php);
#         (sed -i 's/hash_wp_5/{uuid.uuid4()}/g' ./wp-config.php);
#         (sed -i 's/hash_wp_6/{uuid.uuid4()}/g' ./wp-config.php);
#         (sed -i 's/hash_wp_7/{uuid.uuid4()}/g' ./wp-config.php);
#         (sed -i 's/hash_wp_8/{uuid.uuid4()}/g' ./wp-config.php)
#     """),
#     opts=pulumi.ResourceOptions(depends_on=[copy_wp_config])
# )

# # # Copy wp-config to server Wordpress.
# copy_wp_config = command.remote.CopyFile("copyWpconfig",
#     connection=command.remote.ConnectionArgs(
#         host=ec2.public_ip,
#         port=22,
#         user="admin",
#         private_key=private_key,
#     ),
#     local_path="./wp-config.php",
#     remote_path="/var/www/wordpress/wp-config.php",
#     opts=pulumi.ResourceOptions(depends_on=[copy_wp_config])
# )

# # # Copy nginx.conf to the server.
# copy_nginx_conf = command.remote.CopyFile("copyNginxConf",
#     connection=command.remote.ConnectionArgs(
#         host=ec2.public_ip,
#         port=22,
#         user="admin",
#         private_key=private_key,
#     ),
#     local_path="mysite-nginx.conf",
#     remote_path="/tmp/mysite.conf",
#     opts=pulumi.ResourceOptions(depends_on=[copy_wp_config])
# )

# # # Setup and starr nginx.
# setup_nginx = command.remote.Command("setupNginx",
#     connection=command.remote.ConnectionArgs(
#         host=ec2.public_ip,
#         port=22,
#         user="admin",
#         private_key=private_key,
#     ),
#     create="""(sudo cp /tmp/mysite.conf /etc/nginx/sites-available/default);
#         (sudo nginx -t);
#         (sudo systemctl restart nginx)
#         """,
#     opts=pulumi.ResourceOptions(depends_on=[copy_nginx_conf])
# )

# #create wp-config from sample config file
# delete_wp_config = command.local.Command("deleteFileConfigWP",
#     create="""(rm wp-config.php)""",
#     opts=pulumi.ResourceOptions(depends_on=[copy_wp_config])
# )

# pulumi.export("wordpress_address",wordpressdb.address)
# pulumi.export("dns_ec2", ec2.public_dns)
# pulumi.export("ip_ec2", ec2.public_ip)