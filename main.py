from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os

app = FastAPI()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")  # chave segura no Render
)

class NutritionData(BaseModel):
    calories_consumed: int
    calories_target: int
    protein_grams: int
    protein_target: int
    carbs_grams: int
    carbs_target: int
    fat_grams: int
    fat_target: int

@app.post("/coach")
async def get_coach_advice(data: NutritionData):
    prompt = f"""
    Você é um nutricionista brasileiro prático. Analise esses dados da alimentação de hoje:

    📊 CONSUMIDO:
    - Calorias: {data.calories_consumed}/{data.calories_target} kcal ({(data.calories_consumed/data.calories_target*100):.0f}%)
    - Proteína: {data.protein_grams}/{data.protein_target}g ({(data.protein_grams/data.protein_target*100):.0f}%)
    - Carboidrato: {data.carbs_grams}/{data.carbs_target}g ({(data.carbs_grams/data.carbs_target*100):.0f}%)
    - Gordura: {data.fat_grams}/{data.fat_target}g ({(data.fat_grams/data.fat_target*100):.0f}%)

    ⚠️ DÊ 3 SUGESTÕES CONCRETAS:
    1. O que faltou/ajustar (quantidade + alimento específico)
    2. Alimentos brasileiros acessíveis (frango, feijão, arroz, ovo, etc)
    3. Quantidade em gramas e kcal aproximado

    📝 Responda em 100-150 palavras, direto ao ponto, como coach pessoal.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # barato e rápido (~$0.15/1M tokens)
            messages=[
                {"role": "system", "content": "Você é um nutricionista brasileiro prático."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7
        )

        advice = response.choices[0].message.content.strip()
        return {"advice": advice}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na IA: {str(e)}")

@app.get("/")
def root():
    return {"status": "Coach API rodando!"}
