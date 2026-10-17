"""Build with locked tools and canonicalize source-archive metadata offline."""
from __future__ import annotations

import argparse
import gzip
import io
import os
from pathlib import Path
import subprocess
import sys
import tarfile


def normalize_sdist(path: Path, epoch: int) -> None:
    """Normalize a generated sdist without extracting archive paths."""
    buffer = io.BytesIO()
    with tarfile.open(path, 'r:gz') as source, tarfile.open(fileobj=buffer, mode='w', format=tarfile.PAX_FORMAT) as target:
        for member in sorted(source.getmembers(), key=lambda item: item.name):
            if member.name.startswith('/') or '..' in Path(member.name).parts:
                raise ValueError('Unsafe source archive path')
            if not (member.isfile() or member.isdir()):
                raise ValueError('Unexpected source archive member type')
            member.mtime = epoch
            member.uid = member.gid = 0
            member.uname = member.gname = ''
            member.mode = 0o755 if member.isdir() else 0o644
            member.pax_headers = {}
            target.addfile(member, source.extractfile(member) if member.isfile() else None)
    with path.open('wb') as stream, gzip.GzipFile(filename='', fileobj=stream, mode='wb', mtime=epoch, compresslevel=9) as compressed:
        compressed.write(buffer.getvalue())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--outdir', type=Path, default=Path('dist'))
    args = parser.parse_args()
    epoch = int(os.environ.get('SOURCE_DATE_EPOCH', '1729123200'))
    environment = dict(os.environ, SOURCE_DATE_EPOCH=str(epoch))
    subprocess.run([sys.executable, '-m', 'build', '--no-isolation', '--outdir', str(args.outdir)],
                   check=True, env=environment)
    for path in args.outdir.glob('verbatim_md-*.tar.gz'):
        normalize_sdist(path, epoch)


if __name__ == '__main__':
    main()
