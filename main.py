from __future__ import annotations
from Mir import LanguageServer, LoaderInStatusBar, PackageStorage, unzip
import sublime


GITHUB_ASSET_VERSION = 'v0.0.7'
server_storage = PackageStorage(tag='0.0.1')
server_path = server_storage / "package-version-server" / 'package-version-server'

async def package_storage_setup():
    if server_path.exists():
        return
    await install()


class PackageVersionServer(LanguageServer):
    name='package-version-server'
    activation_events={
        'selector': 'source.json',
        # 'on_uri': ['file://**/package.json'],
    }

    async def activate(self):
        # setup runtime and install dependencies
        await package_storage_setup()

        await self.connect('stdio', {
            'cmd': [server_path]
        })


async def install():
    with LoaderInStatusBar(f'Installing {PackageVersionServer.name}'):
        fetch_url, archive_filename = archive_on_github()
        save_to = server_storage / archive_filename
        await server_storage.download(fetch_url, save_to)
        unzip(save_to, new_name='package-version-server')


def _archive_on_github() -> tuple[str, str]:
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
