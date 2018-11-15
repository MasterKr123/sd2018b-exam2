FROM centos/python-36-centos7

RUN pip3.6 install connexion
RUN pip3.6 install fabric
COPY ./flask_endpoint /flask_endpoint
WORKDIR /flask_endpoint

RUN ./scripts/deploy.sh
