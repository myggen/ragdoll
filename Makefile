HOST_VOL_OLLAMA=$(HOME)/.ollama-vol
HOST_VOL_WEBUI=$(HOME)/.open-webui-vol



dockerimg:
	docker build --no-cache -t="registry.met.no/modellprod/ollama-container:latest" .

dockershell-gpu:
	docker run  --runtime=nvidia --gpus all -v $(HOME):$(HOME)  -v /home/ollama:/root/.ollama -i -t registry.met.no/modellprod/ollama-container:latest /bin/bash

dockershell-nogpu:
	docker run -v $(HOME):$(HOME) -v /home/ollama:/root/.ollama -i -t registry.met.no/modellprod/ollama-container:latest /bin/bash

runserver-nogpu: 
	docker run -v $(HOME):$(HOME) -v /home/ollama:/root/.ollama  -p 11434:11434 -p 8000:8000 -i -t registry.met.no/modellprod/ollama-container:latest runserver.sh

runserver-gpu: 
	docker run --runtime=nvidia --gpus all -v $(HOST_VOL_OLLAMA):/root/.ollama  -p 11434:11434 -p 8000:8000 -i -t registry.met.no/modellprod/ollama-container:latest runserver.sh

runmodel: 
	docker run --net=host  -v $(HOME):$(HOME)  -v $(HOST_VOL_OLLAMA):/root/.ollama  -i -t registry.met.no/modellprod/ollama-container:latest ollama run llama3.1:latest

pullmodels: 
	docker run --net=host -v $(HOME):$(HOME) -v $(HOST_VOL_OLLAMA):/root/.ollama -i -t registry.met.no/modellprod/ollama-container:latest ollama pull llama3.1:latest
	docker run --net=host -v $(HOME):$(HOME) -v $(HOST_VOL_OLLAMA):/root/.ollama -i -t registry.met.no/modellprod/ollama-container:latest ollama pull mxbai-embed-large:latest
	docker run --net=host -v $(HOME):$(HOME) -v $(HOST_VOL_OLLAMA):/root/.ollama -i -t registry.met.no/modellprod/ollama-container:latest ollama pull llama3.1:8b

sif: dockerimg
	sudo singularity build ollama-container-latest.sif docker-daemon://registry.met.no/modellprod/ollama-container:latest		

sifshell:
	singularity exec --bind /lustre:/lustre/,$(HOME):$(HOME) ollama-container-latest.sif /bin/bash

make-runserver-gpu-sif: 
	singularity exec --bind $HOME/.ollama-vol:/root/.ollama ollama-container-latest.sif --nv runserver.sh

open-webui-nogpu: 
	docker run -p 3000:8080 --add-host=host.docker.internal:host-gateway -v $(HOST_VOL_WEBUI):/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main

open-webui-gpu: 
	docker run  --runtime=nvidia --gpus all -p 3000:8080 --add-host=host.docker.internal:host-gateway -v $(HOST_VOL_WEBUI):/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main