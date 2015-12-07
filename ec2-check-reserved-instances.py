#!/usr/bin/python

import sys
import os
import boto
from pprint import pprint

# You can uncomment and set these, or set the env variables AWSAccessKeyId & AWSSecretKey
# AWS_ACCESS_KEY_ID="aaaaaaaaaaaaaaaaaaaa"
# AWS_SECRET_ACCESS_KEY="bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"

try:
    AWS_ACCESS_KEY_ID
except NameError:
    try:
        AWS_ACCESS_KEY_ID = os.environ['AWSAccessKeyId']
        AWS_SECRET_ACCESS_KEY = os.environ['AWSSecretKey']
    except KeyError:
        print "Please set env variable"
        sys.exit(1)

ec2_conn = boto.connect_ec2(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
reservations = ec2_conn.get_all_instances()

running_instances_vpc = {}
running_instances_ec2_classic = {}
for reservation in reservations:
    for instance in reservation.instances:
        if instance.state == "running":
            az = instance.placement
            instance_type = instance.instance_type
            if instance.vpc_id:
                running_instances_vpc[(instance_type, az)] = running_instances_vpc.get((instance_type, az), 0) + 1
            else:
                running_instances_ec2_classic[(instance_type, az)] = running_instances_ec2_classic.get((instance_type, az), 0) + 1

# pprint( running_instances )

reserved_instances_vpc = {}
reserved_instances_ec2_classic = {}
for reserved_instance in ec2_conn.get_all_reserved_instances():
    if reserved_instance.state == "active":
        az = reserved_instance.availability_zone
        instance_type = reserved_instance.instance_type
        instance_count = reserved_instance.instance_count
        if reserved_instance.description == "Linux/UNIX (Amazon VPC)":
            reserved_instances_vpc[(instance_type, az)] = reserved_instances_vpc.get((instance_type, az), 0) + instance_count
        else:
            reserved_instances_ec2_classic[(instance_type, az)] = reserved_instances_ec2_classic.get((instance_type, az), 0) + instance_count

# pprint( reserved_instances )


print "\nVPC Instances:"
print "-------------------------------------------------------"
for reserved_instance in reserved_instances_vpc:
    if reserved_instance in running_instances_vpc:
        print "Reserved/Running:\t(%s/%s)\t%s\t%s" % (reserved_instances_vpc[reserved_instance], running_instances_vpc[reserved_instance], reserved_instance[0], reserved_instance[1])

instance_diff_vpc = dict([(x, reserved_instances_vpc[x] - running_instances_vpc.get(x, 0)) for x in reserved_instances_vpc])
for placement_key in instance_diff_vpc:
    if placement_key not in reserved_instances_vpc:
        instance_diff_vpc[placement_key] = -running_instances_vpc[placement_key]

print ""

unused_reservations_vpc = dict((key, value) for key, value in instance_diff_vpc.iteritems() if value > 0)
if unused_reservations_vpc == {}:
    print "Congratulations, you have no unused vpc instance reservations"
else:
    for unused_reservation in unused_reservations_vpc:
        print "UNUSED RESERVATION!\t(%s)\t%s\t%s" % (unused_reservations_vpc[unused_reservation], unused_reservation[0], unused_reservation[1])

qty_running_instances_vpc = reduce(lambda x, y: x + y, running_instances_vpc.values())
qty_reserved_instances_vpc = reduce(lambda x, y: x + y, reserved_instances_vpc.values())
print "\n(%s) running on-demand vpc instances\n(%s) vpc instance reservations\n" % (qty_running_instances_vpc, qty_reserved_instances_vpc)

print "======================================================="

print "\nEC2-Classic Instances:"
print "-------------------------------------------------------"
for reserved_instance in reserved_instances_ec2_classic:
    if reserved_instance in running_instances_ec2_classic:
        print "Reserved/Running:\t(%s/%s)\t%s\t%s" % (reserved_instances_ec2_classic[reserved_instance], running_instances_ec2_classic[reserved_instance], reserved_instance[0], reserved_instance[1])

print ""

instance_diff_ec2_classic = dict([(x, reserved_instances_ec2_classic[x] - running_instances_ec2_classic.get(x, 0)) for x in reserved_instances_ec2_classic])
for placement_key in running_instances_ec2_classic:
    if placement_key not in reserved_instances_ec2_classic:
        instance_diff_ec2_classic[placement_key] = -running_instances_ec2_classic[placement_key]

unused_reservations_ec2_classic = dict((key, value) for key, value in instance_diff_ec2_classic.iteritems() if value > 0)
if unused_reservations_ec2_classic == {}:
    print "Congratulations, you have no unused ec2-classic reservations"
else:
    for unused_reservation in unused_reservations_ec2_classic:
        print "UNUSED RESERVATION!\t(%s)\t%s\t%s" % (unused_reservations_ec2_classic[unused_reservation], unused_reservation[0], unused_reservation[1])

qty_running_instances_ec2_classic = reduce(lambda x, y: x + y, running_instances_ec2_classic.values())
qty_reserved_instances_ec2_classic = reduce(lambda x, y: x + y, reserved_instances_ec2_classic.values())
print "\n(%s) running on-demand ec2-classic instances\n(%s) ec2-classic instance reservations\n" % (qty_running_instances_ec2_classic, qty_reserved_instances_ec2_classic)

print "======================================================="

# unreserved_instances_ec2_classic = dict((key, -value) for key, value in instance_diff_ec2_classic.iteritems() if value < 0)
# if unreserved_instances_ec2_classic == {}:
#     print "Congratulations, you have no unreserved instances"
# else:
#     for unreserved_instance in unreserved_instances_ec2_classic:
#         print "Instance not reserved:\t(%s)\t%s\t%s" % (unreserved_instances_ec2_classic[unreserved_instance], unreserved_instance[0], unreserved_instance[1])

