build:
	@docker build -t spending-tracker .


start:
	@docker run -d \
	    -p 8501:8501 \
		-v $(PWD)/src:/src \
		-v /Users/caleb.crouse/Downloads:/src/data/downloads \
		--name spending-tracker \
		spending-tracker
	@open http://localhost:8501
	@echo http://localhost:8501

stop:
	@docker stop spending-tracker
	@docker rm spending-tracker

backup:
	@cat ./data/categorized/*.csv > ./data/backups/categorized_transactions_backup_`date +%Y%m%d`.csv

python-linter-build:
	@docker build -t python-linter python-linter/.

python-lint:
	@docker run \
		--name python-linter \
		--rm \
		-it \
		-v $(PWD):/src \
		python-linter
