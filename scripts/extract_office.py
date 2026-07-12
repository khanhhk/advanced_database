from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = Path('/tmp/advanced_database_office_text')
OUT.mkdir(exist_ok=True)

def texts(data):
    result = []
    for el in ET.fromstring(data).iter():
        tag = el.tag.rsplit('}', 1)[-1]
        if tag == 't' and el.text:
            result.append(el.text)
        elif tag == 'tab':
            result.append('\t')
        elif tag == 'br':
            result.append('\n')
    return ' '.join(result).replace(' \n ', '\n').replace(' \t ', '\t')

for path in sorted((ROOT / 'docs' / 'sources').glob('*.pptx')):
    with ZipFile(path) as archive:
        slides = [n for n in archive.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml', n)]
        slides.sort(key=lambda n: int(re.search(r'\d+', Path(n).stem).group()))
        notes = {int(re.search(r'\d+', Path(n).stem).group()): n for n in archive.namelist()
                 if re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml', n)}
        chunks = []
        for number, name in enumerate(slides, 1):
            chunks.append(f'\n===== SLIDE {number} =====\n{texts(archive.read(name))}')
            if number in notes:
                note = texts(archive.read(notes[number])).strip()
                if note:
                    chunks.append(f'\n[NOTES]\n{note}')
        (OUT / f'{path.name}.txt').write_text('\n'.join(chunks), encoding='utf-8')

for path in sorted((ROOT / 'docs' / 'sources').glob('*.docx')):
    with ZipFile(path) as archive:
        names = ['word/document.xml'] + sorted(n for n in archive.namelist()
                                                     if n.startswith(('word/header', 'word/footer')))
        chunks = [f'\n===== {name} =====\n{texts(archive.read(name))}'
                  for name in names if name in archive.namelist()]
        (OUT / f'{path.name}.txt').write_text('\n'.join(chunks), encoding='utf-8')

for path in sorted([ROOT / 'README.md', *ROOT.glob('docs/*.md')]):
    name = path.relative_to(ROOT).as_posix().replace('/', '__')
    (OUT / f'{name}.txt').write_text(path.read_text(encoding='utf-8'), encoding='utf-8')

for path in sorted(OUT.glob('*.txt')):
    print(f'{path.name}\t{path.stat().st_size}\t{len(path.read_text(encoding="utf-8").splitlines())} lines')
