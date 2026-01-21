# reteach.py

from llm import llm

def feynman_reteach(topic, wrong_areas):
    prompt = f"""
Explain ONLY this topic using the Feynman Technique:
>>> {topic} <<<

Student failed in:
{wrong_areas}

Rules:
- Simple language
- Analogies
- NO content outside {topic}
"""

    return llm.invoke(prompt).content
