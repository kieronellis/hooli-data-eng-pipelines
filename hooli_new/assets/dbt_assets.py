from typing import Any, Mapping
from dagster._utils import file_relative_path
from dagster_dbt import DbtCliResource, KeyPrefixDagsterDbtTranslator
from dagster_dbt import (
    load_assets_from_dbt_project,
    default_metadata_from_dbt_resource_props,
)
from dagster_dbt.asset_decorator import dbt_assets
from dagster import (
    AssetKey,
    DailyPartitionsDefinition,
    WeeklyPartitionsDefinition,
    OpExecutionContext,
    Output,
    MetadataValue,
    BackfillPolicy,
)
from dateutil import parser
import json
import textwrap
from pathlib import Path


DBT_PROJECT_DIR = file_relative_path(__file__, "../../dbt_project")
DBT_PROFILES_DIR = file_relative_path(__file__, "../../dbt_project/config")


DBT_MANIFEST = Path(
    file_relative_path(__file__, "../../dbt_project/target/manifest.json")
)


class CustomDagsterDbtTranslator(KeyPrefixDagsterDbtTranslator):
    def get_metadata(self, dbt_resource_props: Mapping[str, Any]) -> Mapping[str, Any]:
        return {"dbt_metadata": MetadataValue.json(dbt_resource_props.get("meta", {}))}


dbt_views = load_assets_from_dbt_project(
    DBT_PROJECT_DIR,
    DBT_PROFILES_DIR,
    # key_prefix=["ANALYTICS"],
    # source_key_prefix="ANALYTICS",
    select="tag:bi",
    # node_info_to_group_fn=lambda x: "ANALYTICS",
    dagster_dbt_translator=CustomDagsterDbtTranslator(
        asset_key_prefix=["ANALYTICS"],
        source_asset_key_prefix="ANALYTICS",
    ),
)
