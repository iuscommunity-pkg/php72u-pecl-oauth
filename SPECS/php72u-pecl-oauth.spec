# IUS spec file for php72u-pecl-oauth, forked from Fedora:
# we don't want -z defs linker flag
%undefine _strict_symbol_defs_build

%global pecl_name oauth
%global ini_name  40-%{pecl_name}.ini
%global php       php72u

%bcond_without zts

Name:           %{php}-pecl-%{pecl_name}
Version:	2.0.2
Release:	1.ius%{?dist}
Summary:	PHP OAuth consumer extension
Group:		Development/Languages
License:	BSD
URL:		https://pecl.php.net/package/oauth
Source0:	https://pecl.php.net/get/%{pecl_name}-%{version}.tgz

BuildRequires:  %{php}-devel
BuildRequires:  libcurl-devel
BuildRequires:  pcre-devel

BuildRequires:  pear1u
# explicitly require pear dependencies to avoid conflicts
BuildRequires:  %{php}-cli
BuildRequires:  %{php}-common
BuildRequires:  %{php}-process
BuildRequires:  %{php}-xml

Requires:       php(zend-abi) = %{php_zend_api}
Requires:       php(api) = %{php_core_api}

# provide the stock name
Provides:       php-pecl-%{pecl_name} = %{version}
Provides:       php-pecl-%{pecl_name}%{?_isa} = %{version}

# provide the stock and IUS names without pecl
Provides:       php-%{pecl_name} = %{version}
Provides:       php-%{pecl_name}%{?_isa} = %{version}
Provides:       %{php}-%{pecl_name} = %{version}
Provides:       %{php}-%{pecl_name}%{?_isa} = %{version}

# provide the stock and IUS names in pecl() format
Provides:       php-pecl(%{pecl_name}) = %{version}
Provides:       php-pecl(%{pecl_name})%{?_isa} = %{version}
Provides:       %{php}-pecl(%{pecl_name}) = %{version}
Provides:       %{php}-pecl(%{pecl_name})%{?_isa} = %{version}

# conflict with the stock name
Conflicts:      php-pecl-%{pecl_name} < %{version}


%description
OAuth is an authorization protocol built on top of HTTP which allows
applications to securely access data without having to store
user names and passwords.


%prep
%setup -q -c
mv %{pecl_name}-%{version} NTS

# Don't install/register tests
sed -e 's/role="test"/role="src"/' \
    -e '/LICENSE/s/role="doc"/role="src"/' \
    -i package.xml


cat >%{ini_name} << 'EOF'
; Enable %{pecl_name} extension module
extension=%{pecl_name}.so
EOF

%if %{with zts}
# duplicate for ZTS build
cp -pr NTS ZTS
%endif


%build
pushd NTS
%{_bindir}/phpize
%configure --with-php-config=%{_bindir}/php-config
make %{?_smp_mflags}
popd

%if %{with_zts}
pushd ZTS
%{_bindir}/zts-phpize
%configure --with-php-config=%{_bindir}/zts-php-config
make %{?_smp_mflags}
popd
%endif


%install
make install -C NTS INSTALL_ROOT=%{buildroot}

# Drop in the bit of configuration
install -D -m 644 %{ini_name} %{buildroot}%{php_inidir}/%{ini_name}

# Install XML package description
install -D -m 644 package.xml %{buildroot}%{pecl_xmldir}/%{pecl_name}.xml

%if %{with zts}
make install -C ZTS INSTALL_ROOT=%{buildroot}
install -D -m 644 %{ini_name} %{buildroot}%{php_ztsinidir}/%{ini_name}
%endif

# Test & Documentation
for i in $(grep 'role="doc"' package.xml | sed -e 's/^.*name="//;s/".*$//')
do install -D -p -m 644 NTS/$i %{buildroot}%{pecl_docdir}/%{pecl_name}/$i
done


%check
: Minimal load test for NTS extension
%{__php} -n \
    -d extension=%{buildroot}%{php_extdir}/%{pecl_name}.so \
    --modules | grep OAuth

%if %{with zts}
: Minimal load test for ZTS extension
%{__ztsphp} -n \
    -d extension=%{buildroot}%{php_ztsextdir}/%{pecl_name}.so \
    --modules | grep OAuth
%endif


