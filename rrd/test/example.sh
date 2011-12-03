#!/bin/bash -x

RRDTOOL=/usr/bin/rrdtool
RRD_FILE=test.rrd
RRD_IMAGE=$RRD_FILE.png
VARIABLE=Variable
SOURCE_TYPE=GAUGE  # GAUGE,COUNTER
COLOR1=0000FF


$RRDTOOL create $RRD_FILE --start 1321922514 --step 60 DS:$VARIABLE:$SOURCE_TYPE:120:U:U RRA:AVERAGE:0.5:1:10

$RRDTOOL update $RRD_FILE 1321922580:213
$RRDTOOL update $RRD_FILE 1321922640:253
$RRDTOOL update $RRD_FILE 1321922700:213
$RRDTOOL update $RRD_FILE 1321922760:213
$RRDTOOL update $RRD_FILE 1321922820:713
$RRDTOOL update $RRD_FILE 1321922880:333
$RRDTOOL update $RRD_FILE 1321922940:913
$RRDTOOL update $RRD_FILE 1321923000:13
$RRDTOOL update $RRD_FILE 1321923060:113
$RRDTOOL update $RRD_FILE 1321923120:23
$RRDTOOL update $RRD_FILE 1321923180:23

$RRDTOOL fetch $RRD_FILE AVERAGE --start 1321922574 --end 1321923274

$RRDTOOL graph $RRD_IMAGE --start 1321922580 --end 1321923180 --vertical-label $VARIABLE DEF:v_$VARIABLE=$RRD_FILE:$VARIABLE:AVERAGE AREA:v_$VARIABLE#$COLOR1