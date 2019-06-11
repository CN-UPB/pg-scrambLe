# [SONATA](http://www.sonata-nfv.eu)'s Gatekeeper MANO Management micro-service
[![Build Status](http://jenkins.sonata-nfv.eu/buildStatus/icon?job=son-gkeeper)](http://jenkins.sonata-nfv.eu/job/son-gkeeper)

This is the folder of the **MANO Management** micro-service. This micro-service is used by the [`Gatekeeper API`](https://github.com/sonata-nfv/son-gkeeper/son-gtkapi).

## Configuration
The configuration of the Gatekeeper's MANO Management micro-service is done mostly by defining `ENV` variables in the [`Dockerfile`](https://github.com/sonata-nfv/son-gkeeper/blob/master/son-gtkmano/Dockerfile). These variables are:

* `PORT`: the port the micro-service is to provide it's services, currently `5700`;
* `CATALOGUE_URL`: the URL of the catalogues service, currently `http://catalogues:4002/catalogues`;
* `POSTGRES_PASSWORD` : the postgres password, currently Dockerfile uses `sonata` as default;
* `POSTGRES_USER` : the postgres user, currently Dockerfile uses `sonatatest` as default;
* `DATABASE_HOST` : the postgres host, should be the IP address of postgres database, currently `postgres`;
* `DATABASE_PORT` : the postgres port, is the default postgres tcp port, currently `5432`;
* `MQSERVER` : the AMQP uri, currently `amqp://guest:guest@broker:5672`;

## Usage
To use this application, we write
```sh
$ foreman start
```

[`Foreman`](https://github.com/ddollar/foreman) is a `ruby gem` for managing applications based on a [`Procfile`](https://github.com/sonata-nfv/son-gkeeper/blob/master/son-gtkrec/Procfile).

### Implemented API
The implemented API of the Gatekeeper is the following:

* `/mano`:
    * `GET`: provides a list of MANOs, available in the infrabstructure abstraction;
    	* `/:uuid`: provides the service record data with the given `:uuid`;
    * `POST`: creates a new mano registry for the infrabstructure abstraction
* `/mano_request`:
    * `GET`: provides a list of mano request;
    * `/:uuid/?`: provides the status of the request data with the given `:uuid`;

**Note 1:** `PUT`and `DELETE`operations are already supported by some of the micro-services, and will be described in the next version(s);

**Note 2:** all `GET`operations support pagination, though this still needs some work. This pagination can be done by using the `offset` and `limit` parameters, like in:
```sh
$ curl <resource_url>?offset=0,limit=10
```
This command will result in a list of `10`values (the `limit`) of the first page (`offset` zero). These are the default values used for those parameters.

## Tests
At the module level, we only do **automated unit tests**, using the `RSpec` framework (see the `./spec/`folder). For the remaining tests please see the repositorie's [`README`](https://github.com/sonata-nfv/son-gkeeper/blob/master/README.md) file.