%triggerin -- pear1u
if [ -x %{__pecl} ]; then
    %{pecl_install} %{pecl_xmldir}/%{pecl_name}.xml >/dev/null || :
fi


%posttrans
if [ -x %{__pecl} ]; then
    %{pecl_install} %{pecl_xmldir}/%{pecl_name}.xml >/dev/null || :
fi


%postun
if [ $1 -eq 0 -a -x %{__pecl} ]; then
    %{pecl_uninstall} %{pecl_name} >/dev/null || :
fi

%files
%license NTS/LICENSE
%doc %{pecl_docdir}/%{pecl_name}
%{pecl_xmldir}/%{pecl_name}.xml

%config(noreplace) %{_sysconfdir}/php.d/%{ini_name}
%{php_extdir}/%{pecl_name}.so

%if %{with_zts}
%config(noreplace) %{php_ztsinidir}/%{ini_name}
%{php_ztsextdir}/%{pecl_name}.so
%endif


%changelog
* Thu Feb 08 2018 Ben Harper <ben.harper@rackspace.com> - 2.0.2-1.ius
- port from Fedora

* Mon Jan 29 2018 Remi Collet <remi@remirepo.net> - 2.0.2-7
- undefine _strict_symbol_defs_build

* Tue Oct 03 2017 Remi Collet <remi@fedoraproject.org> - 2.0.2-6
- rebuild for https://fedoraproject.org/wiki/Changes/php72

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.2-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Mon Nov 14 2016 Remi Collet <remi@fedoraproject.org> - 2.0.2-2
- rebuild for https://fedoraproject.org/wiki/Changes/php71

* Mon Jun 27 2016 Remi Collet <rcollet@redhat.com> - 2.0.2-1
- update to 2.0.2
- fix license installation

* Thu Feb 25 2016 Remi Collet <remi@fedoraproject.org> - 1.2.3-11
- drop scriptlets (replaced by file triggers in php-pear) #1310546

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.3-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.3-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon Sep  8 2014 Remi Collet <rcollet@redhat.com> - 1.2.3-8
- cleanup and modernize the spec
- build ZTS extension (fedora)
- install doc in pecl_docdir

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.3-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Thu Jun 19 2014 Remi Collet <rcollet@redhat.com> - 1.2.3-6
- rebuild for https://fedoraproject.org/wiki/Changes/Php56
- add numerical prefix to extension configuration file

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.3-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.3-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Fri Mar 22 2013 Remi Collet <rcollet@redhat.com> - 1.2.3-3
- rebuild for http://fedoraproject.org/wiki/Features/Php55

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Tue Oct 02 2012 F. Kooman <fkooman@tuxed.net> - 1.2.3-1
- update to 1.2.3, bugfix, see 
  http://pecl.php.net/package-changelog.php?package=oauth&release=1.2.3

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu Jan 19 2012 Remi Collet <remi@fedoraproject.org> - 1.2.2-3
- build against php 5.4
- fix filters

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Sun Jul 24 2011 F. Kooman <fkooman@tuxed.net> - 1.2.2-1
- Update to 1.2.2 (really fix RHBZ #724872 this time)

* Fri Jul 22 2011 F. Kooman <fkooman@tuxed.net> - 1.2.1-1
- update to 1.2.1 (RHBZ #724872). See
  http://pecl.php.net/package-changelog.php?package=oauth&release=1.2.1

* Sun Jul 03 2011 F. Kooman <fkooman@tuxed.net> - 1.2-1
- upgrade to 1.2

* Sun Jun 19 2011 F. Kooman <fkooman@tuxed.net> - 1.1.0-6
- add fix for http://pecl.php.net/bugs/bug.php?id=22337

* Mon Jun 13 2011 F. Kooman <fkooman@tuxed.net> - 1.1.0-5
- remove php_apiver marco, was not used

* Mon Jun 13 2011 F. Kooman <fkooman@tuxed.net> - 1.1.0-4
- add minimal check to see if module loads
- fix private-shared-object-provides rpmlint warning

* Sat Jun 11 2011 F. Kooman - 1.1.0-3
- BR pcre-devel

* Sat May 28 2011 F. Kooman - 1.1.0-2
- require libcurl for cURL request engine support 

* Sat May 28 2011 F. Kooman - 1.1.0-1
- initial package 
