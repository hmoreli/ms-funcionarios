from datetime import date

from tests.conftest import CONSULTA, OPERADOR, encabezado, validador_simulado

BASE = {
    "numero_documento": "4567890",
    "nombres": "Ana María",
    "apellidos": "Benítez Gómez",
    "pais_documento_id": 1,
    "pais_origen_id": 1,
    "fecha_ingreso": "2024-03-01",
    "estado": "activo",
    "telefono": "0981123456",
}


def alta(cliente, **cambios):
    r = cliente.post("/funcionarios", json={**BASE, **cambios}, headers=OPERADOR)
    assert r.status_code == 201, r.text
    return r.json()


def test_alta_y_consulta(cliente):
    f = alta(
        cliente,
        estado_civil="casado",
        correo_electronico="ana@example.com",
    )
    r = cliente.get(f"/funcionarios/{f['id']}", headers=CONSULTA)
    assert r.json()["estado_civil"] == "casado"
    assert r.json()["apellidos"] == "Benítez Gómez"


def test_documento_duplicado_409(cliente):
    alta(cliente)
    r = cliente.post("/funcionarios", json=BASE, headers=OPERADOR)
    assert r.status_code == 409


def test_campos_obligatorios_del_contrato(cliente):
    sin_telefono = {k: v for k, v in BASE.items() if k != "telefono"}
    r = cliente.post("/funcionarios", json=sin_telefono, headers=OPERADOR)
    assert r.status_code == 422
    assert r.json()["detalles"][0]["campo"] == "body.telefono"


def test_egreso_anterior_al_ingreso_es_invalido(cliente):
    r = cliente.post("/funcionarios", json={**BASE, "fecha_egreso": "2020-01-01"}, headers=OPERADOR)
    assert r.status_code == 422


def test_correo_invalido(cliente):
    r = cliente.post(
        "/funcionarios", json={**BASE, "correo_electronico": "no-es-mail"}, headers=OPERADOR
    )
    assert r.status_code == 422


def test_delete_es_baja_logica(cliente):
    f = alta(cliente)
    assert cliente.delete(f"/funcionarios/{f['id']}", headers=OPERADOR).status_code == 204
    r = cliente.get(f"/funcionarios/{f['id']}", headers=CONSULTA).json()
    assert r["estado"] == "inactivo"
    assert r["fecha_egreso"] == date.today().isoformat()


def test_filtro_por_estado(cliente):
    a = alta(cliente, numero_documento="1")
    alta(cliente, numero_documento="2")
    cliente.delete(f"/funcionarios/{a['id']}", headers=OPERADOR)
    activos = cliente.get("/funcionarios?estado=activo", headers=CONSULTA).json()
    assert [f["numero_documento"] for f in activos] == ["2"]


def test_hijos_de_un_funcionario(cliente):
    f = alta(cliente)
    r = cliente.post(
        "/hijos",
        json={
            "funcionario_id": f["id"],
            "nombre": "Sofía",
            "fecha_nacimiento": "2018-05-10",
            "apto_bonificacion": True,
        },
        headers=OPERADOR,
    )
    assert r.status_code == 201
    lista = cliente.get(f"/hijos?funcionario_id={f['id']}", headers=CONSULTA).json()
    assert [h["nombre"] for h in lista] == ["Sofía"]


def test_hijo_de_funcionario_inexistente_409(cliente):
    r = cliente.post(
        "/hijos",
        json={"funcionario_id": 99, "nombre": "X", "fecha_nacimiento": "2018-05-10"},
        headers=OPERADOR,
    )
    assert r.status_code == 409


def test_rutas_del_contrato_existen(cliente):
    rutas = cliente.get("/openapi.json").json()["paths"]
    assert {"/funcionarios", "/funcionarios/{id}", "/hijos", "/hijos/{id}"} <= set(rutas)
    assert {"get", "patch", "delete"} <= set(rutas["/funcionarios/{id}"])


def test_cuenta_bancaria_solo_para_rrhh_y_nomina(cliente):
    f = alta(cliente, numero_cuenta_bancaria="000-123456-7")
    nomina = encabezado("nomina-liquidador")
    assert (
        cliente.get(f"/funcionarios/{f['id']}", headers=OPERADOR).json()["numero_cuenta_bancaria"]
        == "000-123456-7"
    )
    assert cliente.get("/funcionarios", headers=nomina).json()[0]["numero_cuenta_bancaria"]
    assert (
        cliente.get(f"/funcionarios/{f['id']}", headers=CONSULTA).json()["numero_cuenta_bancaria"]
        is None
    )
    assert (
        cliente.get("/funcionarios", headers=CONSULTA).json()[0]["numero_cuenta_bancaria"] is None
    )


def test_busqueda_por_nombre_o_documento(cliente):
    alta(cliente, numero_documento="111", nombres="Juan", apellidos="Pérez")
    alta(cliente, numero_documento="222", nombres="Rosa", apellidos="Juanes")
    alta(cliente, numero_documento="333", nombres="Luis", apellidos="Ortiz")
    juan = cliente.get("/funcionarios?q=juan", headers=CONSULTA).json()
    assert [f["numero_documento"] for f in juan] == ["111", "222"]
    assert [f["nombres"] for f in cliente.get("/funcionarios?q=33", headers=CONSULTA).json()] == [
        "Luis"
    ]


def test_sin_nombres_es_invalido(cliente):
    datos = {k: v for k, v in BASE.items() if k != "nombres"}
    assert cliente.post("/funcionarios", json=datos, headers=OPERADOR).status_code == 422


def test_valida_ids_de_ms_organizacion(cliente):
    cliente.app.state.referencias = validador_simulado("ms-organizacion/paises/1")
    alta(cliente)
    r = cliente.post(
        "/funcionarios",
        json={**BASE, "numero_documento": "1", "pais_origen_id": 7},
        headers=OPERADOR,
    )
    assert r.status_code == 422
    assert r.json()["detalles"] == [
        {"campo": "body.pais_origen_id", "mensaje": "No existe el país 7"}
    ]
