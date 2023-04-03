import os
import openai

#os.getenvを入れない
openai.api_key = "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" 

response = openai.Completion.create(
  engine="davinci",
  prompt="I'm happy.", #どの文章から始めるか
  temperature=0.7,
  max_tokens=64,
  top_p=1,
  frequency_penalty=0,
  presence_penalty=0
)
print(response)