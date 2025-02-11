from ollama import Client
from parser import AI


class Ollama(AI):
    def ask(self, prompt: str) -> str:  # Override
        ai = self.conf['ai']
        messages = []
        if self.conf.get('role'):
            system_role = dict(role='system', content=self.conf['role'])
            messages.append(system_role)
        d = dict(role='user', content=prompt)
        messages.append(d)
        c = Client(host=ai['url'])
        r = c.chat(model=ai['model'], messages=messages)
        return r['message']['content'].rstrip()
