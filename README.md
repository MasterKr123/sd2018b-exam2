# sd2018b-exam2
Repository for the exam2

**Universidad ICESI**  
**Curso:** Sistemas Distribuidos  
**Docente:** Daniel Barragán C.  
**Tema:** Construcción de artefactos para entrega continua.  
**Correo:** jorgeeliecercastao@gmail.com
**Estudiante:** Jorge Eliecer Castaño Valencia  
**Codigo:** A00315284

### Objetivos
* Realizar de forma autómatica la generación de artefactos para entrega continua
* Emplear librerías de lenguajes de programación para la realización de tareas específicas
* Diagnosticar y ejecutar de forma autónoma las acciones necesarias para corregir fallos en
la infraestructura

### Objetivos
* Realizar de forma autómatica la generación de artefactos para entrega continua
* Emplear librerías de lenguajes de programación para la realización de tareas específicas
* Diagnosticar y ejecutar de forma autónoma las acciones necesarias para corregir fallos en
la infraestructura

### Tecnlogías sugeridas para el desarrollo del examen
* Vagrant
* Docker
* Box del sistema operativo CentOS7
* Repositorio Github
* Python3
* Librerias Python3: Flask, Connexion, Docker
* Ngrok

### Descripción
Para la realización de la actividad tener en cuenta lo siguiente:

* Crear un Fork del repositorio sd2018b-exam2 y adicionar las fuentes de un microservicio
de su elección.
* Alojar en su fork un archivo Dockerfile para la construcción de un artefacto tipo Docker a
partir de las fuentes de su microservicio.

Deberá probar y desplegar los siguientes componentes:

* Despliegue de un **registry** local de Docker para el almacenamiento de imágenes de Docker. Usar la imagen de DockerHub: https://hub.docker.com/_/registry/ . Probar que es posible descarga la imagen generada desde un equipo perteneciente a la red.

* Realizar un método en Python3.6 o superior que reciba como entrada el nombre de un servicio,
la version y el tipo (Docker ó AMI) y en su lógica realice la construcción de una imagen de Docker cuyo nombre deberá ser **service_name:version** y deberá ser publicada en el **registry** local creado en el punto anterior.

* Realizar una integración con GitHub para que al momento de realizar un **merge** a la rama
**develop**, se inicie la construcción de un artefacto tipo Docker a partir del Dockerfile y las fuentes del repositorio. Idee una estrategia para el envío del **service_name** y la **versión** a través del **webhook** de GitHub. La imagen generada deberá ser publicada en el **registry** local creado.

* Si la construcción es exitosa/fallida debera actualizarse un **badge** que contenga la palabra build y la versión del artefacto creado mas recientemente (**opcional**).

* En lugar de una máquina virtual de CentOS7 para alojar el CI server,  emplear la imagen de Docker de Docker hub para el ejecución de la API (webhook listener) y la generación del artefacto: https://hub.Docker.com/_/Docker/ (**opcional**).

### Actividades
1. Documento README.md en formato markdown:  
  * Formato markdown (5%)
  * Nombre y código del estudiante (5%)
  * Ortografía y redacción (5%)
2. Documentación del procedimiento para el montaje del registry (10%). Evidencias del funcionamiento (5%).
3. Documentación e implementación del método para la generación del artefacto. Incluya el código fuente en el informe. Incluya comentarios en el código donde explique cada paso realizado (20%). Evidencias del funcionamiento (5%).
4. Documentación e integración de un repositorio de GitHub junto con la generación del artefacto tipo Docker (20%). Evidencias del funcionamiento (5%).
5. El informe debe publicarse en un repositorio de github el cual debe ser un fork de https://github.com/ICESI-Training/sd2018b-exam2 y para la entrega deberá hacer un Pull Request (PR) al upstream (10%). Tenga en cuenta que el repositorio debe contener todos los archivos necesarios para el aprovisionamiento
6. Documente algunos de los problemas encontrados y las acciones efectuadas para su solución al aprovisionar la infraestructura y aplicaciones (10%)


## Desarrollo  

### 1. :heavy_check_mark:  

### 2. registry  
Para la realización del despliegue del registry se tomo como referencia el post "Create your own private docker registry on Linux" de la pagina Learnitguide. Esta guia provee los pasos para crear un docker registry local para administrar imagenes docker.

Los pasos son los siguientes:

#### 2.1 Crear un directorio y los certificados  
Para crear el directorio:
```
 mkdir -p /docker_data/certs/
```
Para generar los certificados que aseguran al docker registry se hace uso de ssl:
```
 openssl req -newkey rsa:4096 -nodes -sha256 -keyout `pwd`/docker_data/certs/domain.key -x509 -days 365 -out `pwd`/docker_data/certs/domain.crt
```
![][1]
**Figura 1**. Certificados generados.

