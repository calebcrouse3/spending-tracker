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

data-setup:
	@source ~/virtual_envs/ds3/bin/activate
	@python3 utils.py

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
