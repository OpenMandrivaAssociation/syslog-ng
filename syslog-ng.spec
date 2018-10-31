%global ivykis_ver 0.42.3

%define syslog_ng_major_ver %(echo %{version} |cut -d. -f1)
%define syslog_ng_minor_ver %(echo %{version} |cut -d. -f2)
%define syslog_ng_patch_ver %(echo %{version} |cut -d. -f3)
%define syslog_ng_major_minor_ver %{syslog_ng_major_ver}.%{syslog_ng_minor_ver}

Name:    syslog-ng
Version: 3.17.2
Release: 2
Summary: Next-generation syslog server

Group:   System Environment/Daemons
License: GPLv2+
URL:     https://syslog-ng.org/
Source0: https://github.com/balabit/syslog-ng/releases/download/syslog-ng-%{version}/%{name}-%{version}.tar.gz
Source1: syslog-ng.conf
Source2: syslog-ng.logrotate
Source3: syslog-ng.service

BuildRequires: systemd-units
BuildRequires: pkgconfig
BuildRequires: libtool
BuildRequires: bison, flex
BuildRequires: xsltproc
BuildRequires: json-c-devel
BuildRequires: libcap-devel
BuildRequires: pkgconfig(dbi)
BuildRequires: libnet-devel
BuildRequires: openssl-devel
BuildRequires: pcre-devel
BuildRequires: libuuid-devel
BuildRequires: libesmtp-devel
BuildRequires: GeoIP-devel
BuildRequires: pkgconfig(systemd)
BuildRequires: systemd-macros
BuildRequires: java-devel
BuildRequires: pkgconfig(libcurl)
BuildRequires: snappy-devel
BuildRequires: pkgconfig(hiredis)
BuildRequires: pkgconfig(glib-2.0) pkgconfig(gmodule-2.0) pkgconfig(gthread-2.0)

Requires: logrotate
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units

Provides: syslog
# merge separate syslog-vim package into one
Provides: syslog-ng-vim = %{version}-%{release}
Obsoletes: syslog-ng-vim < 2.0.8-1

# Fedora 17’s unified filesystem (/usr-move)
Conflicts: filesystem < 3

Obsoletes: syslog-ng-json < 3.8

%description
syslog-ng is an enhanced log daemon, supporting a wide range of input and
output methods: syslog, unstructured text, message queues, databases (SQL
and NoSQL alike) and more.

Key features:

 * receive and send RFC3164 and RFC5424 style syslog messages
 * work with any kind of unstructured data
 * receive and send JSON formatted messages
 * classify and structure logs with builtin parsers (csv-parser(),
   db-parser(), ...)
 * normalize, crunch and process logs as they flow through the system
 * hand on messages for further processing using message queues (like
   AMQP), files or databases (like PostgreSQL or MongoDB).


%package libdbi
Summary: libdbi support for %{name}
Group: Development/Libraries
Requires: %{name}%{?_isa} = %{version}-%{release}

%description libdbi
This module supports a large number of database systems via libdbi.


%package mongodb
Summary: mongodb support for %{name}
Group: Development/Libraries
Requires: %{name}%{?_isa} = %{version}-%{release}

%description mongodb
This module supports the mongodb database via libmongo-client.


%package smtp
Summary: smtp support for %{name}
Group: Development/Libraries
Requires: %{name}%{?_isa} = %{version}-%{release}

%description smtp
This module supports sending e-mail alerts through an smtp server.

%package java
Summary:        Java destination support for syslog-ng
Group:          System/Libraries
Requires:       %{name} = %{version}
 
%description java
This package provides java destination support for syslog-ng.

%package geoip
Summary: geoip support for %{name}
Group: Development/Libraries
Requires: %{name}%{?_isa} = %{version}-%{release}

%description geoip
This template function returns the 2-letter country code of
any IPv4 address or host.


%package redis
Summary: redis support for %{name}
Group: Development/Libraries
Requires: %{name}%{?_isa} = %{version}-%{release}

%description redis
This module supports the redis key-value store via hiredis.

%package riemann
Summary: riemann support for %{name}
Group: Development/Libraries
Requires: %{name}%{?_isa} = %{version}-%{release}

%description riemann
This module supports the riemann monitoring server.

%package http
Summary: http support for %{name}
Group: Development/Libraries
Requires: %{name}%{?_isa} = %{version}-%{release}
Obsoletes: %{name}-curl < 3.10

%description http
This module supports the http destination.

%package amqp
Summary: AMQP support for %{name}
Requires: %{name}%{?_isa} = %{version}-%{release}

%description amqp
This module supports the AMQP destination.

%package devel
Summary: Development files for %{name}
Group: Development/Libraries
Requires: %{name}%{?_isa} = %{version}-%{release}

%description devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.


%prep
%autosetup -p 1
# fix perl path
%{__sed} -i 's|^#!/usr/local/bin/perl|#!%{__perl}|' contrib/relogger.pl

# fix executable perms on contrib files
%{__chmod} -c a-x contrib/syslog2ng

