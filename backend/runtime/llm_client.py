from openai import OpenAI
import json

class LLMClient:
    def __init__(self):
        pass

    def call(self, memory: dict, prompt: str) -> dict:
        api_key = memory.get("api_key")
        if not api_key:
            return {
                "error": "NO_API_KEY",
                "content": "No API key provided. Please check settings.",
                "lights": [0, 0, 0, 0, 0, 0, 0],
            }

        try:
            # Initialize OpenAI client
            client = OpenAI(api_key=api_key)

            # Perform the LLM call
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": "You are the Paladin 7-layer runtime engine. Respond ONLY in JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,

                # ⭐ REQUIRED FOR TOKEN USAGE TO APPEAR
                max_tokens=500
            )

            # -------------------------------
            # ⭐ TOKEN TRACKING (Option A)
            # -------------------------------
            usage = getattr(response, "usage", None)
            if usage:
                prompt_tokens = getattr(usage, "prompt_tokens", 0)
                completion_tokens = getattr(usage, "completion_tokens", 0)
                total_tokens = getattr(usage, "total_tokens", 0)

                # Ensure token ledger exists
                mem = memory.setdefault("token_usage", {
                    "total_input": 0,
                    "total_output": 0,
                    "history": []
                })

                mem["total_input"] += prompt_tokens
                mem["total_output"] += completion_tokens
                mem["history"].append({
                    "prompt": prompt_tokens,
                    "completion": completion_tokens,
                    "total": total_tokens
                })

                memory["token_usage"] = mem
            # -------------------------------

            # Extract raw JSON text
            raw = response.choices[0].message.content

            # Parse JSON safely
            try:
                return json.loads(raw)
            except Exception as e:
                return {
                    "error": "BAD_JSON",
                    "content": f"LLM returned invalid JSON: {str(e)}",
                }

        except Exception as e:
            # Catch any connection or SDK errors
            return {
                "error": "LLM_CALL_FAILED",
                "content": f"Connection Error: {str(e)}",
            }
