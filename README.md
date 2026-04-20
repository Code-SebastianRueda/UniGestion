# Plataforma de Gestión de Recursos Humanos

## 📋 Descripción

Sistema integral de gestión de recursos humanos desarrollado para el Politécnico Grancolombiano. Esta plataforma combina reclutamiento inteligente con gestión completa de empleados, utilizando algoritmos de IA para matching de candidatos y procesamiento automático de documentos.

## 🚀 Características Principales

### 🤖 Reclutamiento Inteligente
- **Subida y análisis de CVs**: Soporte para PDF y DOCX con extracción automática de texto
- **Matching híbrido**: Combina búsqueda por keywords con similitud semántica usando embeddings
- **Chat-based search**: Los reclutadores pueden describir requisitos en lenguaje natural
- **Sistema de puntuación**: Algoritmo inteligente que considera skills, áreas, experiencia y sinónimos

### 👥 Gestión de Empleados
- **Perfiles completos**: Información laboral, contacto y datos personales
- **Gestión de vacaciones**: Solicitudes, aprobaciones y seguimiento
- **Nómina**: Registro de salarios, bonos, deducciones y generación de comprobantes
- **Documentos**: Certificados laborales y otros documentos oficiales en PDF

### 🔐 Sistema de Autenticación
- **Roles diferenciados**: Candidato, Empleado, Recursos Humanos
- **Dashboards específicos**: Interfaces adaptadas según el rol del usuario
- **Seguridad**: Autenticación por email/contraseña

## 🏗️ Arquitectura

### Backend
- **Framework**: FastAPI (Python)
- **Base de datos**: PostgreSQL
- **ORM**: SQLAlchemy
- **IA/ML**: Sentence Transformers para embeddings semánticos
- **Documentos**: ReportLab para generación de PDFs

### Frontend
- **Tecnología**: HTML5 + Bootstrap + JavaScript
- **Arquitectura**: Páginas estáticas servidas por FastAPI
- **Responsive**: Diseño adaptativo para diferentes dispositivos

### Infraestructura
- **Contenedorización**: Docker + Docker Compose
- **Base de datos**: PostgreSQL en contenedor
- **Volúmenes**: Persistencia de datos y archivos subidos

## 📊 Modelo de Datos

### Tablas Principales
- **Users**: Usuarios del sistema con roles
- **CandidateProfile**: Perfiles estructurados de candidatos
- **Employee**: Información completa de empleados
- **Resume**: CVs subidos y texto extraído
- **Payroll**: Registros de nómina
- **Vacation**: Solicitudes de vacaciones
- **Document**: Documentos asociados a empleados

## 🔧 Instalación y Configuración

### Prerrequisitos
- Docker y Docker Compose
- Python 3.11+ (opcional para desarrollo local)

### Instalación con Docker
```bash
# Clonar el repositorio
git clone <url-del-repositorio>
cd proyecto

# Construir y ejecutar servicios
docker-compose up --build
```

### Acceso a la aplicación
- **API Backend**: http://localhost:8000
- **Frontend**: http://localhost:8000/auth.html
- **Base de datos**: localhost:5432 (hr_user/hr_password)

### Configuración manual (desarrollo)
```bash
# Instalar dependencias
pip install -r backend/requirements.txt

# Configurar base de datos
# Editar DATABASE_URL en database.py si es necesario

# Ejecutar migraciones
python -c "from backend.app.database import Base, engine; Base.metadata.create_all(bind=engine)"

# Ejecutar aplicación
uvicorn backend.app.main:app --reload
```

## 📖 Uso

### Para Candidatos
1. **Registro**: Crear cuenta con documento de identidad
2. **Subir CV**: Cargar CV en PDF o DOCX
3. **Postular**: El sistema procesa automáticamente el CV

### Para RH
1. **Login**: Acceder con credenciales de administrador
2. **Buscar candidatos**: Usar chat o filtros específicos
3. **Gestionar empleados**: Aprobar vacaciones, generar documentos
4. **Administrar nómina**: Ver y descargar comprobantes

### Para Empleados
1. **Login**: Acceder con credenciales personales
2. **Solicitar vacaciones**: Enviar peticiones de tiempo libre
3. **Ver nómina**: Consultar salarios y descargar comprobantes
4. **Descargar documentos**: Obtener certificados laborales

## 🔍 API Endpoints

### Autenticación
- `POST /register` - Registro de usuarios
- `POST /login` - Inicio de sesión

### Candidatos
- `POST /upload-cv/{user_id}` - Subir CV
- `POST /chat-match` - Búsqueda conversacional
- `POST /ai-match` - Matching semántico

### Empleados
- `GET /employee/{user_id}` - Información del empleado
- `GET /vacations/{user_id}` - Historial de vacaciones
- `POST /vacations/request` - Solicitar vacaciones
- `GET /payroll/{user_id}` - Historial de nómina

### RH
- `GET /rh/vacations` - Todas las solicitudes de vacaciones
- `PUT /rh/vacations/{id}/approve` - Aprobar vacaciones
- `GET /employee/certificate/{user_id}` - Generar certificado

## 🤖 Algoritmos de IA

### Matching de Candidatos
- **Keywords matching**: Búsqueda exacta con sinónimos
- **Semantic similarity**: Embeddings para comprensión contextual
- **Scoring system**: Puntuación por skills (10pts), áreas (7pts), resumen (3pts)

### Procesamiento de CVs
- **Extracción de texto**: PDF con pdfplumber, DOCX con python-docx
- **Parsing estructurado**: Identificación de skills, experiencia, educación
- **Normalización**: Eliminación de acentos y conversión a minúsculas

## 📄 Generación de Documentos

### Certificados Laborales
- Información del empleado y empresa
- Logo institucional
- Firma digital simulada

### Comprobantes de Nómina
- Desglose de salario, bonos y deducciones
- Tabla formateada con colores
- Información del período

## 🧪 Testing y Datos de Prueba

### Generar CVs de prueba
```bash
cd backend/scripts
python generate_cvs.py
```

### Usuario administrador por defecto
- **Email**: admin@rh.com
- **Password**: 123456
- **Rol**: rh

## 🔒 Seguridad

- **Autenticación**: Email/contraseña (considerar implementar hashing)
- **Roles**: Control de acceso basado en roles
- **Validación**: Pydantic para entrada de datos
- **CORS**: Configurado para desarrollo local

## 🚧 Estado del Proyecto

### Implementado ✅
- Sistema completo de autenticación
- Subida y parsing de CVs
- Matching inteligente de candidatos
- Gestión de empleados y vacaciones
- Generación de documentos PDF
- Interfaces web básicas


## 👥 Equipo
Wilson David Florez 
Juan Sebastian Rueda
Proyecto desarrollado como parte del curso de Gestión de Proyectos en el Politécnico Grancolombiano.

## 📄 Licencia

Este proyecto es propiedad del Politécnico Grancolombiano para fines académicos y de investigación.
