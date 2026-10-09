"""Baixa os modelos de voz do Editai (uma vez so; retoma se a internet cair)."""
from faster_whisper import WhisperModel

# "small": rapido, usado para decidir os cortes.
# "medium": preciso, usado nas legendas finais.
MODELOS = ["small", "medium"]

for nome in MODELOS:
    print(f"  baixando modelo '{nome}'...", flush=True)
    WhisperModel(nome, device="cpu", compute_type="int8")
print("  modelos prontos")
