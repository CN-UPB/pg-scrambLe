ENV['RACK_ENV'] ||= 'production'

require 'sinatra/base'
require 'sinatra/json'
require 'sinatra/reloader'
require 'sinatra/activerecord'
require 'sinatra/logger'

# Require the bundler gem and then call Bundler.require to load in all gems listed in Gemfile.
require 'bundler'
Bundler.require :default, ENV['RACK_ENV'].to_sym

['helpers', 'routes', 'models'].each do |dir|
  Dir[File.join(File.dirname(__FILE__), dir, '**', '*.rb')].each do |file|
    require file
  end
end


class GtkMano < Sinatra::Base
  register Sinatra::Reloader
  register Sinatra::ActiveRecordExtension
  register Sinatra::Logger
  set :logger_level, :debug # or :fatal, :error, :warn, :info
  
  helpers GtkManoHelper
  
  set :root, File.dirname(__FILE__)
  set :public_folder, File.join(File.dirname(__FILE__), 'public')
  set :bind, '0.0.0.0'
  set :time_at_startup, Time.now.utc
  set :environments, %w(development test integration qualification demonstration)
  set :environment, ENV['RACK_ENV'] || :development    
  use Rack::Session::Cookie, :key => 'rack.session', :domain => 'foo.com', :path => '/', :expire_after => 2592000, :secret => '$0nata'

  MODULE='GtkMano'
	enable :logging

  FileUtils.mkdir(File.join(settings.root, 'log')) unless File.exists? File.join(settings.root, 'log')
  logfile = File.open(File.join('log', ENV['RACK_ENV'])+'.log', 'a+')
  logfile.sync = true
  # noinspection RubyArgCount
  set :logger, Logger.new(logfile)
  raise 'Can not proceed without a logger file' if settings.logger.nil?
  set :logger_level, (settings.logger_level ||= 'debug').to_sym # can be debug, fatal, error, warn, or info
  logger.info(MODULE) {"Started at #{settings.time_at_startup}"}
  logger.info(MODULE) {"Logger level at :#{settings.logger_level}"}
    
  enable :cross_origin

    logger.info "GtkMano started at #{settings.time_at_startup}"
end
