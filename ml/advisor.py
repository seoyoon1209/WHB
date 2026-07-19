# Generate a preparation guide from the prediction result using GPT (SFR-011)
from openai import AsyncOpenAI

from settings.Settings import get_settings

_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        settings = get_settings()
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is not set.")
        _client = AsyncOpenAI(api_key=settings.openai_api_key)
    return _client


async def generate_guide(
    name: str,
    headache_risk: str,
    stomachache_risk: str,
    factors: list[dict],
) -> str:
    settings = get_settings()
    client = _get_client()

    factor_text = ", ".join(f"{f['label']}({f['value']:+.2f})" for f in factors) or "no notable factors"

    prompt = (
        f"User name: {name}\n"
        f"Headache risk: {headache_risk}\n"
        f"Cramp risk: {stomachache_risk}\n"
        f"Contributing factors: {factor_text}\n\n"
        "Based on the info above, write a 2-3 sentence guide in English to help the user prepare for today, "
        "in a warm, friendly tone. Include at least one concrete lifestyle tip (hydration, sleep, stretching, "
        "etc.), and gently note this is reference advice rather than a diagnosis without repeating a stiff "
        "disclaimer."
    )

    response = await client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a warm AI coach for a women's health app. Always respond in English. "
                    "You do not provide medical diagnoses."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=300,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()
