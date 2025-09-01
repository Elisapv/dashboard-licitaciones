import requests

url = "https://kaiken.up.railway.app/webhook/applicant"

data = {
    "rut": "204443270",
    "nombre": "Elisa",
    "apellido": "Peña",
    "url": "https://dashboard-licitaciones-gjcdfphhzb2aimxapumfjz.streamlit.app/",
    "repo": "https://github.com/Elisapv/dashboard-licitaciones.git",
    "comentario": "Soy desarrollador fullstack y completé el desafío implementando un mini sistema de licitaciones con Streamlit y Supabase."
}

response = requests.post(url, json=data)

print(response.status_code)
print(response.text)
