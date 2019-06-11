class CreateManosrequests < ActiveRecord::Migration
  def change
    create_table :manos_requests, id: :uuid  do |t|
      t.timestamps
     end
  end
end
