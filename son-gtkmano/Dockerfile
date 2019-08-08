FROM ruby:2.4.3-slim-stretch
RUN apt-get update && \
  apt-get install -y --no-install-recommends build-essential libcurl3 libcurl3-gnutls libcurl4-openssl-dev libpq-dev && \
	rm -rf /var/lib/apt/lists/*
RUN mkdir -p /app
WORKDIR /app
COPY Gemfile /app
RUN bundle install
COPY . /app
EXPOSE 8001
WORKDIR /app
ENV POSTGRES_PASSWORD sonatatest
ENV POSTGRES_USER postgres
ENV DATABASE_HOST postgres
ENV DATABASE_PORT 5432
ENV PORT 8001
CMD ["bundle", "exec", "puma", "-C", "config/puma.rb", "-b", "tcp://0.0.0.0:8001"]
