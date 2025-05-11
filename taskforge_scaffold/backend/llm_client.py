import os
import openai
import utils

def extract_actions(text: str) -> list:
    prompt = utils.load_prompt_template()
    resp = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role":"system","content":prompt}, {"role":"user","content":text}],
        temperature=0.0,
    )
    return utils.parse_json(resp.choices[0].message.content)
