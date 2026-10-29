# ms-funcionarios

Microservicio de Gestión de Funcionarios. Núcleo del legajo: datos del funcionario y de sus hijos.

Implementa el contrato [`contrato/openapi.yaml`](contrato/openapi.yaml) con FastAPI, SQLAlchemy 2 y Alembic sobre PostgreSQL (schema `funcionarios`).

## Respecto al contrato

- `DELETE /funcionarios/{id}` es una **baja lógica**: pasa a `inactivo` y completa `fecha_egreso` con la fecha del día. El legajo no se borra.
- Filtros: `/funcionarios?estado=activo&numero_documento=&q=` (`q` busca en nombres, apellidos y documento), `/hijos?funcionario_id=`.
- `nombres` y `apellidos` son obligatorios.
- El cargo actual no está acá: lo maneja ms-desempeno (`/historicos-cargo` y `/cargos-actuales`). Los horarios los maneja ms-asistencia.
- La cuenta bancaria solo la ven `rrhh-operador` y `nomina-liquidador`; al resto le llega vacía.
- Valida email, `fecha_egreso >= fecha_ingreso` y documento único (409 si se repite).
- `telefono` va en formato internacional, solo dígitos: código de país + número, sin `+` ni 0 inicial (`595981123456`).
- `fecha_ingreso` y `fecha_ingreso_seguro_social` no pueden ser posteriores a hoy (zona `ZONA_HORARIA`, por defecto `America/Asuncion`), y la de IPS no puede ser anterior a la de ingreso. El PATCH valida contra los valores ya guardados.
- Con `numero_cuenta_bancaria` hay que indicar `entidad_bancaria_id` (catálogo `/entidades-bancarias` de ms-organizacion).
- Los `*_id` de país, ciudad y tipo de contrato son de ms-organizacion: no hay FK física entre servicios.
- Los ids de otros servicios (país, ciudad, tipo de contrato y entidad bancaria) se verifican con el servicio dueño antes de guardar: 422 si no existe, 503 si no responde. Usa el client `ms-funcionarios` de Keycloak (`SERVICIO_CLIENT_ID`/`SERVICIO_CLIENT_SECRET`); sin esas variables, como en las pruebas, no se verifica.

## Desarrollo

Este repo usa `rrhh-common`, que tiene que estar clonado al lado:

```
rrhh/
├── rrhh-common/
├── rrhh-plataforma/
└── ms-funcionarios/
```

```bash
python -m venv .venv && . .venv/bin/activate
pip install "../rrhh-common[db]" -e ".[dev]"
pytest              # usa SQLite en memoria, no necesita la plataforma
ruff check app tests && ruff format --check app tests
```

## Levantar con la plataforma

```bash
cd ../rrhh-plataforma && docker compose up -d
cd ../ms-funcionarios && docker compose up -d --build
```

Al arrancar, el contenedor aplica las migraciones (`alembic upgrade head`) en el schema `funcionarios`. Queda accesible solo por Kong en `http://localhost:8000/api/funcionarios/...` con un token de Keycloak. La documentación interactiva está en `/api/funcionarios/docs` (también detrás del gateway).

## Migraciones

```bash
export DATABASE_URL=postgresql+psycopg://ms_funcionarios:servicio-dev@localhost:5432/rrhh
alembic revision --autogenerate -m "descripcion del cambio"
alembic upgrade head
```

## Roles

Lectura: `rrhh-operador`, `nomina-liquidador`, `consulta`. Escritura: `rrhh-operador`. `rrhh-admin` puede todo.

## CI

GitHub Actions corre ruff y pytest. Como `rrhh-common` es privado, el repo necesita el secreto **`RRHH_COMMON_TOKEN`**: un token *fine-grained* con permiso `Contents: read` sobre `hmoreli/rrhh-common`.
