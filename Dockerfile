FROM centos:7

RUN yum -y install git
RUN yum -y install epel-release
RUN yum -y install ansible

RUN git clone https://github.com/redhat-performance/jetpack.git

ENTRYPOINT ansible-playbook jetpack/main.yml
