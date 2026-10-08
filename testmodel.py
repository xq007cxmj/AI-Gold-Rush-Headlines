from openai import OpenAI

client = OpenAI(
    # api_key=os.environ[
    #     "sk-3991ee42d3afd3ec14d2ff936f346e800cae611311a97bf4cbac7ccd9fe849ba"
    # ],
    api_key="sk-3991ee42d3afd3ec14d2ff936f346e800cae611311a97bf4cbac7ccd9fe849ba",
    base_url="https://discovery-api.intern-ai.org.cn/v1",
)

response = client.chat.completions.create(
    model="kimi-k2.6",
    messages=[{"role": "user", "content": "你好，请用一句话介绍你自己。"}],
    stream=False,
)

print(response.choices[0].message.content)
