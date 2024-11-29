from pydantic import BaseModel, field_validator, ValidationError

class Estado(BaseModel):
    estado: str
    capital: str
    regiao: str
    populacao: int

    @field_validator('populacao')
    def check_population(cls, value):
        if value <= 0:
            raise ValidationError("A população deve ser maior que zero.")
        return value