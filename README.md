Callcenter-app

Sistema web para la gestión centralizada de requerimientos, reclutamiento, postulación y formación de personal en un contact center.

El proyecto permite registrar requerimientos de personal, administrar campañas y puestos, generar formularios públicos de postulación, revisar candidatos, gestionar entrevistas, registrar resultados de formación y dar seguimiento al avance del flujo operativo.

---

## Descripción del proyecto

**Callcenter-app** fue desarrollado como una solución web orientada a mejorar la trazabilidad del proceso de incorporación de personal en campañas de call center.

El sistema cubre el flujo principal:


Planeamiento → Reclutamiento → Postulación pública → Formación → Resultados


Actualmente, el frontend se encuentra funcional con datos simulados mediante mocks. Además, el repositorio incluye una carpeta de backend preparada para integración con AWS Academy mediante API Gateway, Lambda y base de datos relacional.

---

## Funcionalidades principales

### Planeamiento

* Registro de requerimientos de personal.
* Selección de campañas activas y puestos disponibles.
* Validación de fechas de capacitación e ingreso.
* Dashboard de requerimientos, personal solicitado, postulantes y contratados.
* Vista previa del requerimiento antes de registrarlo.

### Reclutamiento

* Visualización de requerimientos activos.
* Generación de enlace público de postulación por RQ.
* Gestión de candidatos por requerimiento.
* Clasificación de candidatos según requisito y entrevista.
* Visualización del detalle del postulante y enlace de CV.
* Registro de decisión final de contratación.

### Postulación pública

* Pantalla pública sin barra de navegación interna.
* Formulario externo para postulantes.
* Validación de DNI, teléfono, correo y enlace de CV.
* Registro de CV mediante enlace de Google Drive.
* Bloqueo automático cuando el requerimiento está cerrado.

### Formación

* Gestión de postulantes aprobados por reclutamiento.
* Configuración de cantidad de evaluaciones.
* Registro de notas por evaluación.
* Cálculo automático de promedio.
* Clasificación de aprobados y no aprobados.
* Dashboard de seguimiento de formación.

---

## Tecnologías utilizadas

### Frontend

* Angular
* TypeScript
* HTML
* CSS
* Angular Router
* FormsModule
* Componentes standalone
* Diseño responsive

### Backend

* Python
* AWS Lambda
* API Gateway
* SQL Server / RDS
* AWS SAM
* Pydantic
* PyODBC

### Herramientas de desarrollo

* Git
* GitHub
* Visual Studio Code
* AWS Academy
* Angular CLI

---

## Estructura del proyecto

Callcenter-app/
├── public/
│   ├── logo.png
│   └── logonombre.png
│
├── src/
│   └── app/
│       ├── mocks/
│       ├── models/
│       ├── pages/
│       │   ├── formacion/
│       │   ├── planeamiento/
│       │   ├── postular/
│       │   └── reclutamiento/
│       ├── services/
│       └── shared/
│
├── backend/
│   ├── infrastructure/
│   ├── sql/
│   ├── tests/
│   └── lambda_function.py
│
├── angular.json
├── package.json
└── README.md



## Instalación del frontend

Clonar el repositorio:

git clone https://github.com/Fanaker/Callcenter-app.git

Ingresar al proyecto:


cd Callcenter-app


Instalar dependencias:


npm install


Ejecutar el servidor de desarrollo:


ng serve -o


La aplicación se abrirá en:


http://localhost:4200/


---

## Compilación del frontend

Para generar la versión de producción:


ng build


Los archivos compilados se generarán en:


dist/


---

## Backend

El backend se encuentra dentro de la carpeta:


backend/


Esta carpeta contiene la estructura necesaria para trabajar la integración con AWS Academy, incluyendo Lambda, API Gateway, scripts SQL, infraestructura y pruebas.

La arquitectura esperada es:


Angular → API Gateway → Lambda → RDS / SQL Server


El frontend no se conecta directamente a la base de datos. La comunicación debe realizarse mediante endpoints expuestos por API Gateway.

---

## Endpoints esperados para integración

Para conectar el frontend con el backend, se espera contar con endpoints similares a:


GET    /campanias/activas
GET    /puestos/activos
GET    /requerimientos
GET    /requerimientos/{codigo}
POST   /requerimientos
GET    /requerimientos/{codigo}/postulaciones
POST   /postulaciones
PUT    /postulaciones/{idPostulacion}/requisito
PUT    /postulaciones/{idPostulacion}/entrevista
PUT    /postulaciones/{idPostulacion}/contratacion


Para el módulo de formación, se requiere contemplar endpoints para configuración de evaluaciones y registro de notas.

---

## Estado actual del proyecto

* Frontend funcional.
* Diseño visual pulido y responsive.
* Datos gestionados temporalmente mediante mocks.
* Backend agregado en carpeta independiente.
* Integración final entre frontend y backend mediante API Gateway.
* Despliegue final en AWS Academy / Amplify.

---

## Objetivo académico y profesional

Este proyecto fue desarrollado como parte de un trabajo académico de Desarrollo para Entornos Web, pero también está estructurado como una solución demostrable para portafolio profesional.

El sistema evidencia habilidades en:

* Desarrollo frontend con Angular.
* Diseño de interfaces modernas y responsivas.
* Modelado de procesos de negocio.
* Separación entre frontend y backend.
* Preparación para integración cloud.
* Gestión de datos mediante servicios y modelos.
* Uso de Git y GitHub para control de versiones.

---

## Autor

Desarrollado por **Fabián Sebastián** - **Alisson Ayala** estión de requerimientos, reclutamiento y formación de personal en un entorno de contact center.

