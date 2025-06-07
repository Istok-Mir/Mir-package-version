from __future__ import annotations
from Mir import LanguageServer, ActivityIndicator, PackageStorage, unzip
import sublime


GITHUB_ASSET_VERSION = 'v0.0.7'
server_storage = PackageStorage(__package__, tag='0.0.1')


class PackageVersionServer(LanguageServer):
    name='package-version-server'
    activation_events={
        'selector': 'source.json',
        # 'on_uri': ['file://**/package.json'],
    }

    async def activate(self):
        server_path = server_storage / "package-version-server" / 'package-version-server'
        if not server_path.exists():
            await self.install()

        await self.connect('stdio', {
            'cmd': [server_path]
        })

    async def install(self):
        with ActivityIndicator(sublime.active_window(), f'Installing {PackageVersionServer.name}'):
            fetch_url, archive_filename = self._archive_on_github()
            save_to = server_storage / archive_filename
            await server_storage.download(fetch_url, save_to)
            unzip(save_to, new_name='package-version-server')

    def _archive_on_github(self) -> tuple[str, str]:
        platform = sublime.platform()
        arch = sublime.arch()
        if platform == 'windows':
            platform_code = 'pc-windows-msvc.zip'
        elif platform == 'linux':
            platform_code = 'unknown-linux-gnu.tar.gz'
        elif platform == 'osx':
            platform_code = 'apple-darwin.tar.gz'
        else:
            raise Exception('{} {} is not supported'.format(arch, platform))
        if arch == 'x32':
            arch_code = 'x86_64'
        elif arch == 'x64':
            arch_code = 'x86_64'
        elif arch == 'arm64':
            arch_code = 'aarch64'
        else:
            raise Exception('Unsupported architecture: {}'.format(arch))
        archive_filename = 'package-version-server-{}-{}'.format(arch_code, platform_code) # Using 'deno-' prefix

        fetch_url = f'https://github.com/zed-industries/package-version-server/releases/download/{GITHUB_ASSET_VERSION}/{archive_filename}'
        return fetch_url, archive_filename
