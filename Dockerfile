FROM centos:7

RUN yum -y install git epel-release ansible

RUN git clone https://github.com/redhat-performance/jetpack.git

ENTRYPOINT ansible-playbook jetpack/main.yml
