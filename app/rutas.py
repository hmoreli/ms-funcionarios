from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.exceptions import RequestValidationError
from rrhh_common import Paginacion, Usuario, requiere_roles, verificar_referencias
from rrhh_common.crud import ROLES_ESCRITURA, ROLES_LECTURA, router_crud
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import esquemas as e
from app import modelos as m
from app.db import obtener_sesion
from app.fechas import errores_de_fechas
from app.referencias import FUNCIONARIO

# Roles que pueden ver la cuenta bancaria; el resto (p. ej. consulta) la recibe vacía.
ROLES_CUENTA = ("rrhh-operador", "nomina-liquidador")
leer = requiere_roles(*ROLES_LECTURA)

funcionarios = router_crud(
    modelo=m.Funcionario,
    crear=e.FuncionarioPost,
    parche=e.FuncionarioPatch,
    salida=e.Funcionario,
    prefijo="/funcionarios",
    etiqueta="Gestión de Funcionarios",
    nombre="Funcionario",
    sesion=obtener_sesion,
    referencias=FUNCIONARIO,
    # Los listados se arman abajo (ocultan la cuenta bancaria según el rol), el PATCH
    # valida las fechas contra lo ya guardado y DELETE se reemplaza por una baja lógica.
    metodos={"crear"},
)


def _para(usuario: Usuario, funcionario: m.Funcionario) -> e.Funcionario:
    salida = e.Funcionario.model_validate(funcionario)
    if not usuario.tiene_rol(*ROLES_CUENTA):
        salida.numero_cuenta_bancaria = None
        salida.entidad_bancaria_id = None
    return salida


@funcionarios.patch("/{id}", response_model=e.Funcionario, summary="Actualizar funcionario")
def actualizar(
    id: int,
    datos: e.FuncionarioPatch,
    request: Request,
    db: Session = Depends(obtener_sesion),
    _: Usuario = Depends(requiere_roles(*ROLES_ESCRITURA)),
):
    funcionario = db.get(m.Funcionario, id)
    if funcionario is None:
        raise HTTPException(404, detail="Funcionario no encontrado")
    cambios = datos.model_dump(exclude_unset=True)
    verificar_referencias(request, FUNCIONARIO, cambios)
    # Las reglas cruzan campos: se validan sobre el legajo como quedaría.
    final = {c: cambios.get(c, getattr(funcionario, c)) for c in e.CAMPOS_CON_REGLAS}
    errores = [
        {"type": "regla", "loc": ("body", campo), "msg": mensaje, "input": final[campo]}
        for campo, mensaje in errores_de_fechas(
            final["fecha_ingreso"], final["fecha_ingreso_seguro_social"], final["fecha_egreso"]
        )
    ]
    if final["numero_cuenta_bancaria"] and final["entidad_bancaria_id"] is None:
        errores.append(
            {
                "type": "regla",
                "loc": ("body", "entidad_bancaria_id"),
                "msg": "Indicá la entidad bancaria de la cuenta",
                "input": None,
            }
        )
    if errores:
        raise RequestValidationError(errores)
    for campo, valor in cambios.items():
        setattr(funcionario, campo, valor)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            409, detail="Ya existe un funcionario con ese documento o correo"
        ) from exc
    db.refresh(funcionario)
    return funcionario


@funcionarios.get("", response_model=list[e.Funcionario], summary="Listar funcionarios")
def listar(
    p: Paginacion = Depends(),
    estado: m.EstadoFuncionario | None = None,
    numero_documento: str | None = None,
    q: str | None = Query(
        None, min_length=1, description="Buscar en nombres, apellidos y número de documento"
    ),
    db: Session = Depends(obtener_sesion),
    usuario: Usuario = Depends(leer),
):
    consulta = select(m.Funcionario)
    if estado is not None:
        consulta = consulta.where(m.Funcionario.estado == estado)
    if numero_documento is not None:
        consulta = consulta.where(m.Funcionario.numero_documento == numero_documento)
    if q:
        patron = f"%{q}%"
        consulta = consulta.where(
            or_(
                m.Funcionario.nombres.ilike(patron),
                m.Funcionario.apellidos.ilike(patron),
                m.Funcionario.numero_documento.ilike(patron),
            )
        )
    consulta = consulta.order_by(m.Funcionario.id).offset(p.offset).limit(p.limit)
    return [_para(usuario, f) for f in db.scalars(consulta)]


@funcionarios.get("/{id}", response_model=e.Funcionario, summary="Obtener funcionario por ID")
def obtener(id: int, db: Session = Depends(obtener_sesion), usuario: Usuario = Depends(leer)):
    funcionario = db.get(m.Funcionario, id)
    if funcionario is None:
        raise HTTPException(404, detail="Funcionario no encontrado")
    return _para(usuario, funcionario)


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
