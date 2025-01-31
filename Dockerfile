FROM fedora:latest

RUN dnf install -y python3 ansible lscpu

WORKDIR /workdir
COPY . .

RUN ansible-galaxy collection build --force inhouse
RUN ansible-galaxy collection install --force cervoevo-inhouse-1.0.0.tar.gz



