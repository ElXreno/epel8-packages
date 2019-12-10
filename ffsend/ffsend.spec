Name:           ffsend
Version:        0.2.57
Release:        2%{?dist}
Summary:        Easily and securely share files from the command line

License:        GPLv3
URL:            https://github.com/timvisee/ffsend
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

ExclusiveArch:  %{rust_arches}

BuildRequires:  rust-packaging

%description
Easily and securely share files from the command line. A fully featured Firefox
Send client.


%prep
%autosetup
curl https://sh.rustup.rs -sSf | sh -s -- --default-toolchain stable --profile minimal -y


%build
$HOME/.cargo/bin/cargo build --release --locked


%install
install -m 0755 -Dp target/release/ffsend %{buildroot}%{_bindir}/ffsend

for t in ffput ffget ffdel; do
  ln -s ffsend %{buildroot}%{_bindir}/$t
done

%{buildroot}%{_bindir}/ffsend generate completions bash fish zsh
install -Dpm0644 -t %{buildroot}%{_datadir}/bash-completion/completions \
  ffsend.bash
install -Dpm0644 -t %{buildroot}%{_datadir}/fish/vendor_completions.d \
  ffsend.fish
install -Dpm0644 -t %{buildroot}%{_datadir}/zsh/site-functions \
  _ffsend


%files
%license LICENSE
%doc README.md
%{_bindir}/ffsend
%{_bindir}/ffput
%{_bindir}/ffget
%{_bindir}/ffdel
%dir %{_datadir}/bash-completion
%dir %{_datadir}/bash-completion/completions
%{_datadir}/bash-completion/completions/ffsend.bash
%dir %{_datadir}/fish
%dir %{_datadir}/fish/vendor_completions.d
%{_datadir}/fish/vendor_completions.d/ffsend.fish
%dir %{_datadir}/zsh
%dir %{_datadir}/zsh/site-functions
%{_datadir}/zsh/site-functions/_ffsend


%changelog
* Tue Dec 10 2019 ElXreno <elxreno@gmail.com> - 0.2.57-2
- Rewrited spec file for CentOS 8 (stealed from here: https://src.fedoraproject.org/rpms/rust-ffsend)
