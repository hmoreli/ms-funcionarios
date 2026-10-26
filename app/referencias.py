"""Ids que pertenecen a ms-organizacion: se verifica que existan antes de guardar."""

from rrhh_common import Referencia

PAIS_DOCUMENTO = Referencia("pais_documento_id", "organizacion", "/paises/{id}", "país")
PAIS_ORIGEN = Referencia("pais_origen_id", "organizacion", "/paises/{id}", "país")
CIUDAD = Referencia("ciudad_id", "organizacion", "/ciudades/{id}", "ciudad")
TIPO_CONTRATO = Referencia(
    "tipo_contrato_id", "organizacion", "/tipos-contrato/{id}", "tipo de contrato"
)

FUNCIONARIO = (PAIS_DOCUMENTO, PAIS_ORIGEN, CIUDAD, TIPO_CONTRATO)
