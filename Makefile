.PHONY: validate render lab-up lab-down dry-run test cluster-up cluster-down

validate:
	PYTHONPATH=src python -m optilab.cli validate designs/demo-ring.yaml

render:
	PYTHONPATH=src python -m optilab.cli render designs/demo-ring.yaml -o lab/demo-ring.clab.yml

test:
	PYTHONPATH=src pytest -q
	robot --outputdir reports robot/dry_run.robot

lab-up: render
	sudo containerlab deploy -t lab/demo-ring.clab.yml

lab-down:
	sudo containerlab destroy -t lab/demo-ring.clab.yml --cleanup

cluster-up:
	kind create cluster --name optilab || true

cluster-down:
	kind delete cluster --name optilab

dry-run: test
	@echo "Dry-run complete. See reports/"
