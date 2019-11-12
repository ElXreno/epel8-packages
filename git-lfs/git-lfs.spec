# Generate devel rpm
%global with_devel 0
# Build project from bundled dependencies
%global with_bundled %{defined rhel}
# Build with debug info rpm
%global with_debug 1
# Run tests in check section
%global with_check %{undefined rhel}
# Generate unit-test rpm
%global with_unit_test 0
# Build man pages
%global with_manpages %{undefined rhel}

%if 0%{?with_debug}
%global _dwz_low_mem_die_limit 0
%else
%global debug_package   %{nil}
%endif

%if %{undefined gobuild}
%define gobuild(o:) go build -ldflags "${LDFLAGS:-} -B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \\n')" -a -v -x %{?**};
%endif

%global provider        github
%global provider_tld    com
%global project         git-lfs
%global repo            git-lfs
# https://github.com/git-lfs/git-lfs
%global provider_prefix %{provider}.%{provider_tld}/%{project}/%{repo}
%global import_path     %{provider_prefix}
%global commit          6f4b2e98e038530a3e26d26726799832290c61c4
%global shortcommit     %(c=%{commit}; echo ${c:0:7})

Name:           git-lfs
Version:        2.4.2
Release:        2%{?dist}
Summary:        Git extension for versioning large files

License:        MIT
URL:            https://git-lfs.github.io/
Source0:        https://%{provider_prefix}/archive/v%{version}/%{name}-%{version}.tar.gz

ExclusiveArch:  %{?go_arches:%{go_arches}}%{!?go_arches:%{ix86} x86_64 %{arm} aarch64 ppc64le s390x}
BuildRequires:  %{?go_compiler:compiler(go-compiler)}%{!?go_compiler:golang}

%if 0%{?with_bundled}
Provides:       bundled(golang(github.com/git-lfs/go-netrc/netrc)) = e0e9ca483a183481412e6f5a700ff20a36177503
Provides:       bundled(golang(github.com/inconshreveable/mousetrap)) = 76626ae9c91c4f2a10f34cad8ce83ea42c93bb75
Provides:       bundled(golang(github.com/kr/pty)) = 5cf931ef8f76dccd0910001d74a58a7fca84a83d
Provides:       bundled(golang(github.com/olekukonko/ts)) = ecf753e7c962639ab5a1fb46f7da627d4c0a04b8
Provides:       bundled(golang(github.com/pkg/errors)) = c605e284fe17294bda444b34710735b29d1a9d90
Provides:       bundled(golang(github.com/rubyist/tracerx)) = 787959303086f44a8c361240dfac53d3e9d53ed2
Provides:       bundled(golang(github.com/spf13/cobra)) = c55cdf33856a08e4822738728b41783292812889
Provides:       bundled(golang(github.com/spf13/pflag)) = 580b9be06c33d8ba9dcc8757ea56b7642472c2f5
Provides:       bundled(golang(github.com/stretchr/testify)) = 6cb3b85ef5a0efef77caef88363ec4d4b5c0976d
Provides:       bundled(golang(github.com/ThomsonReutersEikon/go-ntlm/ntlm)) = b00ec39bbdd04f845950f4dbb4fd0a2c3155e830
Provides:       bundled(golang(github.com/xeipuuv/gojsonschema)) = 6b67b3fab74d992bd07f72550006ab2c6907c416
Provides:       bundled(golang(github.com/git-lfs/wildmatch)) = 8a0518641565a619e62a2738c7d4498fc345daf6
%else
BuildRequires:  golang(github.com/git-lfs/go-netrc/netrc)
BuildRequires:  golang(github.com/kr/pty)
BuildRequires:  golang(github.com/inconshreveable/mousetrap)
BuildRequires:  golang(github.com/olekukonko/ts)
BuildRequires:  golang(github.com/rubyist/tracerx)
BuildRequires:  golang(github.com/spf13/cobra)
BuildRequires:  golang(github.com/spf13/pflag)
BuildRequires:  golang(github.com/ThomsonReutersEikon/go-ntlm/ntlm)
BuildRequires:  golang(github.com/xeipuuv/gojsonpointer)
BuildRequires:  golang(github.com/xeipuuv/gojsonreference)
BuildRequires:  golang(github.com/xeipuuv/gojsonschema)
BuildRequires:  golang(github.com/pkg/errors)
BuildRequires:  golang(github.com/git-lfs/wildmatch)
%endif

