
from dagster import (
    Definitions,
    load_assets_from_modules,
    load_assets_from_package_module,
    multiprocess_executor,
)
from dagster_dbt import DbtCliResource
import os
from hooli_new.assets import dbt_assets


# ---------------------------------------------------
# Assets

# Dagster assets specify what outputs we care about and
# the logical code needed to create them

# Our first set of assets represent raw data, and the asset
# definitions can be seen in /assets/raw_data/__init__.py
#
# These raw datasets will be used by dbt as dbt sources
# which can be found in dbt_project/models/sources.yml


# Our second set of assets represent dbt models
# these models are defined in the dbt_project
# folder
#
# The dbt file dbt_project/config/profiles.yaml
# specifies what databases to targets, and locally will
# execute against a DuckDB

dbt_assets = load_assets_from_modules([dbt_assets])

# Our final set of assets represent Python code that
# should run after dbt. These assets are defined in
# assets/forecasting/__init__.py


from dagster._utils import file_relative_path
DBT_PROJECT_DIR = file_relative_path(__file__, "../dbt_project")




# ---------------------------------------------------
# Definitions

# Definitions are the collection of assets, jobs, schedules, resources, and sensors
# used with a project. Dagster Cloud deployments can contain mulitple projects.

defs = Definitions(
    assets=[*dbt_assets],
    resources={
        "dbt": DbtCliResource(project_dir=os.fspath(DBT_PROJECT_DIR)),
    },
)
