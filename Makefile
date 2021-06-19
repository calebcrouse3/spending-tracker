build:
	@docker build -t spending-analysis ./app

start:
	@docker run \
		--detach \
		--name spending-analysis \
		--publish 8501:80 \
		spending-analysis
	@echo http://localhost:8501

stop:
	@docker stop spending-analysis
	@docker rm spending-analysis
