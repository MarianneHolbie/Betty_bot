from gradio_client import Client
import sys
import json

client = Client("KingNish/OpenGPT-4o")

def get_open_gpt_4o_response(prompt):
    result = client.predict(
        user_prompt={"text": prompt, "files": []},
        model_selector="idefics2-8b-chatty",
        decoding_strategy="Top P Sampling",
        temperature=0.5,
        max_new_tokens=4096,
        repetition_penalty=1,
        top_p=0.9,
        web_search=True,
        api_name="/chat"
    )
    return result

if __name__ == "__main__":
    prompt = sys.argv[1]
    response = get_open_gpt_4o_response(prompt)
    print(json.dumps(response))
