module GtkManoHelper
  def correct(val, default_val)
    return defalt_val unless val
    return 0 if val < 0
    val
  end

  def json_error(code, message)
    msg = {'error' => message}
    logger.error msg.to_s
    halt code, {'Content-type'=>'application/json'}, msg.to_json
  end

  def valid?(uuid)
    uuid.match /[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89aAbB][a-f0-9]{3}-[a-f0-9]{12}/
    uuid == $&
  end

  def keyed_hash(hash)
    Hash[hash.map{|(k,v)| [k.to_sym,v]}]
  end
end

