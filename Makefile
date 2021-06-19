build:
	@docker build -t spending-analysis ./app

start:
	@docker run -d -p 8501:8501 --name spending-analysis spending-analysis
	@echo http://localhost:8501
	@sleep 1
	@open http://localhost:8501

stop:
	@docker stop spending-analysis
	@docker rm spending-analysis
