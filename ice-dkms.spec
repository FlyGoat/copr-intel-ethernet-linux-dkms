%global dkms_name ice
%global upstream_repo intel/ethernet-linux-ice
%global _disable_source_fetch 0

Name:           ice-dkms
Version:        2.6.6
Release:        2%{?dist}
Summary:        DKMS package for the Intel Ethernet 800 Series ice driver

License:        GPL-2.0-only AND LicenseRef-Intel-Redistributable
URL:            https://github.com/%{upstream_repo}
Source0:        https://github.com/%{upstream_repo}/releases/download/v%{version}/%{dkms_name}-%{version}.tar.gz

BuildArch:      noarch
Requires:       dkms
Requires(post): dkms
Requires(preun): dkms
Recommends:     kernel-devel

%description
This package installs Intel's out-of-tree ice driver sources under
%{_usrsrc}/%{dkms_name}-%{version} and registers them with DKMS so modules are
built for installed kernels.

%prep
%autosetup -n %{dkms_name}-%{version}

%build

%install
dkms_src=%{buildroot}%{_usrsrc}/%{dkms_name}-%{version}
install -d "$dkms_src"
cp -a COPYING README src scripts kcompat-gen pci.updates %{dkms_name}.7 "$dkms_src"/
sed -i '1s|^#!/usr/bin/env python$|#!/usr/bin/env python3|' \
    "$dkms_src/scripts/adqsetup/adqsetup.py"

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

firmware_dir=%{buildroot}/lib/firmware/updates/intel/%{dkms_name}/ddp
install -d "$firmware_dir"
install -m 0644 ddp/%{dkms_name}-*.pkg "$firmware_dir"/
install -m 0644 ddp/LICENSE "$firmware_dir"/
set -- "$firmware_dir"/%{dkms_name}-*.pkg
ddp_package="$(basename "$1")"
ln -s "$ddp_package" "$firmware_dir/%{dkms_name}.pkg"

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
%{_usrsrc}/%{dkms_name}-%{version}/%{dkms_name}.7
%license /lib/firmware/updates/intel/%{dkms_name}/ddp/LICENSE
/lib/firmware/updates/intel/%{dkms_name}/ddp/%{dkms_name}-*.pkg
/lib/firmware/updates/intel/%{dkms_name}/ddp/%{dkms_name}.pkg

%changelog
* Thu Jun 25 2026 FlyGoat <flygoat@users.noreply.github.com> - 2.6.6-2
- Package ice DDP firmware files explicitly.
- Normalize adqsetup Python shebang to python3.

* Thu Jun 25 2026 FlyGoat <flygoat@users.noreply.github.com> - 2.6.6-1
- Initial DKMS package for Intel ice.
