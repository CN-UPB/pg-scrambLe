require 'json'
require 'pp'
require 'addressable/uri'
require 'yaml'
require 'bunny'

class GtkMano < Sinatra::Base
  get '/mano/:uuid/?' do begin
    request = ManoRequest.find(params[:uuid])
  rescue Exception => e
    logger.debug(e.message)
    logger.debug(e.backtrace.inspect)
    halt 404, 'Request #{params[:uuid]} not found'
  end
  end

  # Gets the list o vim compute resources
  get '/mano/?' do 
  begin
    request = ManoRequest.all
    json_request = json(response, {root: false})
    halt 201, json_request
  rescue Exception => e
    logger.debug(e.message)
    logger.debug(e.backtrace.inspect)
    halt 500, 'Internal server error'
  end
  end

  post '/mano/?' do original_body = request.body.read
  params = JSON.parse(original_body)
  begin
    request = ManoRequest.create(params)
    json_request = json(response, {root: false})
    halt 201, json_request

  rescue Exception => e
    logger.debug(e.message)
    logger.debug(e.backtrace.inspect)
    halt 500, 'Internal server error'
  end
  end
end
