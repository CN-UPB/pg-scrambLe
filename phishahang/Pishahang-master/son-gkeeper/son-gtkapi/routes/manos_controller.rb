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
require 'sinatra/namespace'
class GtkApi < Sinatra::Base

  register Sinatra::Namespace

  begin
    namespace '/api/v2/manos' do
      before do
        if request.request_method == 'OPTIONS'
          response.headers['Access-Control-Allow-Origin'] = '*'
          response.headers['Access-Control-Allow-Methods'] = 'POST'
          response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With'
          halt 200
        end
      end

      # POST a request
      post '/?' do
        MESSAGE = "GtkApi::POST /api/v2/manos?"
        remaining = check_rate_limit(limit: 'anonymous_operations', client: settings.gatekeeper_api_client_id) if check_rate_limit_usage()
        params = JSON.parse(request.body.read, symbolize_names: true)

        unless params.nil?
          logger.debug(MESSAGE) {"entered with params=#{params}"}

          # DATA MODEL
          # {"compute_configuration":{"vendor":"name","mano_address":"ip_address",
          #                           "username":"username","pass":"password"},
          #  "country":"country",
          #  "city":"city"
          #  "name" : "nombre"}

          json_error(400, 'MANO compute is missing', MESSAGE) unless valid_param?(params: params, sym: :compute_configuration)
          json_error(400, 'MANO country is missing', MESSAGE) unless valid_param?(params: params, sym: :country)
          json_error(400, 'MANO city is missing', MESSAGE) unless valid_param?(params: params, sym: :city)
          json_error(400, 'MANO name is missing', MESSAGE) unless valid_param?(params: params, sym: :name)

          new_request = ManoManagerService.create_mano_rs(params)
          if new_request
            logger.debug(MESSAGE) {"new_request =#{new_request}"}
            halt 201, new_request.to_json
          else
            logger.debug(MESSAGE) { "leaving with 'No mano creation request was created'"}
            json_error 400, 'No mano create_request was created'
          end
        end
        logger.debug(MESSAGE) { "leaving with 'No request id specified'"}
        json_error 400, 'No params specified for the create request'
      end

      # GET many manos
      get '/?' do
        MESSAGE="GtkApi GET /api/v2/manos?"+query_string
        @offset ||= params['offset'] ||= DEFAULT_OFFSET
        @limit ||= params['limit'] ||= DEFAULT_LIMIT

        logger.info(MESSAGE) {"entered"}
        remaining = check_rate_limit(limit: 'anonymous_operations', client: settings.gatekeeper_api_client_id) if check_rate_limit_usage()
        manos = ManoManagerService.find_manos_comp_rs(params)
        logger.debug(MESSAGE) { "manos= #{manos}"}
        if manos
          links = build_pagination_headers(url: request_url, limit: @limit.to_i, offset: @offset.to_i, total: manos.size)
          [200, {'Link' => links}, manos.to_json]
        else
          logger.info(MESSAGE) { "leaving GET with 'No get manos request were created'"}
          json_error 400, 'No get list of manos request was created'
        end
      end

      # GET one specific request
      get '/:uuid/?' do
        remaining = check_rate_limit(limit: 'anonymous_operations', client: settings.gatekeeper_api_client_id) if check_rate_limit_usage()
        unless params[:uuid].nil?
          logger.debug "GtkApi: GET /api/v2/manos/#{params[:uuid]}"
          json_error 400, 'Invalid request UUID' unless valid? params[:uuid]

          request = ManoManagerService.find_mano_comp_rs_request_by_uuid(params['uuid'])
          json_error 404, "The mano_request UUID #{params[:uuid]} does not exist" unless request

          logger.debug "GtkApi: leaving GET /mano_request/#{params[:uuid]}\" with request #{request}"
          halt 200, request.to_json
        end
        logger.debug "GtkApi: leaving GET /mano_request/#{params[:uuid]} with 'No mano_request UUID specified'"
        json_error 400, 'No mano_request UUID specified'
      end
    end
  end

  namespace '/api/v2/admin/manos' do
    get '/logs/?' do
      log_message = 'GtkApi::GET /api/v2/admin/manos/logs'
      logger.debug(log_message) {'entered'}
      remaining = check_rate_limit(limit: 'anonymous_operations', client: settings.gatekeeper_api_client_id) if check_rate_limit_usage()
      url = ManoManagerService.class_variable_get(:@@url)+'/admin/logs'
      log = ManoManagerService.get_log(url: url, log_message:log_message)
      logger.debug(log_message) {'leaving with log='+log}
      headers 'Content-Type' => 'text/plain; charset=utf8', 'Location' => '/'
      halt 200, log
    end
  end

  get '/api/v2/admin/users/logs/?' do
    log_message = 'GtkApi::GET /admin/users/logs'
    logger.debug(log_message) {'entered'}
    remaining = check_rate_limit(limit: 'anonymous_operations', client: settings.gatekeeper_api_client_id) if check_rate_limit_usage()
    headers 'Content-Type' => 'text/plain; charset=utf8', 'Location' => '/'
    log = User.get_log(url:User.class_variable_get(:@@url)+'/admin/logs', log_message:log_message)
    logger.debug(log_message) {"leaving with log=#{log}"}
    halt 200, log
  end
end