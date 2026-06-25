%global dkms_name iavf
%global upstream_repo intel/ethernet-linux-iavf
%global _disable_source_fetch 0

Name:           iavf-dkms
Version:        4.13.35
Release:        1%{?dist}
Summary:        DKMS package for the Intel Ethernet Adaptive Virtual Function driver

License:        GPL-2.0-only
URL:            https://github.com/%{upstream_repo}
Source0:        https://github.com/%{upstream_repo}/releases/download/v%{version}/%{dkms_name}-%{version}.tar.gz

BuildArch:      noarch
Requires:       dkms
Requires(post): dkms
Requires(preun): dkms
Recommends:     kernel-devel

%description
This package installs Intel's out-of-tree iavf driver sources under
%{_usrsrc}/%{dkms_name}-%{version} and registers them with DKMS so modules are
built for installed kernels.

%prep
%autosetup -n %{dkms_name}-%{version}

%build

%install
dkms_src=%{buildroot}%{_usrsrc}/%{dkms_name}-%{version}
install -d "$dkms_src"
cp -a COPYING README src scripts kcompat-gen pci.updates %{dkms_name}.7 "$dkms_src"/
cp -a SUMS "$dkms_src"/

cat > "$dkms_src/dkms.conf" <<'EOF'
PACKAGE_NAME="%{dkms_name}"
PACKAGE_VERSION="%{version}"
AUTOINSTALL="yes"

BUILT_MODULE_NAME[0]="%{dkms_name}"
BUILT_MODULE_LOCATION[0]="src/"
DEST_MODULE_LOCATION[0]="/updates/dkms"

MAKE[0]="make -C ${kernel_source_dir} M=${dkms_tree}/${PACKAGE_NAME}/${PACKAGE_VERSION}/build/src modules"
CLEAN="make -C ${kernel_source_dir} M=${dkms_tree}/${PACKAGE_NAME}/${PACKAGE_VERSION}/build/src clean"
EOF

%post
/usr/sbin/dkms add -m %{dkms_name} -v %{version} --rpm_safe_upgrade || :
/usr/sbin/dkms install -m %{dkms_name} -v %{version} --force || :

%preun
/usr/sbin/dkms remove -m %{dkms_name} -v %{version} --all --rpm_safe_upgrade || :

%files
%dir %{_usrsrc}/%{dkms_name}-%{version}
%license %{_usrsrc}/%{dkms_name}-%{version}/COPYING
%doc %{_usrsrc}/%{dkms_name}-%{version}/README
%doc %{_usrsrc}/%{dkms_name}-%{version}/pci.updates
%{_usrsrc}/%{dkms_name}-%{version}/dkms.conf
%{_usrsrc}/%{dkms_name}-%{version}/src
%{_usrsrc}/%{dkms_name}-%{version}/scripts
%{_usrsrc}/%{dkms_name}-%{version}/kcompat-gen
%{_usrsrc}/%{dkms_name}-%{version}/SUMS
%{_usrsrc}/%{dkms_name}-%{version}/%{dkms_name}.7

%changelog
* Thu Jun 25 2026 FlyGoat <flygoat@users.noreply.github.com> - 4.13.35-1
- Initial DKMS package for Intel iavf.
