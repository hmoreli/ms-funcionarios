import enum
from datetime import date

from sqlalchemy import CheckConstraint, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class EstadoCivil(enum.StrEnum):
    casado = "casado"
    soltero = "soltero"
    viudo = "viudo"
    union_de_hecho = "union_de_hecho"


class EstadoFuncionario(enum.StrEnum):
    activo = "activo"
    inactivo = "inactivo"


class Funcionario(Base):
    """Legajo base. Los *_id de país, ciudad, cargo y tipo de contrato apuntan a
    ms-organizacion: no hay FK física entre servicios."""

    __tablename__ = "funcionario"
    __table_args__ = (
        CheckConstraint("fecha_egreso IS NULL OR fecha_egreso >= fecha_ingreso", name="egreso"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    numero_documento: Mapped[str] = mapped_column(String(50), unique=True)
    nombres: Mapped[str] = mapped_column(String(100))
    apellidos: Mapped[str] = mapped_column(String(100), index=True)
    pais_documento_id: Mapped[int]
    pais_origen_id: Mapped[int]
    estado_civil: Mapped[EstadoCivil | None] = mapped_column(Enum(EstadoCivil, name="estado_civil"))
    fecha_ingreso: Mapped[date]
    direccion: Mapped[str | None] = mapped_column(String(255))
    ciudad_id: Mapped[int | None]
    correo_electronico: Mapped[str | None] = mapped_column(String(100), unique=True)
    fecha_ingreso_seguro_social: Mapped[date | None]
    fecha_egreso: Mapped[date | None]
    estado: Mapped[EstadoFuncionario] = mapped_column(
        Enum(EstadoFuncionario, name="estado_funcionario"), index=True
    )
    numero_cuenta_bancaria: Mapped[str | None] = mapped_column(String(50))
    tipo_contrato_id: Mapped[int | None]
    telefono: Mapped[str] = mapped_column(String(20))
    contacto_emergencia: Mapped[str | None] = mapped_column(String(100))


class Hijo(Base):
    __tablename__ = "hijo"
    id: Mapped[int] = mapped_column(primary_key=True)
    funcionario_id: Mapped[int] = mapped_column(ForeignKey("funcionario.id"), index=True)
    nombre: Mapped[str] = mapped_column(String(100))
    fecha_nacimiento: Mapped[date]
    documento: Mapped[str | None] = mapped_column(String(50), unique=True)
    apto_bonificacion: Mapped[bool | None]
