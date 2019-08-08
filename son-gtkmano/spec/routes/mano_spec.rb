require_relative '../spec_helper'
require 'json'

RSpec.describe GtkMano do

  describe 'GET /mano/' do
    it 'accepts listing vims'
    it 'publishes get vims request'
    it 'returns uuid of newly created request'
  end

  describe 'POST /mano/' do
    it 'accepts new valid (instantiations) requests'
    it 'publishes the new vim request'
    it 'returns uuid of newly created request'
  end

  describe 'GET /mano/:uuid' do
    it 'accepts getting vim request by uuid'
    it 'returns vim request by uuid'
  end
  
end
