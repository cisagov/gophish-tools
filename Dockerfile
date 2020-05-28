FROM python:3
MAINTAINER Bryce Beuerlein <bryce.beuerlein@cisa.dhs.gov>
ENV PCA_HOME="/home/pca" \
    PCA_CON_SRC="/usr/src/pca-assessment"

RUN groupadd --system pca && useradd --system --gid pca pca

RUN apt-get update && \
apt-get install --no-install-recommends -y \
at &&\
apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN mkdir ${PCA_HOME} && chown pca:pca ${PCA_HOME}
VOLUME ${PCA_HOME}

WORKDIR ${PCA_CON_SRC}

COPY . ${PCA_CON_SRC}
RUN pip install --no-cache-dir .
RUN chmod +x ${PCA_CON_SRC}/var/getenv
RUN ln -snf ${PCA_CON_SRC}/var/getenv /usr/local/bin

USER pca
WORKDIR ${PCA_HOME}
CMD ["getenv"]
