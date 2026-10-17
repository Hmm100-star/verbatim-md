import gzip
import io
from pathlib import Path
import runpy
import tarfile


def test_source_archive_metadata_is_canonical(tmp_path):
    normalize = runpy.run_path(str(Path(__file__).resolve().parents[2] / 'scripts/reproducible_build.py'))['normalize_sdist']
    outputs = []
    for sequence in (('b.txt', 'a.txt'), ('a.txt', 'b.txt')):
        path = tmp_path / (sequence[0] + '.tar.gz')
        with tarfile.open(path, 'w:gz') as archive:
            for number, name in enumerate(sequence):
                entry = tarfile.TarInfo('package/' + name)
                payload = name.encode()
                entry.size = len(payload)
                entry.mtime = 1000 + number
                entry.uid = 44
                entry.uname = 'private-local-username'
                archive.addfile(entry, io.BytesIO(payload))
        normalize(path, 1729123200)
        outputs.append(path.read_bytes())
        with tarfile.open(fileobj=io.BytesIO(gzip.decompress(outputs[-1])), mode='r:') as archive:
            assert all(member.uid == 0 and member.uname == '' for member in archive)
    assert outputs[0] == outputs[1]