#### 2.2 Crear el docker registry
Ejecutar el comando:
```
docker run -d \                                   
  --restart=always \
  --name registry \
  -v `pwd`/docker_data/certs:/certs \
  -e REGISTRY_HTTP_ADDR=0.0.0.0:443 \
  -e REGISTRY_HTTP_TLS_CERTIFICATE=/certs/domain.crt \
  -e REGISTRY_HTTP_TLS_KEY=/certs/domain.key \
  -p 443:443 \
  registry
```
![][2]
**Figura 2**. Creación registry.

#### 2.3 Descargar las imagenes de docker

Para descargar imagenes de docker ejecutamos el comando:
```
docker pull imagen
```
donde "imagen" es la imagen del repositorio de docker (ej: httpd).

Para verificar las imagenes descargadas de docker se ejecuta:
```
docker images
```
![][3]
**Figura 3**. Imagenes descargadas de docker.

#### 2.4 Subir las imagenes al registry
Primero, se debe renombrar las imagenes descargadas de docker para poder subirlas al docker registry por lo cual se ejecuta el comando:
```
docker tag imagen jorgeregistry/my-imagen
```
Donde:
* "imagen" corresponde a alguna de las imagenes listadas (ej: httpd).
* "jorgeregistry/my-imagen" corresponde al nuevo nombre (ej: my-imagen puede ser httpd).

Luego, se ejecuta el siguiente comando para subir la imagen:
```
docker push jorgeregistry/my-imagen
```
Donde "jorgeregistry/my-imagen" es la imagen renombrada anteriormente

#### 2.5 Configuración del cliente del docker REGISTRY_HTTP_ADDR
Para que el cliente pueda consumir recursos del nuevo docker registry, requiere del certificado generado en el punto 2.1 (domain.crt).

Una ves obtenga este certificado, mediante scp por ejemplo, se debe alojar en un directorio creado:
```
mkdir -p /etc/docker/certs.d/jorgeregistry:443/
cp -rf ~/domain.crt /etc/docker/certs.d/jorgeregistry:443/
```

### 3. Generación del artefacto
Para la creación del artefacto se crea un docker_compose definiendo el servicio de registry:
```
version: '3'
services:
    registry:
        image: registry:2
        restart: always
        container_name: registry
        volumes:
            - './docker_data/certs:/certs'
        environment:
            - 'REGISTRY_HTTP_ADDR=0.0.0.0:443'
            - REGISTRY_HTTP_TLS_CERTIFICATE=/certs/domain.crt
            - REGISTRY_HTTP_TLS_KEY=/certs/domain.key
        ports:
            - '443:443'
```
El archivo compose que define el servicio registry:
* Usa una imagen que es construida desde DockerHub (registry:2).
* Con volumes, monta el directorio del proyecto (directorio actual) en el host en ./docker_data/certs:/certs dentro del contenedor.
* Configura las variables de entorno del puerto y certificados en la ubicación de los volumenes exportados.
* Reenvía el puerto 443 expuesto en el contenedor al puerto 443 en la máquina host.

Para desplegar los servicios se ejecuta el comando:
```
docker-compose up
```
![][4]
**Figura 4**. Registry up.

### 4.Integración
Para la integraión, se creo un servidor CI (Continuous Integration) mediante tecnologia Docker.

```
FROM centos/python-36-centos7

RUN pip3.6 install connexion
RUN pip3.6 install fabric
COPY ./flask_endpoint /flask_endpoint
WORKDIR /flask_endpoint

RUN ./scripts/deploy.sh
```
Donde
* Se despliega una imagen de centos de docker con python3.
* Se instala las dependencia de connexion y fabric
* Se monta el endpoint en el host dentro del contenedor.
* Se ejecuta la aplicación flask del endpoint


### 5. :heavy_check_mark:


### 6. Dificultades
Para el aprovisionamiento de la infraestructura y aplicaciones se encontraron las siguientes dificultades:

* Permisos
Algunas ejecuciones requerian de permisos root, para solucionarlo supuse que el usuario distribuidos es el admin y le di los permisos correspondientes a su rol.


* Información sobre los temas  
A pesar de la ardua documentación que contiene Docker, la información necesaria fue dificil de encontrar. La acción tomada fue realizar una investigación e interpretación de los temas.





### Referencias
* https://hub.docker.com/_/registry/
* https://hub.docker.com/_/docker/
* https://docker-py.readthedocs.io/en/stable/index.html
* https://developer.github.com/v3/guides/building-a-ci-server/
* http://flask.pocoo.org/
* https://connexion.readthedocs.io/en/latest/  
* https://www.learnitguide.net/2018/07/create-your-own-private-docker-registry.html
* https://www.youtube.com/watch?v=SEpR35HZ_hQ
* https://docs.docker.com/compose/install/
* https://github.com/MasterKr123/sd2018b-exam1/tree/jcastano/sd2018b-exam1/cookbooks/ci/files/default

[1]: images/generateCertificates.png
[2]: images/createRegistry.png
[3]: images/dockerimages.png
[4]: registryup.png
