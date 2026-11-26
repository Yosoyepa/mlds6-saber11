# Datos

Esta carpeta no se versiona en Git. Su contenido se genera con el script de carga:

```bash
python scripts/data_acquisition/main.py
```

| Ruta | Contenido |
| --- | --- |
| `raw/saber11_20224_d7.csv` | Datos crudos del recorte del proyecto, tal como los entrega la API de datos.gov.co |
| `raw/saber11_20224_d7.meta.json` | Consulta, fecha de descarga y huella SHA-256 del archivo anterior |

La fuente, el recorte y el proceso de carga están descritos en [`docs/data/data_definition.md`](../docs/data/data_definition.md).
