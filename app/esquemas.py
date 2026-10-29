"""Esquemas de la API (contrato en contrato/openapi.yaml, generado desde el código).

Cambios respecto al contrato original (aprobados con la revisión de contratos vs BD):
- Se agregan `nombres` y `apellidos`, que no estaban en ningún lado.
- El cargo actual vive en ms-desempeno (historial de cargos) y el horario en
  ms-asistencia: se quitan `cargo_id`, `fecha_asuncion_cargo`, `horario_ingreso`,
  `horario_salida` y `dias_laborales`.
- `numero_cuenta_bancaria` y `entidad_bancaria_id` (de ms-organizacion) solo los ven
  los roles de RRHH y nómina. Si hay cuenta, hay que indicar la entidad.
- `telefono` en formato internacional: código de país y número, solo dígitos.
- Las fechas de ingreso y de ingreso a IPS no pueden ser posteriores a hoy, y la de
  IPS no puede ser anterior a la de ingreso.
"""

from datetime import date
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from app.fechas import errores_de_fechas
from app.modelos import EstadoCivil, EstadoFuncionario

Texto50 = Annotated[str, Field(min_length=1, max_length=50)]
Texto100 = Annotated[str, Field(min_length=1, max_length=100)]
Telefono = Annotated[
    str,
    Field(
        pattern=r"^[1-9][0-9]{7,14}$",
        description="Código de país seguido del número, solo dígitos (p. ej. 595981123456)",
        examples=["595981123456"],
    ),
]


# Campos que intervienen en las reglas que cruzan campos (ver rutas.actualizar).
CAMPOS_CON_REGLAS = (
    "fecha_ingreso",
    "fecha_ingreso_seguro_social",
    "fecha_egreso",
    "numero_cuenta_bancaria",
    "entidad_bancaria_id",
)


class _CamposFuncionario(BaseModel):
    estado_civil: EstadoCivil | None = None
    direccion: str | None = Field(None, max_length=255)
    ciudad_id: int | None = None
    correo_electronico: EmailStr | None = None
    fecha_ingreso_seguro_social: date | None = None
    fecha_egreso: date | None = None
    numero_cuenta_bancaria: str | None = Field(None, max_length=50)
    entidad_bancaria_id: int | None = None
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
    def _reglas(self):
        errores = errores_de_fechas(
            self.fecha_ingreso, self.fecha_ingreso_seguro_social, self.fecha_egreso
        )
        if errores:
            raise ValueError("; ".join(mensaje for _, mensaje in errores))
        if self.numero_cuenta_bancaria and self.entidad_bancaria_id is None:
            raise ValueError("Indicá la entidad bancaria de la cuenta")
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
