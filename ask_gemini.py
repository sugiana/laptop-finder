import os
from hashlib import md5
from time import sleep
import requests
import pandas as pd
from parser import (
    AI,
    HttpErr,
    )


class ResourceExhaustedErr(HttpErr):
    pass


def md5sum_file(filename: str):
    if not os.path.exists(filename):
        return
    hash_md5 = md5()
    with open(filename, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


class Gemini(AI):
    def ask(self, prompt: str) -> str:  # Override
        d = dict(contents=[dict(parts=[dict(text=prompt)])])
        r = requests.post(self.conf['ai']['url'], json=d)
        if r.status_code == 200:
            d = r.json()
            s = d['candidates'][0]['content']['parts'][0]['text']
            return s.rstrip()
        if r.status_code == 429:
            raise ResourceExhaustedErr(r)
        raise HttpErr(r)

    def parse(self):  # Override
        conf = self.conf['ai']
        step = 10
        wait_seconds = 20
        if os.path.exists(self.output_file):
            df = pd.read_csv(self.output_file)
            count = len(df)
            limit = count // step * step + step
        else:
            limit = step
        is_error = False
        while True:
            old_md5 = md5sum_file(self.output_file)
            try:
                super().parse()
                is_error = False
                wait_seconds = 20
            except ResourceExhaustedErr as e:
                print('*' * 20)
                print('* Quota error')
                if wait_seconds > 60:
                    raise e
                wait_seconds += 10
                is_error = True
            except HttpErr as e:
                if is_error:
                    raise e
                is_error = True
            if is_error:
                print(f'Tunggu {wait_seconds} detik ...')
                sleep(wait_seconds)
                continue
            new_md5 = md5sum_file(self.output_file)
            if old_md5 == new_md5:
                if new_md5:
                    print('Selesai.')
                    break
                continue
            limit += step
