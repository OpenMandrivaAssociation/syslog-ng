%define name    syslog-ng
%define version 3.1
%define pre     beta1
%define release %mkrel 0.%{pre}.2

Name:		%{name}
Version:	%{version}
Release:	%{release}
Summary:	Syslog-ng daemon
Group:		System/Kernel and hardware
License:	GPL
Url:		http://www.balabit.com/products/syslog_ng/
Source0: 	http://www.balabit.com/downloads/files/syslog-ng/sources/%{version}/source/%{name}_%{version}%{pre}.tar.gz
Source1:	syslog-ng.sysconfig
Source2:	syslog-ng.init
Source3:	syslog-ng.conf
Source4:	syslog-ng.logrotate
Source5:	http://people.balabit.hu/frobert/syslog-ng-v3.1admin-guide-en-1ed-draft.pdf
Patch:      syslog-ng-3.0.4-fix-pattern-database-location.patch
BuildRequires:	flex
BuildRequires:	libol-devel >= 0.2.23
BuildRequires:	net-devel >= 1.1.3
BuildRequires:	eventlog-devel
BuildRequires:	glib2-devel
BuildRequires:	libwrap-devel
BuildRequires:	openssl-devel
BuildRequires:	dbi-devel
Provides:       syslog-daemon
Requires(post):	rpm-helper
Requires(preun):rpm-helper
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
Syslog-ng, as the name shows, is a syslogd replacement, but with new
functionality for the new generation. The original syslogd allows
messages only to be sorted based on priority/facility pairs; syslog-ng
adds the possibility to filter based on message contents using regular
expressions. The new configuration scheme is intuitive and powerful.
Forwarding logs over TCP and remembering all forwarding hops makes it
ideal for firewalled environments.

%prep
%setup -q -n %{name}-%{version}%{pre}
%patch -p 1
cp %{SOURCE5} syslog-ng-v3.0-guide-admin-en.pdf
autoreconf -fi

%build
%configure2_5x \
    --bindir=/bin \
    --sbindir=/sbin \
    --enable-dynamic-linking \
    --with-pidfile-dir=%{_localstatedir}/run
%make

%install
rm -rf %{buildroot}
%makeinstall_std

# init script
install -d -m 755 %{buildroot}%{_initrddir}
install -m 755 %{SOURCE2} %{buildroot}%{_initrddir}/syslog-ng
install -d -m 755 %{buildroot}%{_sysconfdir}/sysconfig
install -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/sysconfig/syslog-ng
install -m 644 %{SOURCE3} %{buildroot}%{_sysconfdir}/syslog-ng.conf

install -d -m 755 %{buildroot}%{_sysconfdir}/syslog-ng.d

%post
%_post_service %{name}

%preun
%_preun_service %{name}

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc README AUTHORS COPYING ChangeLog NEWS VERSION
%doc doc/examples doc/security doc/xsd syslog-ng-v3.0-guide-admin-en.pdf
%config(noreplace) %{_sysconfdir}/syslog-ng.conf
%config(noreplace) %{_sysconfdir}/sysconfig/syslog-ng
%{_sysconfdir}/syslog-ng.d
%{_initrddir}/syslog-ng
/sbin/syslog-ng
/bin/loggen
/bin/pdbtool
%{_mandir}/man1/pdbtool.1*
%{_mandir}/man5/syslog-ng.conf.5*
%{_mandir}/man8/syslog-ng.8*
