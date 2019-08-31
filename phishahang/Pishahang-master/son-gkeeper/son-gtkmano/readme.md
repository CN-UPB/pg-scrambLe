son-gtk mano

to run

1. cd into the folder
2. sudo docker-compose build
3. sudo docker-compose up -d

Get/Post:

1. localhost:8001/mano_create - method post

json body example - 

{"mano _type": "OSM",
 "mano_name": "submano",
 "mano_address": "www.google.com",
 "mano_city": "paderborn",
 "mano-country": "Germany",
 "mano_user": "xyz",
 "mano_pass": "1234"}

return: uuid

2. localhost:8001/mano - method get

return: all mano details in python dict

3. localhost:8001/mano_uuid? - method get

Json body: "_id":"uuid"

return: details of particular mano 

4. localhost:8001/mano_remove? - method get

Json body: "_id":"uuid"

return: success if uuid exists


