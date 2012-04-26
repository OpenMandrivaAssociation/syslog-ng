%define _disable_ld_no_undefined 1
%define evtlog_ver	0.2.12

%define name    syslog-ng
%define version 3.3.5
%define release 1

%define major 0
%define libname %mklibname syslog-ng %{major}
%define develname %mklibname syslog-ng -d

Name:		%{name}
Version:	%{version}
Release:	%{release}
Summary:	Syslog-ng daemon
Group:		System/Kernel and hardware
License:	GPLv2 LGPLv2+
Url:		http://www.balabit.com/products/syslog_ng/
Source0: 	http://www.balabit.com/downloads/files/syslog-ng/open-source-edition/%{version}/source/%{name}_%{version}.tar.gz
Source1:	http://www.balabit.com/support/documentation/syslog-ng-ose-v3.2-guide-admin-en.pdf
Source2:	syslog-ng.sysconfig
Source3:	syslog-ng.conf
Source4:	syslog-ng.logrotate
Source5:	syslog-ng.init
Source6:	syslog-ng.sleep
Source7:	syslog-ng.service
BuildRequires:	flex
BuildRequires:	bison
BuildRequires:	eventlog-devel >= %{evtlog_ver}
BuildRequires:	net-devel >= 1.1.3
BuildRequires:	glib2-devel
BuildRequires:	libwrap-devel
BuildRequires:	openssl-devel
BuildRequires:	dbi-devel
BuildRequires:	cap-devel
BuildRequires:	pkgconfig(json)
Provides:       syslog-daemon

%description
Syslog-ng is a flexible and highly scalable system logging application
that is ideal for creating centralized and trusted logging solutions.
Syslog-ng enables you to send the log messages of your hosts to remote
servers using the latest protocol standards : TCP, TLS, X.509 certificates.
Syslog-ng is able to store log messages in the most popular databases :
MySQL, PostgreSQL SQLite, Oracle and MSSQL. Syslog-ng can sort the incoming
log messages based on their content and various parameters like the source
host, application, and priority. Directories, files and database tables can
be created dynamically using macros. Complex filtering using regular
expressions and boolean operators offers almost unlimited flexibility to
forward only the important log messages to the selected destinations.

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
cp %{SOURCE1} .

%build

# XXX: workaround for the default configure paths
%define _sbindir /sbin
%define _sysconfdir /etc/syslog-ng
%define _datadir %{_usr}/share/syslog-ng
%define _libdir /%{_lib}
%define _localstatedir %{_var}/lib/syslog-ng

%configure2_5x \
	--with-pidfile-dir=%{_var}/run \
	--with-module-dir=/%{_lib}/syslog-ng \
	--enable-dynamic-linking \
	--enable-ipv6 \
	--enable-linux-caps \
	--enable-pacct \
	--enable-spoof-source \
	--enable-ssl \
	--enable-tcp-wrapper
	 # --enable-env-wrapper \
%make

%install

%makeinstall_std

# XXX: enforce default paths
%define _sbindir /sbin
%define _sysconfdir /etc
%define _datadir /usr/share
%define _libdir /usr/%{_lib}
%define _localstatedir /var

install -d -m 755 %{buildroot}%{_sysconfdir}/syslog-ng/syslog-ng.d
install -d -m 755 %{buildroot}%{_sysconfdir}/syslog-ng/patterndb.d

install -d -m 755 %{buildroot}%{_sysconfdir}/sysconfig
install -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/sysconfig/syslog-ng

install -m 644 %{SOURCE3} %{buildroot}%{_sysconfdir}/syslog-ng/syslog-ng.conf

install -d -m 755 %{buildroot}%{_sysconfdir}/logrotate.d
install -m 644  %{SOURCE4} %{buildroot}%{_sysconfdir}/logrotate.d/syslog-ng

# init script
install -d -m 755 %{buildroot}%{_initrddir}
install -m 755 %{SOURCE5} %{buildroot}%{_initrddir}/syslog-ng

install -d -m 755 %{buildroot}%{_libdir}/pm-utils/sleep.d
install -m 755 %{SOURCE6} %{buildroot}%{_libdir}/pm-utils/sleep.d/05syslog-ng

install -d -m 755 %{buildroot}%{_unitdir}
install -m 644 %{SOURCE7} %{buildroot}%{_unitdir}/syslog-ng.service

install -d -m 755 %{buildroot}%{_localstatedir}/lib/syslog-ng

rm -f %{buildroot}/%{_lib}/*.la
mv %{buildroot}/%{_lib}/pkgconfig %{buildroot}%{_libdir}/pkgconfig

%post
%_post_service %{name}
# (cg) Handle a quirk of syslog service installations
if [ -f %{_sysconfdir}/systemd/system/multi-user.target.wants/%{name}.service -a ! -f %{_sysconfdir}/systemd/system/syslog.service ]; then
  cp -a %{_sysconfdir}/systemd/system/multi-user.target.wants/%{name}.service %{_sysconfdir}/systemd/system/syslog.service
fi

%preun
%_preun_service %{name}

%files
%defattr(-,root,root)
%doc AUTHORS ChangeLog COPYING NEWS VERSION
%doc doc/security doc/xsd
%doc syslog-ng-ose-v3.2-guide-admin-en.pdf
%dir %{_sysconfdir}/syslog-ng  
%dir %{_sysconfdir}/syslog-ng/syslog-ng.d 
%dir %{_sysconfdir}/syslog-ng/patterndb.d
%dir /%{_lib}/syslog-ng
%config(noreplace) %{_sysconfdir}/syslog-ng/syslog-ng.conf  
%config(noreplace) %{_sysconfdir}/syslog-ng/modules.conf  
%config(noreplace) %{_sysconfdir}/syslog-ng/scl.conf  
%config(noreplace) %{_sysconfdir}/sysconfig/syslog-ng
%config(noreplace) %{_sysconfdir}/logrotate.d/syslog-ng
%{_initrddir}/syslog-ng
%{_unitdir}/syslog-ng.service
%{_sbindir}/syslog-ng
%{_sbindir}/syslog-ng-ctl
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
/%{_lib}/libsyslog-ng-%{version}.so

%files -n %{develname}
/%{_lib}/libsyslog-ng.so
/%{_lib}/%{name}/libafmongodb.so
/%{_lib}/%{name}/libafprog.so
/%{_lib}/%{name}/libafsocket-notls.so
/%{_lib}/%{name}/libafsocket-tls.so
/%{_lib}/%{name}/libafsocket.so
/%{_lib}/%{name}/libafsql.so
/%{_lib}/%{name}/libafuser.so
/%{_lib}/%{name}/libbasicfuncs.so
/%{_lib}/%{name}/libconfgen.so
/%{_lib}/%{name}/libconvertfuncs.so
/%{_lib}/%{name}/libcsvparser.so
/%{_lib}/%{name}/libdbparser.so
/%{_lib}/%{name}/libdummy.so
/%{_lib}/%{name}/libpacctformat.so
/%{_lib}/%{name}/libsyslog-ng-crypto.so
/%{_lib}/%{name}/libsyslogformat.so
/%{_lib}/%{name}/libtfjson.so
/%{_lib}/%{name}/libaffile.so

%{_libdir}/pkgconfig/syslog-ng.pc
%{_includedir}/syslog-ng
