#!/bin/bash

working_dir=$( pwd )

#Build folder tree
echo $working_dir

if [ ! -d $working_dir/res ]
then
	mkdir $working_dir/res
fi

if [ ! -d $working_dir/log ]
then
	mkdir $working_dir/log
	touch $working_dir/log/bot.log
fi

#Check other dependencies
if ! command -v python3 &> /dev/null
then
    echo "python3 could not be found. Installing python3"
    sudo apt install python3 -y
    #exit
fi

if ! command -v pip &> /dev/null
then
    echo "python3-pip could not be found. Installing python3-pip"
    sudo apt install python3-pip -y
    #exit
fi

#Set x-permission
chmod +x $working_dir/bot.py

#Install dependencies
pip install -r requirements
