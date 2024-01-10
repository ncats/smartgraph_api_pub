# Author:	Gergely Zahoranszky-Kohalmi, PhD
#
# Email:	gergely.zahoranszky-kohalmi@nih.gov
#
# Organization:	National Center for Advancing Translational Sciences (NCATS/NIH)
#
# References
#

FROM mambaorg/micromamba:1.5.3

USER root

RUN apt-get update \
 && apt-get install -yq --no-install-recommends \
    p7zip-full \
    awscli \
    vim \
    telnet \
    iputils-ping \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

RUN mkdir /usr/src/smartgraph-api

COPY code/environment.yml /usr/src/smartgraph-api/code/environment.yml

WORKDIR /usr/src/smartgraph-api

RUN micromamba env create -f code/environment.yml

COPY code /usr/src/smartgraph-api/code

# This is to override the default shell in order to use bash
SHELL ["micromamba", "run", "-n", "smartgraph", "/bin/bash", "-c"]

EXPOSE 5058

WORKDIR /usr/src/smartgraph-api/code

ENTRYPOINT ["micromamba", "run", "-n", "smartgraph", "python", "server.py"]
