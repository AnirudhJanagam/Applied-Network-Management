#!/bin/bash



filter=$1

tag=$2

user=admin
passwd=admin
host=192.168.185.71
db=anm

while(true) ; do

sudo bitrate -i ens4 01::71 01::72 $mstream --$filter --format=influx --influx-user="admin" --influx-pwd="admin" --influx-tag="$tag" --influx-url="http://localhost:8086/write?db=anm"

sleep 10;

done
