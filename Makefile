build:
	@docker-compose pull
	@docker-compose build


start:
	@docker-compose up --detach spending-tracker
	@echo http://localhost:8501
	@open http://localhost:8501


jupyter-start:
	@docker-compose up --detach jupyter
	@sleep 5
	@docker exec -it jupyter jupyter server list
	@echo

stop:
	@docker-compose down --remove-orphans

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
