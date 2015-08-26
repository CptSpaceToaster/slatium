#!/bin/bash
while [ 1 ]
do
    ./main.py -s

    secs=$((5))

    while [ $secs -gt 0 ]; do
        echo -ne "Restarting in $secs\033[0K\r"
        sleep 1
        : $((secs--))
    done
done
