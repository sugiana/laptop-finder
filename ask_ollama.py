from ollama import Client
from ollama._types import ResponseError
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
        c = Client(host=ai['url'])
        try:
            r = c.chat(
                    model=ai['model'], messages=messages, options=options)
        except ConnectionError as e:
            raise HttpErr(e)
        except ResponseError as e:
            raise HttpErr(e)
        message = r['message']['content'].rstrip()
        token_prompt = r["prompt_eval_count"]
        token_output = r["eval_count"]
        token = token_prompt + token_output
        return dict(message=message, token=token)
