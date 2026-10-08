from openai import OpenAI

client = OpenAI(
    # api_key=os.environ[
    #     "your-api-key"
    # ],
    api_key="",
    base_url="https://discovery-api.intern-ai.org.cn/v1",
)

response = client.chat.completions.create(
    model="kimi-k2.6",
    messages=[{"role": "user", "content": "你好，请用一句话介绍你自己。"}],
    stream=False,
)

print(response.choices[0].message.content)
