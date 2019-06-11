from flask import Flask, render_template
app = Flask(__name__)

import sys
import docker
client = docker.DockerClient(base_url='unix://container/path/docker.sock')

DOCKER_EXCLUDE = ['experiment-runner']

@app.route('/')
def index_html():
    # print(client.containers.list(), file=sys.stderr)
    docker_list = {}
    for _container in client.containers.list():        
        if not _container.attrs["Name"][1:] in DOCKER_EXCLUDE:
            docker_list[_container.attrs["Name"][1:]] = _container.attrs["Id"]
        
    return render_template('index.html', docker_list=docker_list)

@app.route('/interactive')
def interactive_html():
    # print(client.containers.list(), file=sys.stderr)
    docker_list = {}
    for _container in client.containers.list():
        
        if not _container.attrs["Name"][1:] in DOCKER_EXCLUDE:
            docker_list[_container.attrs["Name"][1:]] = _container.attrs["Id"]
        
    return render_template('index-interactive.html', docker_list=docker_list)

@app.route('/save-experiment-data')
def save_data():
    # Print GET data
    # Make a list_url_query = [] 

    # http://${host}:19999/api/v1/data?chart=system.cpu&after=${after}&before=${before}&format=datasource&options=nonzero
    # http://${host}:19999/api/v1/data?chart=system.load&after=${after}&before=${before}&format=datasource&options=nonzero
    # http://${host}:19999/api/v1/data?chart=system.ram&format=datasource&after=${after}&before=${before}&options=nonzero
    # http://${host}:19999/api/v1/data?chart=system.net&format=datasource&after=${after}&before=${before}&group=average&gtime=0&datasource&options=nonzeroseconds
    # http://${host}:19999/api/v1/data?chart=system.io&format=datasource&after=${after}&before=${before}&group=average&gtime=0&datasource&options=nonzeroseconds


    # http://${host}:19999/api/v1/data?chart=cgroup_{{ _name }}.cpu_per_core&format=datasource&after=${after}&before=${before}&group=average&gtime=0&datasource&options=nonzeroseconds
    # http://${host}:19999/api/v1/data?chart=cgroup_{{ _name }}.throttle_io&format=datasource&after=${after}&before=${before}&group=average&gtime=0&datasource&options=nonzeroseconds
    # http://${host}:19999/api/v1/data?chart=cgroup_{{ _name }}.mem_usage&format=datasource&after=${after}&before=${before}&group=average&gtime=0&datasource&options=nonzeroseconds


    docker_list = {}
    for _container in client.containers.list():        
        if not _container.attrs["Name"][1:] in DOCKER_EXCLUDE:
            docker_list[_container.attrs["Name"][1:]] = _container.attrs["Id"]
            # format url and list_url_query.append() 

    return render_template('index.html', docker_list=docker_list)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9000)
