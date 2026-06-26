%global dkms_name dpdk-kmods
%global debian_release 1
%global _disable_source_fetch 0

Name:           dpdk-kmods-dkms
Version:        0~20241120+git
Release:        1%{?dist}
Summary:        DKMS package for the DPDK igb_uio kernel module

License:        GPL-2.0-only
URL:            https://packages.debian.org/source/sid/dpdk-kmods
Source0:        https://deb.debian.org/debian/pool/main/d/%{dkms_name}/%{dkms_name}_%{version}.orig.tar.xz
Source1:        https://deb.debian.org/debian/pool/main/d/%{dkms_name}/%{dkms_name}_%{version}-%{debian_release}.debian.tar.xz

BuildArch:      noarch
Requires:       dkms
Requires:       elfutils-libelf-devel
Requires:       make
Requires(post): dkms
Requires(preun): dkms
Recommends:     kernel-devel

%description
This package installs Debian's dpdk-kmods igb_uio source under
%{_usrsrc}/%{dkms_name}-%{version} and registers it with DKMS so the module is
built for installed kernels.

%prep
%setup -q -n %{dkms_name}-%{version} -a 1

%build

%install
dkms_src=%{buildroot}%{_usrsrc}/%{dkms_name}-%{version}
install -d "$dkms_src"
cp -a linux/igb_uio/* "$dkms_src"/

cat > "$dkms_src/dkms.conf" <<'EOF'
PACKAGE_NAME="%{dkms_name}"
PACKAGE_VERSION="%{version}"

# dma_set_mask_and_coherent() was introduced in Linux v3.13.
BUILD_EXCLUSIVE_KERNEL_MIN="3.13"

BUILT_MODULE_NAME[0]="igb_uio"
MAKE="make -C ${kernel_source_dir} M=${dkms_tree}/${PACKAGE_NAME}/${PACKAGE_VERSION}/build MODULE_CFLAGS='-fno-PIE' modules"
CLEAN="make -C ${kernel_source_dir} M=${dkms_tree}/${PACKAGE_NAME}/${PACKAGE_VERSION}/build clean"
DEST_MODULE_LOCATION[0]="/updates/dkms"
AUTOINSTALL="yes"
EOF

%post
/usr/sbin/dkms add -m %{dkms_name} -v %{version} --rpm_safe_upgrade || :
/usr/sbin/dkms install -m %{dkms_name} -v %{version} --force || :

%preun
/usr/sbin/dkms remove -m %{dkms_name} -v %{version} --all --rpm_safe_upgrade || :

%files
%license debian/copyright
%doc README
%doc linux/README.rst
%dir %{_usrsrc}/%{dkms_name}-%{version}
%{_usrsrc}/%{dkms_name}-%{version}/dkms.conf
%{_usrsrc}/%{dkms_name}-%{version}/Kbuild
%{_usrsrc}/%{dkms_name}-%{version}/Makefile
%{_usrsrc}/%{dkms_name}-%{version}/compat.h
%{_usrsrc}/%{dkms_name}-%{version}/igb_uio.c

%changelog
* Fri Jun 26 2026 FlyGoat <flygoat@users.noreply.github.com> - 0~20241120+git-1
- Initial DKMS package for Debian dpdk-kmods igb_uio.
