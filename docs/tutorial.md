# Tutorial Paso a Paso

Este tutorial muestra de forma resumida cómo iniciar un proyecto con **Genesis Engine**.

1. Ejecuta el comando de ayuda para conocer las opciones disponibles:
   ```bash
   genesis help
   ```
2. Crea una aplicación SaaS básica utilizando el template incluido:
   ```bash
   genesis init my-saas-app \
     --template=saas-basic
   ```
3. Inicia los servicios en modo desarrollo:
   ```bash
   cd my-saas-app
   docker-compose up -d
   ```
4. Accede a `http://localhost:3000` para el frontend y `http://localhost:8000/docs` para la API.

Consulta el resto de la documentación para detalles avanzados.
