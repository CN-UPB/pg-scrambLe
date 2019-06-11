class AddServiceUuid < ActiveRecord::Migration
  def change
    add_column :manos_requests, :query_uuid, :uuid
  end
end