# fix authors file
/usr/bin/iconv -f iso8859-1 -t utf-8 AUTHORS > AUTHORS.conv && \
    %{__mv} -f AUTHORS.conv AUTHORS


%build
export GEOIP_LIBS=-lGeoIP
export PYTHON=%{__python2}
%configure \
    --prefix=%{_prefix} \
    --sysconfdir=%{_sysconfdir}/%{name} \
    --localstatedir=%{_sharedstatedir}/%{name} \
    --datadir=%{_datadir} \
    --with-module-dir=/%{_libdir}/%{name} \
    --with-systemdsystemunitdir=%{_unitdir} \
    --with-embedded-crypto \
    --enable-manpages \
    --enable-ipv6 \
    --enable-spoof-source \
    --with-linux-caps=auto \
    --enable-sql \
    --enable-json \
    --enable-ssl \
    --enable-smtp \
    --enable-geoip \
    --enable-shared \
    --disable-static \
    --enable-dynamic-linking \
    --enable-systemd \
    --enable-redis \
    --disable-python \
    --enable-java \
    --disable-java-modules \
    --disable-mongodb

# We don't currently have libraries required by
#    --enable-amqp
#    --enable-riemann
#    --enable-mongodb


# remove rpath
#sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
#sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool

make %{_smp_mflags}


%install
make DESTDIR=%{buildroot} install

%{__install} -d -m 755 %{buildroot}%{_sysconfdir}/%{name}/conf.d
%{__install} -p -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/%{name}/syslog-ng.conf

%{__install} -d -m 755 %{buildroot}%{_sysconfdir}/logrotate.d
%{__install} -p -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/syslog

%{__install} -d -m 755 %{buildroot}%{_prefix}/lib/systemd/system
%{__install} -p -m 644 %{SOURCE3} %{buildroot}%{_unitdir}/%{name}.service

# create the local state dir
%{__install} -d -m 755 %{buildroot}/%{_sharedstatedir}/%{name}

