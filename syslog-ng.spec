%define name    syslog-ng
%define version 2.0.6
%define release %mkrel 1

Name:		%{name}
Version:	%{version}
Release:	%{release}
Summary:	Syslog-ng daemon
Group:		System/Kernel and hardware
License:	GPL
Url:		http://www.balabit.com/products/syslog_ng/
Source0: 	http://www.balabit.com/downloads/syslog-ng/2.0/src/%{name}-%{version}.tar.bz2
Source1:	syslog-ng.sysconfig
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
Provides:       syslog-daemon
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

# init script
install -d -m 755 %{buildroot}%{_initrddir}
install -m 755 %{SOURCE2} %{buildroot}%{_initrddir}/syslog-ng
install -d -m 755 %{buildroot}%{_sysconfdir}/sysconfig
install -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/sysconfig/syslog-ng

install -m 644 %{SOURCE3} %{buildroot}%{_sysconfdir}/syslog-ng.conf

install -d -m 755 %{buildroot}%{_docdir}/%{name}
install -m 644 README AUTHORS COPYING ChangeLog NEWS VERSION %{buildroot}%{_docdir}/%{name}
install -d -m 755 %{buildroot}%{_docdir}/%{name}/{reference,examples,security}
install -m 644 doc/examples/* %{buildroot}%{_docdir}/%{name}/examples
install -m 644 doc/security/* %{buildroot}%{_docdir}/%{name}/security
install -m 644 doc/reference/syslog-ng.txt %{buildroot}%{_docdir}/%{name}/reference
tar xzf doc/reference/syslog-ng.html.tar.gz --to-stdout syslog-ng.html/index.html > %{buildroot}%{_docdir}/%{name}/reference/syslog-ng.html
install -m 644 doc/reference/syslog-ng.txt %{buildroot}%{_docdir}/%{name}/reference

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
%{_docdir}/%{name}
%config(noreplace) %{_sysconfdir}/syslog-ng.conf
%config(noreplace) %{_sysconfdir}/sysconfig/syslog-ng
%{_initrddir}/syslog-ng
/sbin/syslog-ng
%{_mandir}/man5/syslog-ng.conf.5*
%{_mandir}/man8/syslog-ng.8*
