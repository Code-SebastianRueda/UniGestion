"""
Esquemas Pydantic para validación de datos de entrada.

Define los modelos de datos que se usan para validar y serializar
la información que llega desde las APIs de FastAPI.
"""

from pydantic import BaseModel

class CandidateCreate(BaseModel):
    """
    Esquema para crear un nuevo candidato.

    Usado en el endpoint POST /candidates para validar los datos
    de registro de candidatos.
    """
    name: str  # Nombre completo del candidato
    email: str  # Email de contacto
    phone: str  # Número de teléfono