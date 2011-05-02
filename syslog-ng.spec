%define name    syslog-ng
%define version 3.2.3
%define release %mkrel 1
# syslog-ng is now plugins based
%define _disable_ld_no_undefined 1

%define major 0
%define libname %mklibname syslog-ng %{major}
%define develname %mklibname syslog-ng -d

Name:		%{name}
Version:	%{version}
Release:	%{release}
Summary:	Syslog-ng daemon
Group:		System/Kernel and hardware
License:	GPL
Url:		http://www.balabit.com/products/syslog_ng/
Source0: 	http://www.balabit.com/downloads/files/syslog-ng/open-source-edition/%{version}/source/%{name}_%{version}.tar.gz
Source1:	syslog-ng.sysconfig
Source2:	syslog-ng.init
Source3:	syslog-ng.conf
Source4:	syslog-ng.logrotate
Source5:	http://www.balabit.com/dl/guides/syslog-ng-ose-v3.2-guide-admin-en_0.pdf
Source6:	syslog-ng.sleep
BuildRequires:	flex
BuildRequires:	bison
BuildRequires:	libol-devel >= 0.2.23
BuildRequires:	net-devel >= 1.1.3
BuildRequires:	eventlog-devel
BuildRequires:	glib2-devel
BuildRequires:	libwrap-devel
BuildRequires:	openssl-devel
BuildRequires:	dbi-devel
Provides:       syslog-daemon
Requires(post):	ccp
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

%package -n %{libname}
Summary:        Libraries for %{name}
Group:          Development/C

%description -n %{libname}
The libraries for %{name}.

%package -n %develname
Summary:        Development files for %{name}
Group:          Development/C
Provides:       %{name}-devel
Requires:       %{libname} = %{version}-%{release}

%description -n %develname
This package contains libraries and header files for
developing applications that use %{name}.

%prep
%setup -q -n %{name}-%{version}

cp %{SOURCE5} syslog-ng-ose-v3.2-guide-admin-en_0.pdf

%build
export CFLAGS="%{optflags} -fPIC"
%configure2_5x \
    --sbindir=/sbin \
    --sysconfdir=%{_sysconfdir}/syslog-ng \
    --localstatedir=%{_localstatedir}/lib/syslog-ng \
    --datadir=%{_datadir}/syslog-ng \
    --libdir=/%{_lib} \
    --with-pidfile-dir=%{_localstatedir}/run \
    --with-module-dir=/%{_lib}/syslog-ng \
    --enable-dynamic-linking \
    --enable-ipv6 \
    --enable-tcp-wrapper \
    --enable-spoof-source \
    --enable-ssl \
    --enable-pacct
%make

%install
rm -rf %{buildroot}
%makeinstall_std

# init script
install -d -m 755 %{buildroot}%{_initrddir}
install -m 755 %{SOURCE2} %{buildroot}%{_initrddir}/syslog-ng
install -d -m 755 %{buildroot}%{_sysconfdir}/sysconfig
install -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/sysconfig/syslog-ng
install -m 644 %{SOURCE3} %{buildroot}%{_sysconfdir}/syslog-ng/syslog-ng.conf
install -d -m 755 %{buildroot}%{_sysconfdir}/logrotate.d
install -m 644  %{SOURCE4} %{buildroot}%{_sysconfdir}/logrotate.d/syslog-ng
install -d -m 755 %{buildroot}%{_libdir}/pm-utils/sleep.d
install -m 755 %{SOURCE6} %{buildroot}%{_libdir}/pm-utils/sleep.d/05syslog-ng

install -d -m 755 %{buildroot}%{_sysconfdir}/syslog-ng/syslog-ng.d
install -d -m 755 %{buildroot}%{_sysconfdir}/syslog-ng/patterndb.d
install -d -m 755 %{buildroot}%{_localstatedir}/lib/syslog-ng

%post
ccp -i -d --set NoOrphans \
    -o %{_sysconfdir}/syslog-ng/syslog-ng.conf \
    -n %{_sysconfdir}/syslog-ng/syslog-ng.conf.rpmnew
ccp -i -d --set NoOrphans \
    -o %{_sysconfdir}/sysconfig/syslog-ng \
    -n %{_sysconfdir}/sysconfig/syslog-ng.rpmnew
%_post_service %{name}

%preun
%_preun_service %{name}

%clean
rm -rf %{buildroot}

%triggerprein -- syslog-ng < 3.2
# move the configuration files in new location
if [ ! -d /etc/syslog-ng ]; then
    mkdir /etc/syslog-ng
    mv /etc/syslog-ng.conf /etc/syslog-ng
    mv /etc/syslog-ng.d /etc/syslog-ng
    mv /etc/patterndb.d /etc/syslog-ng
fi

%files
%defattr(-,root,root)
%doc README AUTHORS COPYING ChangeLog NEWS VERSION
%doc doc/examples doc/security doc/xsd
%doc syslog-ng-ose-v3.2-guide-admin-en_0.pdf
%dir %{_sysconfdir}/syslog-ng  
%dir %{_sysconfdir}/syslog-ng/syslog-ng.d 
%dir %{_sysconfdir}/syslog-ng/patterndb.d
%config(noreplace) %{_sysconfdir}/syslog-ng/syslog-ng.conf  
%config(noreplace) %{_sysconfdir}/syslog-ng/modules.conf  
%config(noreplace) %{_sysconfdir}/syslog-ng/scl.conf  
%config(noreplace) %{_sysconfdir}/sysconfig/syslog-ng
%config(noreplace) %{_sysconfdir}/logrotate.d/syslog-ng
%{_initrddir}/syslog-ng
/sbin/syslog-ng
/sbin/syslog-ng-ctl
/%{_lib}/syslog-ng
%{_bindir}/loggen
%{_bindir}/pdbtool
%{_bindir}/update-patterndb
%{_libdir}/pm-utils/sleep.d/05syslog-ng
%{_datadir}/syslog-ng
%{_mandir}/man1/pdbtool.1*
%{_mandir}/man1/loggen.1*
%{_mandir}/man1/syslog-ng-ctl.1*
%{_mandir}/man5/syslog-ng.conf.5*
%{_mandir}/man8/syslog-ng.8*
%{_localstatedir}/lib/syslog-ng

%files -n %{libname}
%defattr(-,root,root)
/%{_lib}/*.so.*

%files -n %{develname}
%defattr(-,root,root)
/%{_lib}/*.so
/%{_lib}/*.la
