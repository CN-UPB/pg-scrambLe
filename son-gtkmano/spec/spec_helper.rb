require 'rack/test'
require 'rspec'
require 'webmock/rspec'

ENV['RACK_ENV'] ||= 'test'

$: << File.expand_path('../..', __FILE__)
require 'gtk_mano'

RSpec.configure do |config|
  config.include Rack::Test::Methods
  config.mock_with :rspec
  config.include WebMock::API
end

# WebMock.disable_net_connect!(allow_localhost: true)
WebMock.allow_net_connect!
