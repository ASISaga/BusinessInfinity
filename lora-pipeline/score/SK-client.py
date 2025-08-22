import os
import json
import aiohttp
import semantic_kernel as sk
from semantic_kernel.skill_definition import sk_function

AML_ENDPOINT = os.getenv("AML_ENDPOINT")
AML_KEY = os.getenv("AML_KEY")

class AlignmentSkill:
    @sk_function(
        description="Get alignment score from AML‑hosted Llama‑3.1‑8B‑Instruct",
        name="get_alignment_score"
    )
    async def get_alignment_score(self, vision: str, decision: str) -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {AML_KEY}"
        }
        payload = {"vision": vision, "decision": decision}

        async with aiohttp.ClientSession() as session:
            async with session.post(AML_ENDPOINT, headers=headers, data=json.dumps(payload)) as resp:
                result = await resp.json()
                return json.dumps(result)

# Kernel setup
kernel = sk.Kernel()
kernel.import_skill(AlignmentSkill(), skill_name="alignment")