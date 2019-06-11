class AddQueryResponse < ActiveRecord::Migration
  def change
    add_column :manos_requests, :query_response, :json 
  end
end
