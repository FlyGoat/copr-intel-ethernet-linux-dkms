%global dkms_name idpf
%global upstream_repo intel/ethernet-linux-idpf
%global _disable_source_fetch 0

Name:           idpf-dkms
Version:        1.0.11
Release:        1%{?dist}
Summary:        DKMS package for the Intel Infrastructure Data Path Function driver

License:        GPL-2.0-only
URL:            https://github.com/%{upstream_repo}
Source0:        https://github.com/%{upstream_repo}/archive/refs/tags/v%{version}/%{dkms_name}-%{version}.tar.gz

BuildArch:      noarch
Requires:       dkms
Requires(post): dkms
Requires(preun): dkms
Recommends:     kernel-devel

%description
This package installs Intel's out-of-tree idpf driver sources under
%{_usrsrc}/%{dkms_name}-%{version} and registers them with DKMS so modules are
built for installed kernels.

%prep
%autosetup -n ethernet-linux-%{dkms_name}-%{version}

%build

%install
dkms_src=%{buildroot}%{_usrsrc}/%{dkms_name}-%{version}
install -d "$dkms_src"
cp -a COPYING README Makefile idpf auxiliary linux scripts "$dkms_src"/

cat > "$dkms_src/dkms.conf" <<'EOF'
PACKAGE_NAME="%{dkms_name}"
PACKAGE_VERSION="%{version}"
AUTOINSTALL="yes"

BUILT_MODULE_NAME[0]="%{dkms_name}"
BUILT_MODULE_LOCATION[0]="idpf/src/"
DEST_MODULE_LOCATION[0]="/updates/dkms"

MAKE[0]="make -C ${dkms_tree}/${PACKAGE_NAME}/${PACKAGE_VERSION}/build KSRC=${kernel_source_dir} BUILD_KERNEL=${kernelver}"
CLEAN="make -C ${dkms_tree}/${PACKAGE_NAME}/${PACKAGE_VERSION}/build KSRC=${kernel_source_dir} BUILD_KERNEL=${kernelver} clean"
EOF

%post
/usr/sbin/dkms add -m %{dkms_name} -v %{version} --rpm_safe_upgrade || :
/usr/sbin/dkms install -m %{dkms_name} -v %{version} --force || :

%preun
/usr/sbin/dkms remove -m %{dkms_name} -v %{version} --all --rpm_safe_upgrade || :

%files
%dir %{_usrsrc}/%{dkms_name}-%{version}
%license %{_usrsrc}/%{dkms_name}-%{version}/COPYING
%license %{_usrsrc}/%{dkms_name}-%{version}/idpf/COPYING
%license %{_usrsrc}/%{dkms_name}-%{version}/auxiliary/COPYING
%doc %{_usrsrc}/%{dkms_name}-%{version}/README
%doc %{_usrsrc}/%{dkms_name}-%{version}/idpf/pci.updates
%{_usrsrc}/%{dkms_name}-%{version}/dkms.conf
%{_usrsrc}/%{dkms_name}-%{version}/Makefile
%{_usrsrc}/%{dkms_name}-%{version}/idpf/idpf.7
%{_usrsrc}/%{dkms_name}-%{version}/idpf/src
%{_usrsrc}/%{dkms_name}-%{version}/auxiliary/auxiliary.7
%{_usrsrc}/%{dkms_name}-%{version}/auxiliary/src
%{_usrsrc}/%{dkms_name}-%{version}/linux
%{_usrsrc}/%{dkms_name}-%{version}/scripts

%changelog
* Thu Jun 25 2026 FlyGoat <flygoat@users.noreply.github.com> - 1.0.11-1
- Initial DKMS package for Intel idpf.
