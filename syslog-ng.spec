%define name    syslog-ng
%define version 1.6.9
%define release %mkrel 1

Summary:	Syslog-ng daemon
Name:		%{name}
Version:	%{version}
Release:	%{release}
Group:		System/Kernel and hardware
License:	GPL
Url:		http://www.balabit.com/products/syslog_ng/
Source0: 	http://www.balabit.com/downloads/syslog-ng/1.6/src/%{name}-%{version}.tar.gz
Source1: 	http://www.balabit.com/downloads/syslog-ng/1.6/src/%{name}-%{version}.tar.gz.asc
Source2:	syslog-ng.init
Source3:	syslog-ng.conf
Source4:	syslog-ng.logrotate
Patch0:		syslog-ng-1.6.5-conf.patch
BuildRequires:	flex
BuildRequires:	libol-devel >= 0.2.23
Requires(post):	chkconfig
Requires(preun):chkconfig
Buildroot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

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
%patch0 -p1

%build
%configure --sbindir=/sbin
%make

%install
[ -n "%{buildroot}" -a "%{buildroot}" != / ] && rm -rf %{buildroot}

mkdir -p %{buildroot}%{_initrddir}
%{makeinstall_std} sbindir=/sbin sysconfdir=%{_sysconfdir} \
  mandir=%{_mandir} prefix=%{_prefix}

install -m755 %{SOURCE2} %{buildroot}%{_initrddir}/syslog-ng
install -m644 %{SOURCE3} %{buildroot}%{_sysconfdir}/syslog-ng.conf

%post
if [ "$1" -eq 1 ]; then
	/sbin/chkconfig --add syslog-ng
	/sbin/chkconfig syslog-ng off
fi

%preun
if [ "$1" -eq 0 ] ; then
	if [ -f /var/lock/subsys/syslog-ng ]; then
		%{_sysconfdir}/rc.d/init.d/syslog-ng stop
	fi
	/sbin/chkconfig --del syslog-ng
fi

%postun
if [ "$1" -ge 1 ]; then
	%{_sysconfdir}/rc.d/init.d/syslog-ng condrestart
fi

%clean
[ -n "%{buildroot}" -a "%{buildroot}" != / ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc AUTHORS COPYING README ChangeLog INSTALL NEWS PORTS
%doc doc/sgml/syslog-ng.txt
%doc doc/*.demo doc/*.sample doc/*.solaris
%config(noreplace) %{_sysconfdir}/syslog-ng.conf
%config(noreplace) %{_initrddir}/syslog-ng
/sbin/syslog-ng
%{_mandir}/man5/syslog-ng.conf.5*
%{_mandir}/man8/syslog-ng.8*

