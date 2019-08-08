environment = ENV['RACK_ENV'] || 'production'
stdout_and_stderr_file_name=::File.join('.', 'log', environment+'.log')
stdout_redirect stdout_and_stderr_file_name, stdout_and_stderr_file_name, true

