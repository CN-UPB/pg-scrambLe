##
## Copyright (c) 2015 SONATA-NFV [, ANY ADDITIONAL AFFILIATION]
## ALL RIGHTS RESERVED.
## 
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
## 
##     http://www.apache.org/licenses/LICENSE-2.0
## 
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
## 
## Neither the name of the SONATA-NFV [, ANY ADDITIONAL AFFILIATION]
## nor the names of its contributors may be used to endorse or promote 
## products derived from this software without specific prior written 
## permission.
## 
## This work has been performed in the framework of the SONATA project,
## funded by the European Commission under Grant number 671517 through 
## the Horizon 2020 and 5G-PPP programmes. The authors would like to 
## acknowledge the contributions of their colleagues of the SONATA 
## partner consortium (www.sonata-nfv.eu).
# encoding: utf-8
class VFunction
  
  def initialize(catalogue, logger)
    @catalogue = catalogue
    @logger = logger
  end
  
  def find_function(name,vendor,version)
    log_message = 'VFunction.'+__method__.to_s
    headers = { 'Accept'=> 'application/json', 'Content-Type'=>'application/json'}
    url = @catalogue.url+"?name=#{name}&vendor=#{vendor}&version=#{version}"
    @logger.debug(log_message) {"url="+url}
    begin
      response = RestClient.get(url, headers)
      body = response.body
      @logger.debug(log_message) {"body=#{body}"}
      function=JSON.parse(body, symbolize_names: true)
      @logger.debug(log_message) {"function=#{function}"}
      function[0]
    rescue => e
      @logger.error(log_message) {"No function found for "+url}
      e.message
    end
  end
end