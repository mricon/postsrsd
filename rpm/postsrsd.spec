%global selinux_variants mls targeted
%define _shortrel 29f7526
%define _longrel  29f7526ce8164cca3fae4181fffccc5a39a1f2d8
%define _snapdate 20170501

Name:          postsrsd
Version:       1.5
Release:       0.%{_snapdate}git%{_shortrel}%{?dist}
Summary:       A sender-envelope rewriter to comply with SPF forwarding for postfix 

License:       GPLv2+
URL:           https://github.com/roehling/postsrsd
Source0:       https://github.com/roehling/%{name}/archive/%{_longrel}.tar.gz

BuildRequires: cmake
BuildRequires: help2man
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
BuildRequires: systemd
Requires:      coreutils postfix
# SELinux-related requires
BuildRequires: checkpolicy, selinux-policy-devel
Requires(post): policycoreutils
Requires(postun): policycoreutils

%description
PostSRSd provides the Sender Rewriting Scheme (SRS) via TCP-based
lookup tables for Postfix. SRS is needed if your mail server acts
as forwarder.


%prep
%setup -q -n %{name}-%{_longrel}

%check
ctest -V %{?_smp_mflags}

%build
mkdir -p build
cd build
%cmake -DINIT_FLAVOR=systemd -DCONFIG_DIR=%{_sysconfdir}/sysconfig -DSYSD_UNIT_DIR=%{_unitdir} \
-DGENERATE_SRS_SECRET=OFF -DCHROOT_DIR=%{_sharedstatedir}/%{name} ..
make %{?_smp_mflags}
cd -
cd selinux
    make -f /usr/share/selinux/devel/Makefile
cd -


%install
%make_install
install -d %{buildroot}%{_sharedstatedir}/%{name}
install -D selinux/%{name}.pp %{buildroot}%{_datadir}/selinux/packages/%{name}.pp

%pre
if [ ! -f "%{_sysconfdir}/postsrsd.secret" ]; then
    umask 077
    dd if=/dev/urandom bs=18 count=1 status=noxfer 2> /dev/null | base64 > %{_sysconfdir}/postsrsd.secret
fi

%preun
%systemd_preun postsrsd.service

%post
semodule -u %{_datadir}/selinux/packages/%{name}.pp
fixfiles -R %{name} restore || :
%systemd_post postsrsd.service

%postun
%systemd_postun_with_restart postsrsd.service
if [ "$1" -lt "1" ]; then #Final uninstall
    semodule -r %{_datadir}/selinux/packages/%{name}.pp
    fixfiles -R %{name} restore || :
fi

%files
%config(noreplace) %{_sysconfdir}/sysconfig/postsrsd
%{_unitdir}/postsrsd.service
%{_sbindir}/postsrsd
%{_datadir}/selinux/packages/%{name}.pp
%doc %{_defaultdocdir}/postsrsd
%doc %{_mandir}/man8/postsrsd.8.gz
%attr(700, nobody, nobody) %dir %{_sharedstatedir}/%{name}

%changelog
* Mon May 01 2017 Konstantin Ryabitsev <konstantin@linuxfoundation.org>
- Update to latest upstream with SELinux fixes.
- Use version 1.5-0.{gitinfo} until 1.5 release by upstream.

* Mon Mar 07 2016 Anatole Denis <natolumin@rezel.net>
- Add selinux policy compilation. Do not use the one in the CMakefile, it breaks sandbox

* Mon Feb 22 2016 Anatole Denis <natolumin@rezel.net>
- Stop using systemd_requires macro (not recommended by guidelines)

* Tue Feb 16 2016 Anatole Denis <natolumin@rezel.net>
- Version 1.4
- Change the source URL to use github releases instead of tags

* Mon Dec 14 2015 Anatole Denis <natolumin@rezel.net>
- Version Bump
