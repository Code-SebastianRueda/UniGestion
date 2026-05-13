# UniGestión HR Platform

Plataforma integral de gestión de Recursos Humanos con inteligencia artificial para búsqueda semántica de candidatos.

## Características Principales

- **Autenticación y Roles**: Login/Registro con roles (Candidato, Empleado, RH)
- **Gestión de Candidatos**: Subida y parsing inteligente de CVs
- **Matching con IA**: Búsqueda semántica de candidatos usando Sentence Transformers
- **Chat RH tipo ChatGPT**: Interfaz conversacional para búsqueda de talento
- **Portal del Empleado**: Dashboard, vacaciones, nómina, certificados, solicitudes
- **Generación de PDFs**: Comprobantes de nómina y certificados laborales profesionales
- **Dashboard RH**: Estadísticas y gestión centralizada

## Stack Tecnológico

| Componente | Tecnología |
|-----------|-----------|
| Backend | Python, FastAPI, SQLAlchemy |
| Base de Datos | PostgreSQL 15 |
| Frontend | HTML5, CSS3, Bootstrap 5, JavaScript Vanilla |
| IA/NLP | Sentence Transformers, scikit-learn |
| PDFs | ReportLab |
| Infraestructura | Docker, Docker Compose |

## Inicio Rápido

### Requisitos
- Docker y Docker Compose instalados

### Ejecución

```bash
docker compose up -d --build
```

La aplicación estará disponible en: **http://localhost:8000**

### Credenciales Demo

| Rol | Email | Contraseña |
|-----|-------|-----------|
| RH | admin@unigestion.com | admin123 |
| Empleado | empleado@unigestion.com | emp123 |
| Candidato | candidato@unigestion.com | cand123 |

## Estructura del Proyecto

```
UniGestion/
├── backend/
│   ├── app/
│   │   ├── main.py              # Aplicación FastAPI principal
│   │   ├── models.py            # Modelos SQLAlchemy
│   │   ├── database.py          # Configuración de BD
│   │   ├── auth.py              # Autenticación JWT
│   │   ├── matching.py          # Motor de matching con IA
│   │   ├── documents.py         # Generación de PDFs
│   │   ├── seed_data.py         # Datos demo
│   │   ├── routes/
│   │   │   ├── auth_routes.py   # Endpoints de autenticación
│   │   │   ├── candidate_routes.py  # Endpoints de candidatos
│   │   │   ├── employee_routes.py   # Endpoints de empleados
│   │   │   └── rh_routes.py    # Endpoints de RH
│   │   ├── static/
│   │   │   ├── css/styles.css   # Estilos globales
│   │   │   └── js/app.js       # JavaScript principal
│   │   ├── templates/
│   │   │   ├── auth.html        # Login/Registro
│   │   │   ├── candidate.html   # Portal candidato
│   │   │   ├── employee.html    # Portal empleado
│   │   │   └── rh.html         # Panel RH
│   │   └── assets/
│   │       └── logo.png         # Logo corporativo
│   ├── uploads/                 # CVs subidos
│   ├── requirements.txt
│   └── Dockerfile
├── scripts/
│   └── init.sql                 # Script SQL de referencia
├── docker-compose.yml
└── README.md
```

## Endpoints API

### Autenticación
- `POST /api/auth/register` - Registro de usuario
- `POST /api/auth/login` - Inicio de sesión
- `GET /api/auth/me` - Usuario actual

### Candidatos
- `POST /api/candidates/upload-cv` - Subir CV (PDF)
- `GET /api/candidates/profile` - Perfil del candidato
- `GET /api/candidates/all` - Listar candidatos (RH)

### Empleados
- `GET /api/employee/profile` - Perfil y dashboard
- `GET /api/employee/vacations` - Listar vacaciones
- `POST /api/employee/vacations` - Solicitar vacaciones
- `GET /api/employee/payroll` - Historial de nómina
- `GET /api/employee/payroll/{id}/pdf` - Descargar nómina PDF
- `GET /api/employee/certificate` - Descargar certificado laboral
- `GET /api/employee/requests` - Listar solicitudes
- `POST /api/employee/requests` - Crear solicitud

### Recursos Humanos
- `GET /api/rh/dashboard` - Estadísticas
- `GET /api/rh/candidates` - Listar candidatos
- `POST /api/rh/convert-employee` - Convertir candidato a empleado
- `GET /api/rh/employees` - Listar empleados
- `GET /api/rh/vacations` - Listar vacaciones
- `PUT /api/rh/vacations/{id}` - Aprobar/Rechazar vacación
- `GET /api/rh/requests` - Listar solicitudes
- `POST /api/rh/chat` - Chat IA de búsqueda

## Flujo Funcional

1. **Candidato** se registra → sube su CV → el sistema lo parsea y genera embeddings
2. **RH** usa el Chat IA → busca candidatos con lenguaje natural → el motor de matching encuentra los mejores perfiles
3. **RH** convierte candidato a empleado → se crea perfil de empleado
4. **Empleado** accede a su portal → solicita vacaciones, consulta nómina, descarga certificados
5. **RH** gestiona solicitudes → aprueba/rechaza vacaciones y solicitudes

## Motor de IA

El sistema utiliza **Sentence Transformers** (modelo `all-MiniLM-L6-v2`) para:
- Generar embeddings de los CVs procesados
- Calcular similitud coseno entre consultas y perfiles
- Ranking inteligente con pesos por habilidades, experiencia y áreas
- Soporte para consultas en español e inglés

## Notas

- La primera ejecución descargará el modelo de IA (~90MB)
- Los PDFs se generan dinámicamente con ReportLab
- Coloca un archivo `logo.png` en `backend/app/assets/` para personalizar los PDFs
- La base de datos se inicializa automáticamente con datos demo

## Licencia

Proyecto académico/profesional - UniGestión HR Platform
