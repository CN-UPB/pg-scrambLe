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

FROM python:3.5-slim
MAINTAINER SONATA

# define plugin name once
ENV PLUGIN_BASE son-mano-service-lifecycle-management
# Configuration
ENV broker_host amqp://guest:guest@son-broker:5672/%2F
ENV broker_exchange son-kernel

ENV url_gk_api http://son-gtkapi:5000/api/v2/
ENV url_nsr_repository http://son-catalogue-repos:4011/records/nsr/
ENV url_vnfr_repository http://son-catalogue-repos:4011/records/vnfr/
ENV url_monitoring_server http://son-monitor-manager:8000/api/v1/

#ARG HOST_PISHAHANG
#ARG HOST_OSM
ARG HOST
# Environment variables
ENV splitter_url=http://$HOST:8003/Main_splitter/split
ENV translator_url=http://$HOST:8003/translator/hello
#ENV username_osm=admin
#ENV password_osm=admin
#ENV host_osm=$HOST_OSM
#ENV username_pish2=sonata
#ENV password_pish2=1234
#ENV host_pishahang=$HOST_PISHAHANG
ENV gtkmanourl=http://$HOST:7001/scrambled_ns

RUN apt-get update && apt-get install -y gcc

# add generic project files
ADD son-mano-base /son-mano-base
ADD utils/delayedstart.sh /delayedstart.sh

# install son-mano-base to be able to use the plugin base class etc.
WORKDIR /son-mano-base
RUN python setup.py install

# add plugin related files
WORKDIR /
ADD plugins/${PLUGIN_BASE} /plugins/${PLUGIN_BASE}
RUN chmod +x /plugins/${PLUGIN_BASE}/son_mano_slm/generate_descriptor_pkg.sh

# install actual plugin
WORKDIR /plugins/${PLUGIN_BASE}
RUN python setup.py develop

COPY /plugins/${PLUGIN_BASE}/requirements.txt ./
RUN pip install --no-cache-dir -r /plugins/${PLUGIN_BASE}/requirements.txt

CMD ["son-mano-service-lifecycle-management"]


