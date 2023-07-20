from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel, BaseSettings, validator

from dataherald.utils.encrypt import FernetEncrypt


class SSHSettings(BaseSettings):
    load_dotenv()

    host: str | None
    username: str | None
    password: str | None

    remote_host: str | None
    remote_db_name: str | None
    remote_db_password: str | None
    private_key_path: str | None
    private_key_password: str | None
    db_driver: str | None

    @validator(
        "password", "remote_db_password", "private_key_password", pre=True, always=True
    )
    def encrypt(cls, value: str):
        fernet_encrypt = FernetEncrypt()
        try:
            fernet_encrypt.decrypt(value)
            return value
        except Exception:
            return fernet_encrypt.encrypt(value)

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


class DatabaseConnection(BaseModel):
    load_dotenv()
    alias: str
    use_ssh: bool
    uri: str | None
    ssh_settings: SSHSettings | None = None

    @validator("uri", pre=True, always=True)
    def set_uri_without_ssh(cls, v, values):
        if values["use_ssh"] and v:
            raise ValueError("When use_ssh is True don't set uri")
        if not values["use_ssh"] and not v:
            raise ValueError("When use_ssh is False set uri")
        return v

    @validator("uri", pre=True, always=True)
    def encrypt(cls, value: str):
        fernet_encrypt = FernetEncrypt()
        try:
            fernet_encrypt.decrypt(value)
            return value
        except Exception:
            return fernet_encrypt.encrypt(value)


class ForeignKeyDetail(BaseModel):
    field_name: str
    reference_table: str


class ColumnDetail(BaseModel):
    name: str
    is_primary_key: bool = False
    data_type: str = "str"
    description: str | None
    low_cardinality: bool = False
    categories: list[str] | None
    foreign_key: ForeignKeyDetail | None


class TableSchemaDetail(BaseModel):
    db_alias: str
    table_name: str
    description: str | None
    table_schema: str | None
    columns: list[ColumnDetail]
    examples: list = []


def get_mock_table_schema_detail() -> TableSchemaDetail:
    period_start = ColumnDetail(
        name="period_start",
        is_primary_key=False,
        data_type="date",
        description="Period when it starts, the date format is YYYY-MM-dd",
        low_cardinality=False,
    )
    period_end = ColumnDetail(
        name="period_end",
        is_primary_key=False,
        data_type="date",
        description="Period when it ends, the date format is YYYY-MM-dd",
        low_cardinality=False,
    )
    period_type = ColumnDetail(
        name="period_type",
        is_primary_key=False,
        data_type="str",
        description="Period type",
        low_cardinality=True,
        categories=[
            "monthly",
            "quarterly",
        ],
    )
    geo_type = ColumnDetail(
        name="geo_type",
        is_primary_key=False,
        data_type="str",
        description="Geo type",
        low_cardinality=True,
        categories=[
            "city",
            "county",
            "national",
            "state",
            "zip",
        ],
    )
    property_type = ColumnDetail(
        name="property_type",
        is_primary_key=False,
        data_type="str",
        description="Property type",
        low_cardinality=True,
        categories=[
            "All Residential",
            "Condo/Co-op",
            "Multi-family",
            "Single-family",
            "Single unit",
            "Townhouse",
        ],
    )
    location_name = ColumnDetail(
        name="location_name",
        is_primary_key=False,
        data_type="str",
        description="Location",
        low_cardinality=False,
    )
    dh_state_name = ColumnDetail(
        name="dh_state_name",
        is_primary_key=False,
        data_type="str",
        description="American state name",
        low_cardinality=True,
        categories=[
            "Alabama",
            "Alaska",
            "Arizona",
            "Arkansas",
            "California",
            "Colorado",
            "Connecticut",
            "Delaware",
            "District of Columbia",
            "Florida",
            "Georgia",
            "Hawaii",
            "Idaho",
            "Illinois",
            "Indiana",
            "Iowa",
            "Kansas",
            "Kentucky",
            "Louisiana",
            "Maine",
            "Maryland",
            "Massachusetts",
            "Michigan",
            "Minnesota",
            "Mississippi",
            "Missouri",
            "Montana",
            "Nebraska",
            "Nevada",
            "New Hampshire",
            "New Jersey",
            "New Mexico",
            "New York",
            "North Carolina",
            "Ohio",
            "Oklahoma",
            "Oregon",
            "Pennsylvania",
            "Rhode Island",
            "South Carolina",
            "South Dakota",
            "Tennessee",
            "Texas",
            "Utah",
            "Vermont",
            "Virginia",
            "Washington",
            "West Virginia",
            "Wisconsin",
        ],
    )
    dh_county_name = ColumnDetail(
        name="dh_county_name",
        is_primary_key=False,
        data_type="str",
        description="County name",
        low_cardinality=False,
    )
    dh_city_name = ColumnDetail(
        name="dh_city_name",
        is_primary_key=False,
        data_type="str",
        description="City name",
        low_cardinality=False,
    )
    metric_value = ColumnDetail(
        name="metric_value",
        is_primary_key=False,
        data_type="float",
        description="Number of listing houses",
        low_cardinality=False,
    )
    return TableSchemaDetail(
        db_alias="v2_real_estate",
        table_name="redfin_new_listings",
        description="List the number of houses sold in a period of time",
        table_schema="""
        CREATE TABLE public.redfin_new_listings (
            period_start date NOT NULL,
            period_end date NOT NULL,
            period_type text NOT NULL,
            geo_type text NOT NULL,
            property_type text NOT NULL,
            location_name text NOT NULL,
            dh_state_fips text NOT NULL,
            dh_state_name text NOT NULL,
            dh_state_abbr bpchar(2) NOT NULL,
            dh_county_fips text NOT NULL,
            dh_county_name text NOT NULL,
            dh_county_fullname text NOT NULL,
            dh_place_fips text NOT NULL,
            dh_place_name text NOT NULL,
            dh_place_fullname text NOT NULL,
            dh_city_name text NOT NULL,
            dh_city_fullname text NOT NULL,
            dh_zip_code text NOT NULL,
            is_seasonally_adjusted bool NOT NULL,
            metric_value float8 NULL,
            hg_date_updated timestamp NULL DEFAULT timezone('utc'::text, now()),
            CONSTRAINT redfin_new_listings_temp_pkey PRIMARY KEY (period_start,period_end,property_type,
            location_name,dh_state_fips,dh_county_fips,dh_place_fips,dh_zip_code,is_seasonally_adjusted)
        );
        """,
        columns=[
            period_start,
            period_end,
            period_type,
            geo_type,
            property_type,
            location_name,
            dh_state_name,
            dh_county_name,
            dh_city_name,
            metric_value,
        ],
        examples=[
            {
                "period_start": "2016-02-01",
                "period_end": "2016-02-29",
                "period_type": "monthly",
                "geo_type": "city",
                "property_type": "Single-family",
                "location_name": "Loves Park",
                "dh_state_fips": "17",
                "dh_state_name": "Illinois",
                "dh_state_abbr": "IL",
                "dh_county_fips": "007",
                "dh_county_name": "Boone",
                "dh_county_fullname": "Boone County",
                "dh_place_fips": "45031",
                "dh_place_name": "Loves Park",
                "dh_place_fullname": "Loves Park city",
                "dh_city_name": "Loves Park",
                "dh_city_fullname": "Loves Park city",
                "dh_zip_code": "-",
                "is_seasonally_adjusted": "false",
                "metric_value": "7.0",
                "hg_date_updated": "2023-05-02 09:44:43.946",
            }
        ],
    )
