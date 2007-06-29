%define name    syslog-ng
%define version 2.0.4
%define release %mkrel 1

Summary:	Syslog-ng daemon
Name:		%{name}
Version:	%{version}
Release:	%{release}
Group:		System/Kernel and hardware
License:	GPL
Url:		http://www.balabit.com/products/syslog_ng/
Source0: 	http://www.balabit.com/downloads/syslog-ng/2.0/src/%{name}-%{version}.tar.gz
Source2:	syslog-ng.init
Source3:	syslog-ng.conf
Source4:	syslog-ng.logrotate
BuildRequires:	flex
BuildRequires:	libol-devel >= 0.2.23
BuildRequires:	net2-devel 
BuildRequires:	eventlog-devel
BuildRequires:	glib2-devel
BuildRequires:	libwrap-devel
BuildRequires:	openssl-devel
Requires(post):	rpm-helper
Requires(preun):rpm-helper
Buildroot:	%{_tmppath}/%{name}-%{version}

%description
Syslog-ng, as the name shows, is a syslogd replacement, but with new 
functionality for the new generation. The original syslogd allows 
messages only to be sorted based on priority/facility pairs; syslog-ng 
adds the possibility to filter based on message contents using regular 
expressions. The new configuration scheme is intuitive and powerful. 
Forwarding logs over TCP and remembering all forwarding hops makes it 
ideal for firewalled environments.

%prep
%setup -q

%build
%configure2_5x --sbindir=/sbin --enable-dynamic-linking
%make

%install
rm -rf %{buildroot}
%makeinstall_std

mkdir -p %{buildroot}%{_initrddir}
install -m 755 %{SOURCE2} %{buildroot}%{_initrddir}/syslog-ng
install -m 644 %{SOURCE3} %{buildroot}%{_sysconfdir}/syslog-ng.conf

%post
%_post_service %{name}

%preun
%_preun_service %{name}

%postun
if [ "$1" -ge 1 ]; then
	%{_sysconfdir}/rc.d/init.d/syslog-ng condrestart
fi

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc AUTHORS COPYING README ChangeLog NEWS VERSION
%doc doc/examples doc/reference doc/security
%config(noreplace) %{_sysconfdir}/syslog-ng.conf
%{_initrddir}/syslog-ng
/sbin/syslog-ng
%{_mandir}/man5/syslog-ng.conf.5*
%{_mandir}/man8/syslog-ng.8*
