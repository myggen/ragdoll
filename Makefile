dockerimg:
	docker build --no-cache -t="registry.met.no/modellprod/ollama-container:latest" .

dockershell-gpu:
	docker run  --runtime=nvidia --gpus all -v /lustre:/lustre -v $(HOME):$(HOME)  -p 11434:11434 -i -t registry.met.no/modellprod/ollama-container:latest /bin/bash

dockershell-nogpu:
	docker run -v /lustre:/lustre -v $(HOME):$(HOME) -v /home/ollama:/home/ollama -i -t registry.met.no/modellprod/ollama-container:latest /bin/bash

runserver-nogpu: 
	docker run -v /lustre:/lustre -v $(HOME):$(HOME) -v /home/ollama:/home/ollama  -p 11434:11434 -p 8000:8000 -i -t registry.met.no/modellprod/ollama-container:latest runserver.sh

runmodel: 
	docker run --net=host -v /lustre:/lustre -v $(HOME):$(HOME)  -v /home/ollama:/home/ollama  -i -t registry.met.no/modellprod/ollama-container:latest ollama run llama3.1:latest

pullmodel: 
	docker run --net=host -v /lustre:/lustre -v $(HOME):$(HOME)  -v /home/ollama:/home/ollama  -i -t registry.met.no/modellprod/ollama-container:latest ollama pull llama3.1:latest

sif: dockerimg
	sudo singularity build ollama-container-latest.sif docker-daemon://registry.met.no/modellprod/ollama-container:latest		

sifshell:
	singularity exec --bind /lustre:/lustre/,$(HOME):$(HOME) ollama-container-latest.sif /bin/bash


