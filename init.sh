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

if [ -f $( pwd )/conf.json ]
then
    echo "export BOT_CONF_FILE=$(pwd)/conf.json" >> ~/.bashrc
    echo "export BOT_CONF_FILE=$(pwd)/conf.json" >> ~/.bash_profile
    source ~/.bashrc
    source ~/.bash_profile

    git update-index --skip-worktree conf.json

    # Read the JSON file
    json_data=$(cat $BOT_CONF_FILE)

    # Parse the JSON data and update the field "HOME" with the value of the current directory
    json_data=$(echo $json_data | jq --arg dir "$working_dir/" '.HOME = $dir')
    json_data=$(echo $json_data | jq --arg dir "$working_dir/log/bot.log" '.Log_directory = $dir')

    # Write the updated JSON data back to the file
    echo $json_data > $BOT_CONF_FILE
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
pip3 install -r requirements.txt
