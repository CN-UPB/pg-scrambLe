## SONATA - Gatekeeper
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
require 'json'

class CService
  
  JSON_HEADERS = { 'Accept'=> 'application/json', 'Content-Type'=>'application/json'}
  
  def initialize(repository, logger)
    raise ArgumentError.new('CService.initialize: repository can not be nil') if repository.nil?
    raise ArgumentError.new('CService.initialize: logger can not be nil') if logger.nil?
    @repository = repository
    @logger = logger
    @logger.debug "CService.new(repository=#{repository.inspect}, logger#{logger.inspect})"
  end
  
  def find(params)
    @logger.debug "CService.find(#{params})"
    services = @repository.find(params)
    @logger.debug "CService.find: #{services}"
    services
  end

  def find_by_uuid(uuid)
    @logger.debug "CService.find_by_uuid(#{uuid})"
    service = @repository.find_by_uuid(uuid)
    @logger.debug "CService.find_by_uuid: #{service}"
    service
  end
end
