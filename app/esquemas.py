"""Esquemas del contrato contrato/openapi.yaml."""

from datetime import date, time
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from app.modelos import EstadoCivil, EstadoFuncionario

Texto50 = Annotated[str, Field(min_length=1, max_length=50)]
Texto100 = Annotated[str, Field(min_length=1, max_length=100)]
Telefono = Annotated[str, Field(min_length=6, max_length=20)]


class _CamposFuncionario(BaseModel):
    estado_civil: EstadoCivil | None = None
    direccion: str | None = Field(None, max_length=255)
    ciudad_id: int | None = None
    correo_electronico: EmailStr | None = None
    fecha_ingreso_seguro_social: date | None = None
    fecha_egreso: date | None = None
    numero_cuenta_bancaria: str | None = Field(None, max_length=50)
    tipo_contrato_id: int | None = None
    cargo_id: int | None = None
    fecha_asuncion_cargo: date | None = None
    horario_ingreso: time | None = None
    horario_salida: time | None = None
    dias_laborales: str | None = Field(None, max_length=100)
    contacto_emergencia: str | None = Field(None, max_length=100)


class FuncionarioPost(_CamposFuncionario):
    numero_documento: Texto50
    pais_documento_id: int
    pais_origen_id: int
    fecha_ingreso: date
    estado: EstadoFuncionario
    telefono: Telefono

    @model_validator(mode="after")
    def _fechas(self):
        if self.fecha_egreso and self.fecha_egreso < self.fecha_ingreso:
            raise ValueError("fecha_egreso no puede ser anterior a fecha_ingreso")
        return self


class FuncionarioPatch(_CamposFuncionario):
    numero_documento: Texto50 | None = None
    pais_documento_id: int | None = None
    pais_origen_id: int | None = None
    fecha_ingreso: date | None = None
    estado: EstadoFuncionario | None = None
    telefono: Telefono | None = None


class Funcionario(_CamposFuncionario):
    model_config = ConfigDict(from_attributes=True)
    id: int
    numero_documento: str
    pais_documento_id: int
    pais_origen_id: int
    fecha_ingreso: date
    estado: EstadoFuncionario
    telefono: str
    correo_electronico: str | None = None


class HijoPost(BaseModel):
    funcionario_id: int
    nombre: Texto100
    fecha_nacimiento: date
    documento: Texto50 | None = None
    apto_bonificacion: bool | None = None


class HijoPatch(BaseModel):
    funcionario_id: int | None = None
    nombre: Texto100 | None = None
    fecha_nacimiento: date | None = None
    documento: Texto50 | None = None
    apto_bonificacion: bool | None = None


class Hijo(HijoPost):
    model_config = ConfigDict(from_attributes=True)
    id: int
