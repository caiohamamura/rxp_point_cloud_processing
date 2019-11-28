#!/usr/bin/bash

location="$1"
append="$2"
ls -1 $location/*day1_loc1*.txt > d1l1${append}.txt
ls -1 $location/*day2_loc1*.txt > d2l1${append}.txt
ls -1 $location/*day1_loc2*.txt > d1l2${append}.txt
ls -1 $location/*day2_loc2*.txt > d2l2${append}.txt
ls -1 $location/*entry1*.txt > entry1${append}.txt
ls -1 $location/*entry2*.txt > entry2${append}.txt
