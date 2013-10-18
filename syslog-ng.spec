%define _disable_ld_no_undefined 1
%define evtlog_ver  0.2.12


%define _tmpfilesdir /usr/lib/tmpfiles.d
%define _tmpfilescreate() /bin/systemd-tmpfiles --create %{1}.conf

%define name syslog-ng
%define version 3.4.4
%define release 1

%define major %{version}
%define libname %mklibname syslog-ng %{major}
%define develname %mklibname syslog-ng -d

Name:       %{name}
Version:    %{version}
Release:    %{release}
Summary:    Syslog-ng daemon
Group:      System/Kernel and hardware
License:    GPLv2 LGPLv2+
Url:        http://www.balabit.com/products/syslog_ng/
Source0:    http://www.balabit.com/downloads/files/syslog-ng/open-source-edition/%{version}/source/%{name}_%{version}.tar.gz
Source1:    http://www.balabit.com/support/documentation/syslog-ng-ose-v3.2-guide-admin-en.pdf
Source2:    syslog-ng.sysconfig
Source3:    syslog-ng.conf
Source4:    syslog-ng.logrotate
Source5:    syslog-ng.tmpfiles
Patch0:     syslog-ng-3.4.3-service-configuration.patch
BuildRequires:  flex
BuildRequires:  bison
BuildRequires:  eventlog-devel >= %{evtlog_ver}
BuildRequires:  libnet-devel >= 1.1.3
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  libwrap-devel
BuildRequires:  openssl-devel
BuildRequires:  dbi-devel
BuildRequires:  cap-devel
Provides:       syslog-daemon
Requires:       %{libname} = %{version}-%{release}
Requires(post):  systemd
Requires(post):  rpm-helper
Requires(preun): rpm-helper

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
%patch0 -p 1

cp %{SOURCE1} .

%build
%configure2_5x \
    --prefix=%{_prefix} \
    --sysconfdir=%{_sysconfdir}/%{name} \
    --localstatedir=%{_localstatedir}/lib/%{name} \
    --datadir=%{_datadir}/%{name} \
    --with-module-dir=/%{_libdir}/%{name} \
    --with-pidfile-dir=/run/syslog-ng \
    --with-systemdsystemunitdir=%{_unitdir} \
    --enable-ipv6 \
    --enable-linux-caps \
    --disable-pacct \
    --enable-spoof-source \
    --enable-ssl \
    --enable-tcp-wrapper \
    --enable-shared \
    --disable-static \
    --enable-dynamic-linking \
    --enable-systemd
     # --enable-env-wrapper \
%make

%install
%makeinstall_std

install -m 644 %{SOURCE3} %{buildroot}%{_sysconfdir}/syslog-ng/syslog-ng.conf
install -d -m 755 %{buildroot}%{_sysconfdir}/syslog-ng/conf.d
install -d -m 755 %{buildroot}%{_sysconfdir}/syslog-ng/patterndb.d

install -D -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/sysconfig/syslog-ng

install -D -m 644 %{SOURCE4} %{buildroot}%{_sysconfdir}/logrotate.d/syslog-ng

install -D -m 644 %{SOURCE5} %{buildroot}%{_tmpfilesdir}/%{name}.conf

install -d -m 755 %{buildroot}%{_localstatedir}/lib/syslog-ng

# install the ld.so conf file
install -d -m 755 %{buildroot}%{_sysconfdir}/ld.so.conf.d/
cat > %{buildroot}%{_sysconfdir}/ld.so.conf.d/%{name}.conf <<EOF
%{_libdir}/%{name}
EOF

sed -i 's!//!/!g' %{buildroot}/%{_libdir}/pkgconfig/*.pc

rm -f %{buildroot}%{_libdir}/*.la

%post
%_tmpfilescreate %{name}
%_post_service %{name}
# (cg) Handle a quirk of syslog service installations
if [ -f %{_sysconfdir}/systemd/system/multi-user.target.wants/%{name}.service -a ! -f %{_sysconfdir}/systemd/system/syslog.service ]; then
  cp -a %{_sysconfdir}/systemd/system/multi-user.target.wants/%{name}.service %{_sysconfdir}/systemd/system/syslog.service
fi

%preun
%_preun_service %{name}

%files
%doc AUTHORS COPYING NEWS VERSION
%doc doc/security doc/xsd
%doc syslog-ng-ose-v3.2-guide-admin-en.pdf
%dir %{_sysconfdir}/syslog-ng
%dir %{_sysconfdir}/syslog-ng/conf.d
%dir %{_sysconfdir}/syslog-ng/patterndb.d
%config(noreplace) %{_sysconfdir}/syslog-ng/syslog-ng.conf
#%config(noreplace) %{_sysconfdir}/syslog-ng/modules.conf
%config(noreplace) %{_sysconfdir}/syslog-ng/scl.conf
%config(noreplace) %{_sysconfdir}/sysconfig/syslog-ng
%config(noreplace) %{_sysconfdir}/logrotate.d/syslog-ng
%{_unitdir}/syslog-ng.service
%{_tmpfilesdir}/%{name}.conf
%{_sysconfdir}/ld.so.conf.d/%{name}.conf
%{_sbindir}/syslog-ng
%{_sbindir}/syslog-ng-ctl
%{_libdir}/syslog-ng
%{_bindir}/loggen
%{_bindir}/pdbtool
%{_bindir}/update-patterndb
%{_datadir}/syslog-ng
%{_mandir}/man1/pdbtool.1*
%{_mandir}/man1/loggen.1*
%{_mandir}/man1/syslog-ng-ctl.1*
%{_mandir}/man5/syslog-ng.conf.5*
%{_mandir}/man8/syslog-ng.8*
%{_localstatedir}/lib/syslog-ng

%files -n %{libname}
%{_libdir}/libsyslog-ng-%{version}.so

%files -n %{develname}
%{_libdir}/libsyslog-ng.so
%{_libdir}/pkgconfig/syslog-ng.pc
%{_includedir}/syslog-ng
