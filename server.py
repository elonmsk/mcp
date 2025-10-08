import requests
from fastapi import FastAPI

app = FastAPI()

@app.post("/get_variants_for_gene")
def get_variants_for_gene(gene: list[str]):
    response = requests.post(
        "https://discovery.indra.bio/api/get_variants_for_gene",
        json={"gene": gene},
        headers={"accept": "application/json"}
    )
    return response.json()
