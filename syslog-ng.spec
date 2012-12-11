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


%changelog
* Thu Apr 26 2012 Alexander Khrukin <akhrukin@mandriva.org> 3.3.5-1
+ Revision: 793564
- BR:pkgconfig(json)
- version update 3.3.5

  + Oden Eriksson <oeriksson@mandriva.com>
    - relink against libpcre.so.1

* Thu May 12 2011 Guillaume Rousse <guillomovitch@mandriva.org> 3.2.4-1
+ Revision: 673917
- update to new version 3.2.4

* Mon May 02 2011 Guillaume Rousse <guillomovitch@mandriva.org> 3.2.3-1
+ Revision: 662718
- update to new version 3.2.3

* Sun Jan 16 2011 Guillaume Rousse <guillomovitch@mandriva.org> 3.2.2-2
+ Revision: 631158
- new version
- ensure logrotate configuration get installed (#62217)
- let init script handle conditional reload

* Sun Dec 05 2010 Oden Eriksson <oeriksson@mandriva.com> 3.2.1-2mdv2011.0
+ Revision: 609663
- rebuilt against new libdbi

* Sat Nov 27 2010 Guillaume Rousse <guillomovitch@mandriva.org> 3.2.1-1mdv2011.0
+ Revision: 601850
- new version

* Mon Oct 18 2010 Guillaume Rousse <guillomovitch@mandriva.org> 3.2-0.beta1.2mdv2011.0
+ Revision: 586603
- enable pacct support
- allow plugins to be underlinked

* Sat Oct 16 2010 Guillaume Rousse <guillomovitch@mandriva.org> 3.2-0.beta1.1mdv2011.0
+ Revision: 586096
- new beta version

* Tue Oct 12 2010 Guillaume Rousse <guillomovitch@mandriva.org> 3.2-0.git.1mdv2011.0
+ Revision: 585240
- new git snapshot (nearly beta1)
- configuration files are now in /etc/syslog-ng directory, and package upgrade
  should take care of transferring them
- use configuration switches instead of patches to fix files location

* Fri Aug 06 2010 Guillaume Rousse <guillomovitch@mandriva.org> 3.1.2-1mdv2011.0
+ Revision: 566501
- new version
- drop previous patch moving patterndb to /usr/share/syslog-ng instead of /var
- move all variable files under /var/lib/syslog-ng instead of /var

* Wed Jun 09 2010 Raphaël Gertz <rapsys@mandriva.org> 3.1.1-2mdv2010.1
+ Revision: 547311
- Fix release for rebuild
- Add merge config

* Mon Apr 12 2010 Guillaume Rousse <guillomovitch@mandriva.org> 3.1.1-1mdv2010.1
+ Revision: 533706
- new version

  + Funda Wang <fwang@mandriva.org>
    - rebuild

* Fri Mar 26 2010 Guillaume Rousse <guillomovitch@mandriva.org> 3.1.0-1mdv2010.1
+ Revision: 527592
- 3.1.0 final

  + Raphaël Gertz <rapsys@mandriva.org>
    - Remove tabs for 4spaces indentation
      Enable dir creation to avoid initial start fail on empty system

* Tue Feb 23 2010 Raphaël Gertz <rapsys@mandriva.org> 3.1-0.beta2.4mdv2010.1
+ Revision: 510435
- Add resume syslog-ng restart script
  Fix low number of max-connexion (#55807)
  Fix logrotate script

* Mon Jan 25 2010 Guillaume Rousse <guillomovitch@mandriva.org> 3.1-0.beta2.3mdv2010.1
+ Revision: 496474
- fix configuration file syntax

* Sun Jan 24 2010 Guillaume Rousse <guillomovitch@mandriva.org> 3.1-0.beta2.2mdv2010.1
+ Revision: 495360
- cosmetics: get back to plain spaces for indentation in configuration file
- set catchall flag to all log statements, in order to catch more easily content from external sources (such as postfix chroot)

* Thu Dec 31 2009 Guillaume Rousse <guillomovitch@mandriva.org> 3.1-0.beta2.1mdv2010.1
+ Revision: 484535
- update to beta2

* Fri Dec 11 2009 Guillaume Rousse <guillomovitch@mandriva.org> 3.1-0.beta1.2mdv2010.1
+ Revision: 476400
- update admin guide
- init script: don't remove lock when reloading

* Thu Dec 03 2009 Guillaume Rousse <guillomovitch@mandriva.org> 3.1-0.beta1.1mdv2010.1
+ Revision: 473023
- use /etc/syslog-ng.d directory for splitted configuration files
- update administrator guide
- new version

* Wed Oct 28 2009 Guillaume Rousse <guillomovitch@mandriva.org> 3.0.4-3mdv2010.0
+ Revision: 459853
- should start after network

* Fri Oct 16 2009 Guillaume Rousse <guillomovitch@mandriva.org> 3.0.4-2mdv2010.0
+ Revision: 457898
- add dbi-devel build dependency
- move pattern database default location to %%{_datadir}/%%{name}/patterndb.xml

* Thu Aug 20 2009 Guillaume Rousse <guillomovitch@mandriva.org> 3.0.4-1mdv2010.0
+ Revision: 418417
- new version
- drop merged patch
- drop undocumented %%postun hack

* Thu Jun 04 2009 Oden Eriksson <oeriksson@mandriva.com> 3.0.1-6mdv2010.0
+ Revision: 382701
- rebuilt against libnet 1.1.3

* Wed May 20 2009 Guillaume Rousse <guillomovitch@mandriva.org> 3.0.1-5mdv2010.0
+ Revision: 377827
- fix incorrect perms on init scripts, introduced in latest release

* Mon Apr 20 2009 Raphaël Gertz <rapsys@mandriva.org> 3.0.1-4mdv2009.1
+ Revision: 368104
- Add the same owner, group and perm as msec for log files
  Increase max-connections to avoid losing log
  Apply a patch reported upstream to resolve user correctly
  Change syslog-ng initscript file permissions to fit msec rule

* Sat Jan 31 2009 Raphaël Gertz <rapsys@mandriva.org> 3.0.1-3mdv2009.1
+ Revision: 335906
- Fix missing s in /var/log/daemons/errors.log file path
- Fix missing s in /var/log/daemons/errors.log file path

* Sat Jan 31 2009 Guillaume Rousse <guillomovitch@mandriva.org> 3.0.1-2mdv2009.1
+ Revision: 335896
- add admin guide
- make default configuration compatible with new version
- fix pid directory location

  + Michael Scherer <misc@mandriva.org>
    - fix missing option in configure, so the pidfile is correctly created, as spotted again by rapsys
    - adapt the config to new syslog ( as proposed by raphale gertz ), now syslog is a reserved word, among others

* Tue Jan 20 2009 Guillaume Rousse <guillomovitch@mandriva.org> 3.0.1-1mdv2009.1
+ Revision: 331909
- new version

* Sun Jan 04 2009 Jérôme Soyer <saispo@mandriva.org> 2.0.10-1mdv2009.1
+ Revision: 324260
- New upstream release

* Fri Aug 08 2008 Thierry Vignaud <tv@mandriva.org> 2.0.9-2mdv2009.0
+ Revision: 269400
- rebuild early 2009.0 package (before pixel changes)

* Sun May 18 2008 Funda Wang <fwang@mandriva.org> 2.0.9-1mdv2009.0
+ Revision: 208579
- New version 2.0.9

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

* Tue Dec 18 2007 Jérôme Soyer <saispo@mandriva.org> 2.0.6-1mdv2008.1
+ Revision: 132087
- New release 2.0.6

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Tue Oct 23 2007 Jérôme Soyer <saispo@mandriva.org> 2.0.5-1mdv2008.1
+ Revision: 101437
- New release 2.0.5

* Thu Aug 30 2007 Guillaume Rousse <guillomovitch@mandriva.org> 2.0.4-4mdv2008.0
+ Revision: 75199
- add a sysconfig file

* Thu Aug 30 2007 Guillaume Rousse <guillomovitch@mandriva.org> 2.0.4-3mdv2008.0
+ Revision: 75191
- rewrite init script
- sanitize reference documentation
- provides syslog-dameon

* Thu Jul 19 2007 Guillaume Rousse <guillomovitch@mandriva.org> 2.0.4-2mdv2008.0
+ Revision: 53700
- sync default configuration file with sysklogd one, and set maximum connection number (fix #30790 and #31817)

* Fri Jun 29 2007 Guillaume Rousse <guillomovitch@mandriva.org> 2.0.4-1mdv2008.0
+ Revision: 45712
- new version

