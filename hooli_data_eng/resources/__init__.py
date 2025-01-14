import os

from dagster import EnvVar, FilesystemIOManager, ResourceDefinition
from dagster._utils import file_relative_path
from dagster_aws.s3 import ConfigurablePickledObjectS3IOManager, S3Resource
from dagster_dbt import DbtCliClientResource
from dagster_duckdb_pandas import DuckDBPandasIOManager
from dagster_pyspark import pyspark_resource
from dagster_snowflake_pandas import SnowflakePandasIOManager
from dagstermill import ConfigurableLocalOutputNotebookIOManager

from hooli_data_eng.resources.api import RawDataAPI
from hooli_data_eng.resources.databricks import db_step_launcher
from hooli_data_eng.resources.dbt import DbtCli2 as DbtCli
#from hooli_data_eng.resources.warehouse import MySnowflakeIOManager as SnowflakePandasIOManager
from hooli_data_eng.resources.sensor_file_managers import s3FileSystem, LocalFileSystem
from hooli_data_eng.resources.sensor_smtp import LocalEmailAlert, SESEmailAlert


# Resources represent external systems and, and specifically IO Managers
# tell dagster where our assets should be materialized. In dagster
# resources are separate from logical code to make it possible
# to develop locally, run tests, and run integration tests
#
# This project is designed for everything to run locally
# using the file system and DuckDB as the primary development resources
#
# PRs use a "branch" environment that mirrors production with
# staging Snowflake and S3 resources
#
# The production deployment on Dagster Cloud uses production Snowflake
# and S3 resources

def get_env():
    if os.getenv("DAGSTER_CLOUD_IS_BRANCH_DEPLOYMENT", "") == "1":
        return "BRANCH"
    if os.getenv("DAGSTER_CLOUD_DEPLOYMENT_NAME", "") == "data-eng-prod":
        return "PROD"
    return "LOCAL"


# The dbt file dbt_project/config/profiles.yaml
# specifies what databases to targets, and locally will
# execute against a DuckDB

DBT_PROJECT_DIR = file_relative_path(__file__, "../../dbt_project")
DBT_PROFILES_DIR = file_relative_path(__file__, "../../dbt_project/config")

# Similar to having different dbt targets, here we create the resource
# configuration by environment

resource_def = {
    "LOCAL": {
        "io_manager": DuckDBPandasIOManager(
            database=os.path.join(DBT_PROJECT_DIR, "example.duckdb")
        ),
        "model_io_manager": FilesystemIOManager(),
        "output_notebook_io_manager": ConfigurableLocalOutputNotebookIOManager(),
        "api": RawDataAPI.configure_at_launch(),
        "s3": ResourceDefinition.none_resource(),
        "dbt": DbtCliClientResource(
            project_dir=DBT_PROJECT_DIR, profiles_dir=DBT_PROFILES_DIR, target="LOCAL"
        ),
        "dbt2": DbtCli(project_dir=DBT_PROJECT_DIR, profiles_dir=DBT_PROFILES_DIR, target="LOCAL"),
        "pyspark": pyspark_resource,
        "step_launcher": ResourceDefinition.none_resource(),
        "monitor_fs": LocalFileSystem(base_dir=file_relative_path(__file__, ".")),
        "email": LocalEmailAlert(
            smtp_email_to=["data@awesome.com"], smtp_email_from="no-reply@awesome.com"
        ),
    },
    "BRANCH": {
        "io_manager": SnowflakePandasIOManager(
            database="DEMO_DB2_BRANCH",
            account=EnvVar("SNOWFLAKE_ACCOUNT"),
            user=EnvVar("SNOWFLAKE_USER"),
            password=EnvVar("SNOWFLAKE_PASSWORD"),
            warehouse="TINY_WAREHOUSE",
        ),
        "model_io_manager": ConfigurablePickledObjectS3IOManager(
            s3_bucket="hooli-demo-branch",
            s3_resource=S3Resource(region_name="us-west-2"),
        ),
        "output_notebook_io_manager": ConfigurableLocalOutputNotebookIOManager(),
        "api": RawDataAPI.configure_at_launch(),
        "dbt": DbtCliClientResource(
            project_dir=DBT_PROJECT_DIR, profiles_dir=DBT_PROFILES_DIR, target="BRANCH"
        ),
        "dbt2": DbtCli(project_dir=DBT_PROJECT_DIR, profiles_dir=DBT_PROFILES_DIR, target="BRANCH"),
        "pyspark": pyspark_resource,
        "step_launcher": db_step_launcher,
        "monitor_fs": s3FileSystem(
            region_name="us-west-2", s3_bucket="hooli-demo-branch"
        ),
        "email": ResourceDefinition.none_resource(),
    },
    "PROD": {
        "io_manager": SnowflakePandasIOManager(
            database="DEMO_DB2",
            account=EnvVar("SNOWFLAKE_ACCOUNT"),
            user=EnvVar("SNOWFLAKE_USER"),
            password=EnvVar("SNOWFLAKE_PASSWORD"),
            warehouse="TINY_WAREHOUSE",
        ),
        "model_io_manager": ConfigurablePickledObjectS3IOManager(
            s3_bucket="hooli-demo-branch",
            s3_resource=S3Resource(region_name="us-west-2"),
        ),
        "output_notebook_io_manager": ConfigurableLocalOutputNotebookIOManager(),
        "api": RawDataAPI.configure_at_launch(),
        "dbt": DbtCliClientResource(
            project_dir=DBT_PROJECT_DIR, profiles_dir=DBT_PROFILES_DIR, target="PROD"
        ),
        "dbt2": DbtCli(project_dir=DBT_PROJECT_DIR, profiles_dir=DBT_PROFILES_DIR, target="PROD"),
        "pyspark": pyspark_resource,
        "step_launcher": db_step_launcher,
        "monitor_fs": s3FileSystem(region_name="us-west-2", s3_bucket="hooli-demo"),
        "email": SESEmailAlert(
            smtp_host="email-smtp.us-west-2.amazonaws.com",
            smtp_email_from="lopp@elementl.com",
            smtp_email_to=["lopp@elementl.com"],
            smtp_username=EnvVar("SMTP_USERNAME"),
            smtp_password=EnvVar("SMTP_PASSWORD"),
        ),
    },
}