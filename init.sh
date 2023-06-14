#!/bin/bash

working_dir=$( pwd )

#Build folder tree
echo $working_dir

echo "/log" >> $working_dir/.gitignore
echo "/res" >> $working_dir/.gitignore

if [ ! -d $working_dir/res ]
then
	mkdir $working_dir/res
fi

if [ ! -d $working_dir/log ]
then
	mkdir $working_dir/log
	touch $working_dir/log/bot.log
    touch $working_dir/log/preview.log
fi

if [ -f $( pwd )/conf.json ]
then

    
# Check if .bashrc contains the statement
    if grep -q "export BOT_CONF_FILE=" ~/.bashrc; then
        echo ".bashrc contains the statement"
    else
        echo ".bashrc does not contain the statement"
        echo "export BOT_CONF_FILE=$( pwd )/conf.json" >> ~/.bashrc
    fi

    # Check if .bash_profile contains the statement
    if grep -q "export BOT_CONF_FILE=" ~/.bash_profile; then
        echo ".bash_profile contains the statement"
    else
        echo ".bash_profile does not contain the statement"
        echo "export BOT_CONF_FILE=$( pwd )/conf.json" >> ~/.bash_profile
    fi

    source ~/.bashrc
    #source ~/.bash_profile

    git update-index --skip-worktree conf.json

    # Read the JSON file
    json_data=$(cat $BOT_CONF_FILE)

    if ! command -v jq &> /dev/null
    then
        sudo apt install jq
    fi
    
    # Parse the JSON data and update the field "HOME" with the value of the current directory
    json_data=$(echo $json_data | jq --arg dir "$working_dir/" '.HOME = $dir')
    json_data=$(echo $json_data | jq --arg dir "$working_dir/log/bot.log" '.bot_log = $dir')
    json_data=$(echo $json_data | jq --arg dir "$working_dir/log/preview.log" '.preview_log = $dir')

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
