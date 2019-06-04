from flask import Flask, render_template
app = Flask(__name__)

import sys
import docker
client = docker.DockerClient(base_url='unix://container/path/docker.sock')

@app.route('/')
def index_html():
    # print(client.containers.list(), file=sys.stderr)
    docker_list = {}
    for _container in client.containers.list():
        docker_list[_container.attrs["Name"][1:]] = _container.attrs["Id"]
        
    return render_template('index.html', docker_list=docker_list)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9000)

