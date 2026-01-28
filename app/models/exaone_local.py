import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

MODEL_ID = "LGAI-EXAONE/EXAONE-3.5-2.4B-Instruct"

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.float32,
    device_map="cpu",
    trust_remote_code=True
)

app = FastAPI()

# ==== OpenAI-compatible schemas ====

class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: Optional[str] = None
    messages: List[Message]
    temperature: float = 0.2
    max_tokens: int = 512

@app.post("/v1/chat/completions")
def chat_completions(req: ChatCompletionRequest):
    # ✅ Gunakan apply_chat_template biar format benar
    messages = [{"role": m.role, "content": m.content} for m in req.messages]
    
    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    print("\n" + "="*50)
    print("📥 PROMPT RECEIVED:")
    print(prompt)
    print("="*50 + "\n")

    inputs = tokenizer(prompt, return_tensors="pt")

    outputs = model.generate(
        **inputs,
        max_new_tokens=req.max_tokens,
        temperature=req.temperature,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id  # ✅ Tambahkan ini
    )

    full_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # ✅ Ekstrak jawaban dengan lebih akurat
    answer = full_text[len(prompt):].strip()

    print("🤖 ANSWER:")
    print(answer)
    print("="*50)

    prompt_tokens = inputs["input_ids"].shape[1]
    completion_tokens = outputs[0].shape[0] - prompt_tokens
    completion_response = {
        "id": "chatcmpl-exaone",
        "object": "chat.completion",
        "created": 1745623456,
        "model": "gpt-4o-mini",
        "system_fingerprint": "fp_abc123",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": answer
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens
        },
    }
    print(completion_response)
    return completion_response
