#Usar una imagen base de Python
FROM python:3.12-alpine

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /FormularioCurriculum

# Copiar el archivo de dependencias 
COPY requirements.txt ./

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de la aplicación al contenedor
COPY . ./

#comando para ejecutar la aplicación
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000","app:app"]

# Exponer el puerto 5000 para acceder a la aplicación
EXPOSE 8000