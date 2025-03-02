import requests
from parser import (
    AI,
    HttpErr,
    )


class Ollama(AI):
    def ask(self, prompt: str) -> str:  # Override
        ai = self.conf['ai']
        messages = []
        if self.conf.get('role'):
            system_role = dict(role='system', content=self.conf['role'])
            messages.append(system_role)
        d = dict(role='user', content=prompt)
        messages.append(d)
        options = dict(temperature=0)
        data = dict(
                model=ai['model'],
                messages=messages,
                options=options,
                stream=False)
        r = requests.post(ai['url'], json=data)
        if r.status_code == 200:
            d = r.json()
            return d['message']['content'].rstrip()
        raise HttpErr(r)
