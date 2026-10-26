"""Esquemas de la API (contrato en contrato/openapi.yaml, generado desde el código).

Cambios respecto al contrato original (aprobados con la revisión de contratos vs BD):
- Se agregan `nombres` y `apellidos`, que no estaban en ningún lado.
- El cargo actual vive en ms-desempeno (historial de cargos) y el horario en
  ms-asistencia: se quitan `cargo_id`, `fecha_asuncion_cargo`, `horario_ingreso`,
  `horario_salida` y `dias_laborales`.
- `numero_cuenta_bancaria` solo lo ven los roles de RRHH y nómina.
"""

from datetime import date
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
    contacto_emergencia: str | None = Field(None, max_length=100)


class FuncionarioPost(_CamposFuncionario):
    numero_documento: Texto50
    nombres: Texto100
    apellidos: Texto100
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
    nombres: Texto100 | None = None
    apellidos: Texto100 | None = None
    pais_documento_id: int | None = None
    pais_origen_id: int | None = None
    fecha_ingreso: date | None = None
    estado: EstadoFuncionario | None = None
    telefono: Telefono | None = None


class Funcionario(_CamposFuncionario):
    model_config = ConfigDict(from_attributes=True)
    id: int
    numero_documento: str
    nombres: str
    apellidos: str
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
