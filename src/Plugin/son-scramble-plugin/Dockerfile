# Copyright (c) 2015 SONATA-NFV
# ALL RIGHTS RESERVED.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#    http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# Neither the name of the SONATA-NFV [, ANY ADDITIONAL AFFILIATION]
# nor the names of its contributors may be used to endorse or promote
# products derived from this software without specific prior written
# permission.
# This work has been performed in the framework of the SONATA project,
# funded by the European Commission under Grant number 671517 through
# the Horizon 2020 and 5G-PPP programmes. The authors would like to
# acknowledge the contributions of their colleagues of the SONATA
# partner consortium (www.sonata-nfv.eu).

FROM python:3.4-slim
MAINTAINER SONATA

# define plugin name once
ENV PLUGIN_BASE son-scramble-plugin
# Configuration
ENV broker_host amqp://guest:guest@son-broker:5672/%2F
ENV broker_exchange son-kernel

# Environment variables
ENV splitter_url=http://131.234.250.202:8000/Main_splitter/hello
ENV translator_url=http://131.234.250.202:8000/translator/hello
ENV username_osm=admin
ENV password_osm=admin
ENV host_5=vm-hadik3r-05.cs.uni-paderborn.de
ENV username_pish2=sonata
ENV password_pish2=1234
ENV host_10=vm-hadik3r-10.cs.uni-paderborn.de
ENV host_6=vm-hadik3r-06.cs.uni-paderborn.de
ENV host_8=vm-hadik3r-08.cs.uni-paderborn.de

# add generic project files
ADD son-mano-base /son-mano-base

# add plugin related files
ADD plugins/${PLUGIN_BASE} /plugins/${PLUGIN_BASE}
RUN chmod +x /plugins/${PLUGIN_BASE}/son_scramble_plugin/generate_descriptor_pkg.sh

# install son-mano-base to be able to use the plugin base class etc.
WORKDIR /son-mano-base
RUN python setup.py install

# install actual plugin
WORKDIR /plugins/${PLUGIN_BASE}
RUN python setup.py develop

# Install python requirements
COPY /plugins/${PLUGIN_BASE}/requirements.txt ./

COPY /plugins/${PLUGIN_BASE}/son_scramble_plugin/osm_helpers.py ./son_scramble_plugin/osm_helpers.py
RUN pip install --no-cache-dir -r /plugins/${PLUGIN_BASE}/requirements.txt

CMD ["son-scramble-plugin"]


