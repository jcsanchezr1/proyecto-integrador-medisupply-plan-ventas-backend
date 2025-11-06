# MediSupply Sales Plan Backend

Sistema de gestión de planes de ventas para MediSupply.

## Descripción

Este servicio se encarga de la gestión de planes de ventas en el sistema MediSupply, permitiendo crear y consultar planes de ventas con información detallada de cliente, fechas, metas de ingresos y objetivos.

## Estructura del Proyecto

```
proyecto-integrador-medisupply-plan-ventas-backend/
├── app/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   └── database.py
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── base_controller.py
│   │   ├── health_controller.py
│   │   ├── sales_plan_controller.py
│   │   └── sales_plan_create_controller.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base_model.py
│   │   ├── sales_plan.py
│   │   └── db_models.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base_repository.py
│   │   └── sales_plan_repository.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── base_service.py
│   │   └── sales_plan_service.py
│   ├── exceptions/
│   │   ├── __init__.py
│   │   └── custom_exceptions.py
│   └── utils/
│       └── __init__.py
├── app.py
├── requirements.txt
├── Dockerfile
└── README.md
```

## Instalación

1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

2. Configurar variables de entorno:
   - `DATABASE_URL`: URL de conexión a PostgreSQL
   - `AUTH_SERVICE_URL`: URL del servicio de autenticación
   - `PORT`: Puerto del servicio (default: 8080)

3. Ejecutar:
   ```bash
   python app.py
   ```

### Pruebas unitarias

1. Correr pruebas unitarias con coverage:
   ```bash
   coverage run -m unittest discover -s tests
   ```

1. Ver reporte de cobertura de las pruebas unitarias
   ```bash
   coverage report
   ```

## Endpoints

### Health Check
- `GET /sales-plan/ping` - Verifica el estado del servicio
  - **Respuesta**: `"pong"`

### Gestión de Planes de Ventas
- `POST /sales-plan/create` - Crea un nuevo plan de ventas
  - Body: `name`, `start_date`, `end_date`, `client_id`, `target_revenue`, `objectives` (opcional)
  
- `GET /sales-plan` - Obtiene planes de ventas con paginación
  - Query params:
    - `page` (default: 1)
    - `per_page` (default: 10, max: 100)
    - `name` - Búsqueda por nombre (LIKE)
    - `client_id` - Filtrar por cliente
    - `start_date` - Filtrar por fecha inicio
    - `end_date` - Filtrar por fecha fin
  
- `DELETE /sales-plan/delete-all` - Elimina todos los planes de ventas

## Modelo de Datos

### SalesPlan
- `id`: Integer (PK, autoincrement)
- `name`: String(255), unique, NOT NULL
- `start_date`: DateTime, NOT NULL
- `end_date`: DateTime, NOT NULL
- `client_id`: String(36), NOT NULL (UUID)
- `target_revenue`: Float, NOT NULL (máximo 2 decimales)
- `objectives`: Text, nullable
- `created_at`: DateTime
- `updated_at`: DateTime

## Validaciones

1. **name**: Solo caracteres alfabéticos, espacios y tildes
2. **client_id**: Debe existir en el servicio de autenticación
3. **start_date <= end_date**: La fecha de inicio debe ser menor o igual a la fecha de fin
4. **target_revenue >= 0**: Número mayor o igual a 0, máximo 2 decimales
5. **name único**: No se permiten nombres duplicados

## Integración con Servicio de Autenticación

El servicio valida que el `client_id` existe llamando al servicio de autenticación en `/clients/{client_id}`.

## Tecnologías

- Python 3.9
- Flask 3.0.3
- Flask-RESTful 0.3.10
- SQLAlchemy 2.0.34
- PostgreSQL (psycopg2-binary)
- Gunicorn 21.2.0
- pytest 8.3.4