from dagster_databricks import databricks_pyspark_step_launcher
from pathlib import Path

cluster_config = {
    "size": {
        "num_workers": 1
    },
    "spark_version": "11.2.x-scala2.12",
    "nodes": {
        "node_types": {
            "node_type_id": "i3.xlarge"
        }
    }
}

db_step_launcher = databricks_pyspark_step_launcher.configured({
    
        "run_config": {
            "run_name": "launch_step",
            "cluster": {"new": cluster_config},
            "libraries": [  
                {"pypi": {"package": "dagster-aws"}},
                {"pypi": {"package": "dagster-pandas"}},
                {"pypi": {"package": "dagster-dbt"}},
                {"pypi": {"package": "dagster-duckdb"}},
                {"pypi": {"package": "dagster-duckdb-pandas"}},
                {"pypi": {"package": "dbt-core"}},
                {"pypi": {"package": "dbt-snowflake"}},
                {"pypi": {"package": "dagster-cloud"}},
                {"pypi": {"package": "pandas>=1.4.0"}},
                {"pypi": {"package": "dagster-snowflake"}},
                {"pypi": {"package": "requests"}},
            ],
        },
        "databricks_host": {"env": "DATABRICKS_HOST"},
        "databricks_token": {"env": "DATABRICKS_TOKEN"},
        "local_pipeline_package_path": str(Path(__file__).parent.parent.parent),
        "secrets_to_env_variables": [
            {"name": "DATABRICKS_TOKEN", "key": "adls2_key", "scope": "dagster-test"},
            {"name": "SNOWFLAKE_USER", "key": "snowflake_user", "scope": "dagster-test"},
            {"name": "SNOWFLAKE_PASSWORD", "key": "snowflake_password", "scope": "dagster-test"},
            {"name": "SNOWFLAKE_ACCOUNT", "key": "snowflake_account", "scope": "dagster-test"},
        ],
        "storage": {
            "s3": {
                "access_key_key": "access_key_key",
                "secret_key_key": "secret_key_key",
                "secret_scope": "dagster-test",
            }
        },
    }
)