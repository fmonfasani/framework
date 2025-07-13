# Despliegue en Producción

Genesis Engine permite desplegar las aplicaciones generadas en distintos entornos.

## Despliegue Local

```bash
genesis deploy --local --prod
```

## Despliegue en Cloud

```bash
# Ejemplo para AWS
genesis deploy --cloud=aws --region=us-east-1
```

Consulta las opciones avanzadas en `genesis deploy --help` para adaptar el despliegue a tu infraestructura.
