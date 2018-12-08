#!/bin/bash


timeout=$1

echo "will wait $timeout"

sleep $timeout

echo "killing capshow"

sudo pkill capshow

echo "done"
