FROM apache/airflow:2.10.4

# Installer des bibliothèques supplémentaires
RUN pip install psycopg2-binary pandas prometheus_client

# Copier les DAGs et plugins
COPY ./dags /opt/airflow/dags
COPY ./plugins /opt/airflow/plugins

# Configurer les permissions
USER root
RUN chmod -R 755 /opt/airflow/dags /opt/airflow/plugins
USER airflow