%if 0%{?with_manpages}
# Generate mans
BuildRequires:  /usr/bin/ronn
%endif

%if 0%{?with_check}
# For tests
%if ! 0%{?with_bundled}
BuildRequires:  golang(github.com/stretchr/testify)
%endif
BuildRequires:  perl-Digest-SHA
# Tests require full git suite, but not generally needed.
BuildRequires:  git >= 1.8.2
%endif

# https://github.com/git-lfs/git-lfs/commit/263bfd784aa0bb23e942033605fce6c870fc8e4f
# 1.8.5 needed for macOS, but 1.8.2 sufficient for Linux.
Requires:       git-core >= 1.8.2

%description
Git Large File Storage (LFS) replaces large files such as audio samples,
videos, datasets, and graphics with text pointers inside Git, while
storing the file contents on a remote server.


%if 0%{?with_devel}
%package -n golang-%{provider}-%{project}-%{repo}-devel
Summary:       %{summary}
BuildArch:     noarch

%description -n golang-%{provider}-%{project}-%{repo}-devel
%{summary}

This package contains library source intended for
building other packages which use import path with
%{import_path} prefix.
%endif


%if 0%{?with_unit_test} && 0%{?with_devel}
%package -n golang-%{provider}-%{project}-%{repo}-unit-test-devel
Summary:         Unit tests for %{name} package

# test subpackage tests code from devel subpackage
Requires:        golang-%{provider}-%{project}-%{repo}-devel = %{version}-%{release}


%description -n golang-%{provider}-%{project}-%{repo}-unit-test-devel
%{summary}

This package contains unit tests for project
providing packages with %{import_path} prefix.
%endif


%prep
%autosetup -p1

%if ! 0%{?with_bundled}
rm -rf vendor
%endif


%build
mkdir -p src/%{provider}.%{provider_tld}/%{project}/
ln -s $(pwd) src/%{provider}.%{provider_tld}/%{project}/%{repo}
export GOPATH=$(pwd):%{gopath}