# install the main library header files
%{__install} -d -m 755 %{buildroot}%{_includedir}/%{name}
%{__install} -p -m 644 config.h %{buildroot}%{_includedir}/%{name}
%{__install} -p -m 644 lib/*.h %{buildroot}%{_includedir}/%{name}

# install vim files
%{__install} -d -m 755 %{buildroot}%{_datadir}/%{name}
%{__install} -p -m 644 contrib/syslog-ng.vim %{buildroot}%{_datadir}/%{name}
for vimver in 81 ; do
    %{__install} -d -m 755 %{buildroot}%{_datadir}/vim/vim$vimver/syntax
    cd %{buildroot}%{_datadir}/vim/vim$vimver/syntax
    ln -s ../../../%{name}/syslog-ng.vim .
    cd -
done

find %{buildroot} -name "*.la" -exec rm -f {} \;

# remove some extra testing related files
rm %{buildroot}%{_unitdir}/%{name}@.service

# %check
# LD_LIBRARY_PATH=%{buildroot}/%{_libdir}:%{buildroot}/%{_libdir}/%{name} VERBOSE=1 make check

%post
ldconfig
%systemd_post syslog-ng.service

%preun
%systemd_preun syslog-ng.service

%postun
ldconfig
%systemd_postun_with_restart syslog-ng.service


%triggerun -- syslog-ng < 3.2.3
if /sbin/chkconfig --level 3 %{name} ; then
    /bin/systemctl enable %{name}.service >/dev/null 2>&1 || :
fi


%triggerin -- vim-common
VIMVERNEW=`rpm -q --qf='%%{epoch}:%%{version}\n' vim-common | sort | tail -n 1 | sed -e 's/[0-9]*://' | sed -e 's/\.[0-9]*$//' | sed -e 's/\.//'`
[ -d %{_datadir}/vim/vim${VIMVERNEW}/syntax ] && \
    cd %{_datadir}/vim/vim${VIMVERNEW}/syntax && \
    ln -sf ../../../%{name}/syslog-ng.vim . || :

%triggerun -- vim-common
VIMVEROLD=`rpm -q --qf='%%{epoch}:%%{version}\n' vim-common | sort | head -n 1 | sed -e 's/[0-9]*://' | sed -e 's/\.[0-9]*$//' | sed -e 's/\.//'`
[ $2 = 0 ] && rm -f %{_datadir}/vim/vim${VIMVEROLD}/syntax/syslog-ng.vim || :

%triggerpostun -- vim-common
VIMVEROLD=`rpm -q --qf='%%{epoch}:%%{version}\n' vim-common | sort | head -n 1 | sed -e 's/[0-9]*://' | sed -e 's/\.[0-9]*$//' | sed -e 's/\.//'`
VIMVERNEW=`rpm -q --qf='%%{epoch}:%%{version}\n' vim-common | sort | tail -n 1 | sed -e 's/[0-9]*://' | sed -e 's/\.[0-9]*$//' | sed -e 's/\.//'`
if [ $1 = 1 ]; then
    rm -f %{_datadir}/vim/vim${VIMVEROLD}/syntax/syslog-ng.vim || :
    [ -d %{_datadir}/vim/vim${VIMVERNEW}/syntax ] && \
        cd %{_datadir}/vim/vim${VIMVERNEW}/syntax && \
        ln -sf ../../../%{name}/syslog-ng.vim . || :
fi


%files
%doc AUTHORS COPYING NEWS.md
%doc contrib/{relogger.pl,syslog2ng,syslog-ng.conf.doc}

%dir %{_sysconfdir}/syslog-ng
%dir %{_sysconfdir}/syslog-ng/conf.d
%dir %{_sysconfdir}/syslog-ng/patterndb.d
%config(noreplace) %{_sysconfdir}/logrotate.d/syslog
%config(noreplace) %{_sysconfdir}/syslog-ng/scl.conf
%config(noreplace) %{_sysconfdir}/syslog-ng/syslog-ng.conf

%{_unitdir}/syslog-ng.service

%dir %{_sharedstatedir}/syslog-ng

%{_sbindir}/syslog-ng
%{_sbindir}/syslog-ng-ctl
%{_sbindir}/syslog-ng-debun

%{_bindir}/dqtool
%{_bindir}/loggen
%{_bindir}/pdbtool
%{_bindir}/update-patterndb

%{_libdir}/libevtlog-%{syslog_ng_major_minor_ver}.so.0
%{_libdir}/libevtlog-%{syslog_ng_major_minor_ver}.so.0.0.0
%{_libdir}/libloggen_helper-%{syslog_ng_major_minor_ver}.so.0
%{_libdir}/libloggen_helper-%{syslog_ng_major_minor_ver}.so.0.0.0
%{_libdir}/libloggen_plugin-%{syslog_ng_major_minor_ver}.so.0
%{_libdir}/libloggen_plugin-%{syslog_ng_major_minor_ver}.so.0.0.0
%{_libdir}/libsecret-storage.so.0
%{_libdir}/libsecret-storage.so.0.0.0
%{_libdir}/libsyslog-ng-%{syslog_ng_major_minor_ver}.so.0
%{_libdir}/libsyslog-ng-%{syslog_ng_major_minor_ver}.so.0.0.0

%dir %{_libdir}/syslog-ng
%{_libdir}/syslog-ng/*.so

%dir %{_libdir}/syslog-ng/loggen
%{_libdir}/syslog-ng/loggen/libloggen_socket_plugin.so
%{_libdir}/syslog-ng/loggen/libloggen_ssl_plugin.so

%exclude %{_libdir}/syslog-ng/libafsmtp.so
%exclude %{_libdir}/syslog-ng/libafsql.so
%exclude %{_libdir}/syslog-ng/libgeoip2-plugin.so
%exclude %{_libdir}/syslog-ng/libgeoip-plugin.so
%exclude %{_libdir}/syslog-ng/libhttp.so
%exclude %{_libdir}/syslog-ng/libmod-java.so
%exclude %{_libdir}/syslog-ng/libredis.so

%dir %{_datadir}/syslog-ng
%{_datadir}/syslog-ng/syslog-ng.vim
%ghost %{_datadir}/vim/

# scl files
%{_datadir}/syslog-ng/include/

# uhm, some better places for those?
%{_datadir}/syslog-ng/xsd/

%{_mandir}/man1/loggen.1*
%{_mandir}/man1/pdbtool.1*
%{_mandir}/man1/syslog-ng-ctl.1*
%{_mandir}/man1/syslog-ng-debun.1*
%{_mandir}/man1/dqtool.1*
%{_mandir}/man5/syslog-ng.conf.5*
%{_mandir}/man8/syslog-ng.8*

%files libdbi
%{_libdir}/syslog-ng/libafsql.so

%files redis
%{_libdir}/syslog-ng/libredis.so

%files smtp
%{_libdir}/syslog-ng/libafsmtp.so

%files java
%attr(755,root,root) %{_libdir}/syslog-ng/libmod-java.so
%dir %{_libdir}/syslog-ng/java-modules/
%{_libdir}/syslog-ng/java-modules/*

%files geoip
%{_libdir}/syslog-ng/libgeoip-plugin.so
%if 0
%{_libdir}/syslog-ng/libgeoip2-plugin.so
%endif

%files http
%{_libdir}/syslog-ng/libhttp.so

%if 0
%files riemann
%{_libdir}/syslog-ng/libriemann.so

%files amqp
%{_libdir}/syslog-ng/libafamqp.so

%files mongodb
%{_libdir}/syslog-ng/libafmongodb.so
%endif

%files devel
%{_datadir}/syslog-ng/tools/
%{_includedir}/syslog-ng/
%{_libdir}/libevtlog.so
%{_libdir}/libloggen_helper.so
%{_libdir}/libloggen_plugin.so
%{_libdir}/libsecret-storage.so
%{_libdir}/libsyslog-ng-native-connector.a
%{_libdir}/libsyslog-ng.so
%{_libdir}/pkgconfig/syslog-ng-native-connector.pc
%{_libdir}/pkgconfig/syslog-ng.pc
