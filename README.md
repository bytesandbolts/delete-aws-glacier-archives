# delete-aws-glacier-archives

A simple Python script to delete all archives in a given AWS Glacier Vault 

Takes the json archive list collected for an AWS vault and deletes all listed archives. 
It backups the original json file with extension .bak and pops every deleted archive from the list. Every 10 minutes or when stopping the script with Ctrl+C, the list gets exported back into json file. From then You can restart the process with the same command, it will continue from where it was. 
After finished, an inventory is initiated, otherwise deletion of the vault still would be not possible.

## Getting started
You have to install arnparse: `pip install arnparse`

See this for how to create the json file: https://docs.aws.amazon.com/amazonglacier/latest/dev/deleting-an-archive-using-cli.html

Then pass the json file with the inventory like this: `./glacier_delete.py output.json`


