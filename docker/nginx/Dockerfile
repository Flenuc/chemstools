FROM nginx:alpine

# Eliminar la configuración por defecto de nginx
RUN rm /etc/nginx/conf.d/default.conf

# Copiar nuestra configuración personalizada
COPY nginx.conf /etc/nginx/nginx.conf

# Crear directorio para logs
RUN mkdir -p /var/log/nginx

# Exponer el puerto 80
EXPOSE 80

# Comando para iniciar nginx
CMD ["nginx", "-g", "daemon off;"]
