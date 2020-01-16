# PCA Assessment Docker 
A python docker utility for Team leads to produce a JSON file containing all configurations to run a CISA PCA. 

## PCA Assessment Docker
The PCA Assessment commands implemented in the docker container can be aliased into the host environment by using the procedure below.

Alias the container commands to the local environment:
```bash
eval "$(docker run pca-assessment)"
```

To run a GoPhish Control command:
```bash
pca-assessment-builder -h
```

## Building the pca-assessment container
To build the Docker container for pca-assessment:

```bash
docker build -t pca-assessment .
```



