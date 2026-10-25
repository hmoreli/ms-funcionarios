from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Response
from rrhh_common import Usuario, requiere_roles
from rrhh_common.crud import ROLES_ESCRITURA, router_crud
from sqlalchemy.orm import Session

from app import esquemas as e
from app import modelos as m
from app.db import obtener_sesion

funcionarios = router_crud(
    modelo=m.Funcionario,
    crear=e.FuncionarioPost,
    parche=e.FuncionarioPatch,
    salida=e.Funcionario,
    prefijo="/funcionarios",
    etiqueta="Gestión de Funcionarios",
    nombre="Funcionario",
    sesion=obtener_sesion,
    filtros={"estado": m.EstadoFuncionario, "cargo_id": int, "numero_documento": str},
    # DELETE se reemplaza por una baja lógica (abajo).
    metodos={"listar", "crear", "obtener", "actualizar"},
)


@funcionarios.delete("/{id}", status_code=204, summary="Dar de baja un funcionario")
def dar_de_baja(
    id: int,
    db: Session = Depends(obtener_sesion),
    _: Usuario = Depends(requiere_roles(*ROLES_ESCRITURA)),
):
    """No borra el legajo: lo pasa a `inactivo` y completa `fecha_egreso` con hoy si
    estaba vacía. Así no se pierde el historial que usan nómina y vacaciones."""
    funcionario = db.get(m.Funcionario, id)
    if funcionario is None:
        raise HTTPException(404, detail="Funcionario no encontrado")
    funcionario.estado = m.EstadoFuncionario.inactivo
    funcionario.fecha_egreso = funcionario.fecha_egreso or date.today()
    db.commit()
    return Response(status_code=204)


hijos = router_crud(
    modelo=m.Hijo,
    crear=e.HijoPost,
    parche=e.HijoPatch,
    salida=e.Hijo,
    prefijo="/hijos",
    etiqueta="Gestión de Hijos",
    nombre="Hijo",
    sesion=obtener_sesion,
    filtros={"funcionario_id": int},
)

routers: list[APIRouter] = [funcionarios, hijos]