# Build manpages first (some embedding in the executable is done.)
pushd docs
%if 0%{?with_manpages}
ronn --roff man/*.ronn
%endif
%gobuild -o mangen man/mangen.go
./mangen
popd

%gobuild -o bin/git-lfs %{import_path}

%if 0%{?with_check}
# Build test executables
for go in test/cmd/*.go; do
    %gobuild -o "bin/$(basename $go .go)" "$go"
done
%gobuild -o "bin/git-lfs-test-server-api" test/git-lfs-test-server-api/*.go
%endif


%install
install -Dpm0755 bin/git-lfs %{buildroot}%{_bindir}/%{name}
%if 0%{?with_manpages}
install -d -p %{buildroot}%{_mandir}/man1/
install -Dpm0644 docs/man/*.1 %{buildroot}%{_mandir}/man1/
install -d -p %{buildroot}%{_mandir}/man5/
install -Dpm0644 docs/man/*.5 %{buildroot}%{_mandir}/man5/
%endif

# source codes for building projects
%if 0%{?with_devel}
install -d -p %{buildroot}%{gopath}/src/%{import_path}/
echo "%%dir %%{gopath}/src/%%{import_path}/." >> devel.file-list
# find all *.go but no *_test.go files and generate devel.file-list
for file in $(find . \( -iname "*.go" -or -iname "*.s" \) \! -iname "*_test.go") ; do
    dirprefix=$(dirname $file)
    install -d -p %{buildroot}%{gopath}/src/%{import_path}/$dirprefix
    cp -pav $file %{buildroot}%{gopath}/src/%{import_path}/$file
    echo "%%{gopath}/src/%%{import_path}/$file" >> devel.file-list

    while [ "$dirprefix" != "." ]; do
        echo "%%dir %%{gopath}/src/%%{import_path}/$dirprefix" >> devel.file-list
        dirprefix=$(dirname $dirprefix)
    done
done
%endif

# testing files for this project
%if 0%{?with_unit_test} && 0%{?with_devel}
install -d -p %{buildroot}%{gopath}/src/%{import_path}/
# find all *_test.go files and generate unit-test-devel.file-list
for file in $(find . -iname "*_test.go") ; do
    dirprefix=$(dirname $file)
    install -d -p %{buildroot}%{gopath}/src/%{import_path}/$dirprefix
    cp -pav $file %{buildroot}%{gopath}/src/%{import_path}/$file
    echo "%%{gopath}/src/%%{import_path}/$file" >> unit-test-devel.file-list

    while [ "$dirprefix" != "." ]; do
        echo "%%dir %%{gopath}/src/%%{import_path}/$dirprefix" >> devel.file-list
        dirprefix=$(dirname $dirprefix)
    done
done
%endif

%if 0%{?with_devel}
sort -u -o devel.file-list devel.file-list
%endif


%post
%{_bindir}/%{name} install --system &> /dev/null

%preun
if [ $1 -eq 0 ]; then
    %{_bindir}/%{name} uninstall --system &> /dev/null
fi
exit 0


%check
%if 0%{?with_check}
export GOPATH=%{buildroot}%{gopath}:$(pwd):%{gopath}
export GIT_LFS_TEST_MAXPROCS=$(getconf _NPROCESSORS_ONLN) SKIPCOMPILE=1
pushd src/%{provider}.%{provider_tld}/%{project}/%{name}
./script/cibuild
popd
%endif


%files
%license LICENSE.md
%{_bindir}/%{name}
%if 0%{?with_manpages}
%{_mandir}/man1/%{name}*.1*
%{_mandir}/man5/%{name}*.5*
%endif

%if 0%{?with_devel}
%files -n golang-%{provider}-%{project}-%{repo}-devel -f devel.file-list
%license LICENSE.md
%dir %{gopath}/src/%{provider}.%{provider_tld}/%{project}
%endif

%if 0%{?with_unit_test} && 0%{?with_devel}
%files -n golang-%{provider}-%{project}-%{repo}-unit-test-devel -f unit-test-devel.file-list
%license LICENSE.md
%endif


%changelog
* Wed Oct 17 2018 Carl George <carl@george.computer> - 2.4.2-2
- Redirect scriptlet output to /dev/null

* Wed Aug 29 2018 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.4.2-1
- Update to 2.4.2

* Tue Jul 31 2018 Florian Weimer <fweimer@redhat.com> - 2.4.1-3
- Rebuild with fixed binutils

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2.4.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Wed May 23 2018 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.4.1-1
- Update to latest release

* Mon May 21 2018 Carl George <carl@george.computer> - 2.4.0-3
- Fix %%preun to correctly remove the lfs filter on uninstall (rhbz#1580357)

* Mon Mar 12 2018 Carl George <carl@george.computer> - 2.4.0-2
- Add %%go_arches fallback to work around Koji issues

* Sun Mar 04 2018 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.4.0-1
- Update to latest release.

* Thu Feb 08 2018 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.3.4-6
- Add patches to build with Go 1.10.

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2.3.4-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Mon Dec 04 2017 Carl George <carl@george.computer> - 2.3.4-4
- Use vendored libraries on RHEL
- Skip test on RHEL
- Don't build man pages on RHEL due to missing ronn
- Don't build html versions of man pages

* Fri Dec 01 2017 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.3.4-3
- Require git-core instead of git.

* Fri Nov 03 2017 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.3.4-2
- Patch tests to work on slow systems like arm and aarch builders.
- Fix "git lfs help" command.

* Fri Nov 03 2017 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.3.4-1
- Update to latest release.
- Run all tests during build.

* Fri Sep 01 2017 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.2.1-3
- Remove redundant doc tag on manpages.
- Use path macros in %%post/%%postun.

* Thu Aug 31 2017 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.2.1-2
- Disable unnecessary subpackages.

* Sun Jul 30 2017 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.2.1-1
- Update to latest version.

* Wed Apr 19 2017 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.0.2-2
- Patch up to build with Go 1.7

* Wed Apr 19 2017 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.0.2-1
- Update to latest release
- Add some requested macros

* Tue Mar 14 2017 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.0.1-1
- Update to latest release
- Don't disable git-lfs globally during upgrade

* Mon Mar 06 2017 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.0.0-1
- Update to latest release

* Sun Feb 12 2017 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 1.5.5-1
- Update to latest release
- Add -devel and -unit-test-devel subpackages
- Add post/preun scriptlets for global enablement

* Sun May 15 2016 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 1.2.0-1
- Initial package
