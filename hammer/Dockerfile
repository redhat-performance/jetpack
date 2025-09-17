FROM centos:8

ARG foreman_url=https://foreman.example.com

# Pint to Vault and clean repos
RUN sed -i 's/^mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-* \
    && sed -i 's|#baseurl=.*|baseurl=http://vault.centos.org/8.5.2111/BaseOS/x86_64/os/|g' /etc/yum.repos.d/CentOS-* \
    && echo -e "[AppStream]\nname=CentOS-8.5.2111 - AppStream\nbaseurl=http://vault.centos.org/8.5.2111/AppStream/x86_64/os/\nenabled=1\ngpgcheck=0" >> /etc/yum.repos.d/CentOS-AppStream.repo \
    && dnf clean all

# Install wget and clean dependencies
RUN dnf -y install wget python3 python3-virtualenv python3-pip git rpm-build \
    && dnf clean all

# Install wget y EPEL
RUN wget https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm \
    && rpm -ivh epel-release-latest-8.noarch.rpm \
    && dnf clean all

RUN python3 -m pip install --upgrade pip \
    && python3 -m pip install "ansible==2.10.7"

RUN dnf install -y --skip-broken https://yum.theforeman.org/releases/2.1/el8/x86_64/foreman-release.rpm \
        https://yum.theforeman.org/releases/2.1/el8/x86_64/rubygem-hammer_cli-2.1.0-1.el8.noarch.rpm \
        http://yum.theforeman.org/releases/2.1/el8/x86_64/rubygem-hammer_cli_foreman-2.1.0-2.el8.noarch.rpm

RUN dnf install -y rubygem-hammer_cli \
        rubygem-hammer_cli_foreman

RUN pip3 install j2cli

RUN  hammer --fetch-ca-cert ${foreman_url}

COPY foreman.yml.j2 /root/
RUN j2 /root/foreman.yml.j2 > /etc/hammer/cli.modules.d/foreman.yml
