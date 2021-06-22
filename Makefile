build:
	@docker build -t spending-analysis .

start:
	@docker run -d -p 8501:8501 \
		--name spending-analysis \
		--volume $(PWD)/data:/src/data \
		--volume $(PWD)/app/:/src/app \
		spending-analysis
	@echo http://localhost:8501
	@sleep 1
	@open http://localhost:8501

stop:
	@docker stop spending-analysis
	@docker rm spending-analysis

backup:
	@cat ./data/categorized/*.csv > ./data/backups/categorized_transactions_backup_`date +%Y%m%d`.csv
