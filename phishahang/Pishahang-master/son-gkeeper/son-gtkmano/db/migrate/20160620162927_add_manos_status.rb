class AddStatus < ActiveRecord::Migration
  def change
    add_column :manos_requests, :status, :string, :default => 'waiting'
  end
end
