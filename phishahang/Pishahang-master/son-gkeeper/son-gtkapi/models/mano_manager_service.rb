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
require './models/manager_service.rb'

class ManoManagerService < ManagerService

  JSON_HEADERS = { 'Accept'=> 'application/json', 'Content-Type'=>'application/json'}
  CLASS_NAME = self.name
  LOG_MESSAGE = 'GtkApi::' + CLASS_NAME

  def self.config(url:, logger:)
    method = LOG_MESSAGE + "##{__method__}(url=#{url})"
    raise ArgumentError, CLASS_NAME+' can not be configured with nil or empty url' if url.to_s.empty?
    @@url = url
    @@logger = logger
    @@logger.debug(method) {'entered'}
  end

  #General Case Add MANO compute and network

  def self.create_mano_rs(params)
    method = LOG_MESSAGE + "##{__method__}(#{params})"
    @@logger.debug(method) {"entered"}

    saved_params = params.dup

    # Object compute-resources created from params
    #{"mano_type":String,"configuration":{"tenant_ext_router\":String, "tenant_ext_net":String, "tenant":String},
    # "city":String,"country":String, "mano_address":String,"username":String,"pass":String,"domain":String}

    cparams = {}
    cparams[:mano_type] = params[:mano_type].capitalize
    cparams[:configuration] = {}
    cparams[:country] = params[:country]
    cparams[:city] = params[:city]
    cparams[:name] = params[:name]
    cparams[:mano_address] = params[:compute_configuration][:mano_address]
    cparams[:username] = params[:compute_configuration][:username]
    cparams[:pass] = params[:compute_configuration][:pass]
    end

    begin
      @@logger.debug(method) {"@url = " + @@url}
      # Creating compute resource
      response = postCurb(url:@@url+'/mano/compute-resources', body: cparams)
      @@logger.debug(method) {"response="+response.to_s}
      #Wait a bit for the process call
      sleep 3

      #Wait a bit for the process call
      request_uuid = response[:items][:request_uuid]
      @@logger.debug(method) {"request_uuid="+request_uuid.to_s}
      @@logger.debug(method) {"@url = " + @@url}
      sleep 2

      # Finding compute resource uuid
      response2 = getCurb(url:@@url+'/mano_requests/compute-resources/'+request_uuid, headers: JSON_HEADERS)
      @@logger.debug(method) {"response2="+response2.to_s}
      compute_uuid = response2[:items][:query_response][:uuid]
      @@logger.debug(method) {"compute_uuid="+compute_uuid.to_s}
    end
  end

  # MANO COMPUTE-RESOURCES

  def self.find_manos_comp_rs(params)
    method = LOG_MESSAGE + "##{__method__}(#{params})"
    @@logger.debug(method) {'entered'}
    begin
      response = getCurb(url:@@url+'/mano/compute-resources', headers:JSON_HEADERS)
      @@logger.debug(method) {'response='+response.to_s}
      response
    rescue => e
      @@logger.error(method) {"Error during processing: #{$!}"}
      @@logger.error(method) {"Backtrace:\n\t#{e.backtrace.join("\n\t")}"}
      nil
    end
  end

  def self.create_mano_comp_rs(params)
    method = LOG_MESSAGE + "##{__method__}(#{params})"
    @@logger.debug(method) {"entered"}

    begin
      @@logger.debug(method) {"@url = " + @@url}
      response = postCurb(url:@@url+'/mano/compute-resources', body: params)
      @@logger.debug(method) {"response="+response.to_s}
      response
    rescue => e
      @@logger.error(method) {"Error during processing: #{$!}"}
      @@logger.error(method) {"Backtrace:\n\t#{e.backtrace.join("\n\t")}"}
      nil
    end
  end

  def self.find_mano_comp_rs_request_by_uuid(uuid)
    method = LOG_MESSAGE + "##{__method__}(#{uuid})"
    @@logger.debug(method) {'entered'}
    begin
      response = getCurb(url:@@url+'/mano_requests/compute-resources/'+uuid, headers: JSON_HEADERS)
      @@logger.debug(method) {"Got response: #{response}"}
      query_response = response[:items][:query_response]
      if query_response
        query_response
      else
        []
      end
    rescue => e
      @@logger.error(method) {"Error during processing: #{$!}"}
      @@logger.error(method) {"Backtrace:\n\t#{e.backtrace.join("\n\t")}"}
      nil
    end
  end

  # MANO NETWORKING-RESOURCES
  def self.find_manos_net_rs(params)
    method = LOG_MESSAGE + "##{__method__}(#{params})"
    @@logger.debug(method) {'entered'}
    begin
      response = getCurb(url:@@url+'/mano/networking-resources', headers:JSON_HEADERS)
      @@logger.debug(method) {'response='+response.to_s}
      response
    rescue => e
      @@logger.error(method) {"Error during processing: #{$!}"}
      @@logger.error(method) {"Backtrace:\n\t#{e.backtrace.join("\n\t")}"}
      nil
    end
  end

  def self.create_mano_net_resources(params)
    method = LOG_MESSAGE + "##{__method__}(#{params})"
    @@logger.debug(method) {"entered"}

    begin
      @@logger.debug(method) {"@url = " + @@url}
      response = postCurb(url:@@url+'/mano/networking-resources', body: params)
      @@logger.debug(method) {"response="+response.to_s}
      response
    rescue => e
      @@logger.error(method) {"Error during processing: #{$!}"}
      @@logger.error(method) {"Backtrace:\n\t#{e.backtrace.join("\n\t")}"}
      nil
    end
  end

  def self.find_mano_net_rs_request_by_uuid(uuid)
    method = LOG_MESSAGE + "##{__method__}(#{uuid})"
    @@logger.debug(method) {'entered'}
    begin
      response = getCurb(url:@@url+'/mano_requests/networking-resources/'+uuid, headers: JSON_HEADERS)
      @@logger.debug(method) {"Got response: #{response}"}
      query_response = response[:items][:query_response]
      if query_response
        query_response
      else
        []
      end
    rescue => e
      @@logger.error(method) {"Error during processing: #{$!}"}
      @@logger.error(method) {"Backtrace:\n\t#{e.backtrace.join("\n\t")}"}
      nil
    end
  end
  
  def self.began_at
    log_message=LOG_MESSAGE+"##{__method__}"
    @@logger.debug(log_message) {'entered'}    
    response = getCurb(url: @@url + '/began_at')
    @@logger.debug(log_message) {"response=#{response}"}
    response
  end
end
