
# Imports
import base64
import hashlib
import magic
import os
import sys

run_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(run_path, ".."))


def get_file_type(data):
    valid_types = {'audio/mpeg': '.mp3', 'video/x-ms-asf': '.wmv',
                   'video/ogg':  '.ogg', 'audio/ogg':      '.ogg'}
    mimetype = magic.from_buffer(data, mime=True)
    print(mimetype)
    return valid_types.get(mimetype, '')


# Functions
def clean_path(path):
    for c in  "%:/,.\\[]<>*?":
        path = path.replace(c, '_')
    return path


def read_tja(path):
    with open(path, 'rb') as fh:
        raw = fh.read()
    return decode_tja(raw)


def decode_tja(raw):
    for enc in ['utf-8-sig', 'utf-8', 'utf-16', 'shift-jis', 'shift-jis_2004']:
        try:
            data = raw.decode(enc)
            assert 'TITLE:' in data
            return data
        except Exception as e:
            pass
    print("unknown encoding")
    print("Copy the below in cyberchef for bruteforcing:")
    print(base64.b64encode(raw[:300]))
    raise(Exception("Unknown Encoding"))


def encode_tja(text):
    return text.encode('utf-8-sig')


def write_tja(data, path):
    if isinstance(data, str):
        data = encode_tja(data)
    open(path, 'wb').write(data)


def set_tja_metadata(tja, title=None, sub=None, song=None):
    return_raw = False
    if isinstance(tja, bytes):
        tja = decode_tja(tja)
        return_raw = True

    new_tja = ''
    for line in tja.splitlines():
        if title and line.lower().startswith('title:'):
            line = line.split(':')[0] + ':' + title
        if sub   and line.lower().startswith('subtitle:'):
            line = line.split(':')[0] + ':' + sub
        if song  and line.lower().startswith('wave:'):
            line = line.split(':')[0] + ':' + song
        new_tja = new_tja + line + '\r\n'
    if return_raw:
        return encode_tja(new_tja)
    return new_tja


def parse_tja(tja):
    lval = lambda l:l.split(':')[1]
    return_raw = False
    if isinstance(tja, bytes):
        tja = decode_tja(tja)
        return_raw = True

    meta = {'title': None, 'sub': None, 'bpm': None, 'song': None, 'genre': None,
            'easy': None, 'normal': None, 'hard': None, 'oni': None, 'ura': None,
            'movie': None, 'image': None, 'maker': None, 'easy_charter': None,
            'normal_charter': None, 'hard_charter': None, 'oni_charter': None,
            'ura_charter': None, 'tower_charter': None, 'tower_lives': None}
    d_map = {'0': 'easy', '1': 'normal', '2': 'hard', '3': 'oni', '4': 'ura',
             '5': 'tower'}

    difficulty = None
    for line in tja.splitlines():
        lline = line.lower()
        if   lline.startswith('title:'):    meta['title']       = lval(line)
        elif lline.startswith('subtitle:'): meta['sub']         = lval(line)
        elif lline.startswith('bpm:'):      meta['bpm']         = float(lval(line))
        elif lline.startswith('wave:'):     meta['song']        = lval(line)
        elif lline.startswith('genre:'):    meta['genre']       = lval(line)
        elif lline.startswith('bgmovie:'):  meta['movie']       = lval(line)
        elif lline.startswith('bgimage:'):  meta['image']       = lval(line)
        elif lline.startswith('maker:'):    meta['maker']       = lval(line)
        elif lline.startswith('life:'):     meta['tower_lives'] = lval(line)
        elif lline.startswith('notesdesigner'):
            level, charter = line.split(':')
            meta[d_map[level[-1]]+'_charter'] = charter
        elif lline.startswith('course'):
            difficulty = lval(line)
            if difficulty in d_map.keys():
                difficulty = d_map[difficulty]
            if difficulty == 'edit':
                difficulty = 'ura'
        elif lline.startswith('level:'):
            meta[difficulty] = int(lval(line))
        if all(meta.values()):
            return meta
    return meta


def md5(tja):
    if isinstance(tja, str):
        tja = encode_tja(tja)
    return hashlib.md5(tja).hexdigest()


def prepare_orig_tja(tja, song, wave):
    wave = get_file_type(wave)
    print(wave)
    tja = set_tja_metadata(tja, title=song.title_orig, sub=song.subtitle_orig,
                           song=clean_path(song.title_orig)+wave)
    return tja


def prepare_en_tja(tja, song, wave):
    wave = get_file_type(wave)
    tja = set_tja_metadata(tja, title=song.title_en, sub=song.subtitle_en,
                           song=clean_path(song.title_en)+wave)
    return tja


def generate_md5s(tja, song, wave):
    wave = get_file_type(wave)
    # Orig TJA
    tja = prepare_orig_tja(tja, song, wave)
    md5_orig = md5(tja)
    # Eng TJA
    tja = prepare_en_tja(tja, song, wave)
    return md5_orig, md5(tja)
