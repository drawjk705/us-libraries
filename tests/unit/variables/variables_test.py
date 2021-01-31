from typing import Any, Dict, List, Union

import pytest

from us_pls._variables.fy2018 import (
    outlet_data_vars,
    state_summary_data_vars,
    system_data_vars,
)
from us_pls._variables.models import Variables


def get_expected_keys(_variables: Union[Variables, Dict[str, Any]]) -> List[str]:
    expected_keys = []

    for k, v in _variables.items():
        if isinstance(v, str):
            expected_keys.append(k)
        else:
            expected_keys += get_expected_keys(v)

    return expected_keys


@pytest.mark.parametrize(
    "variables",
    [
        outlet_data_vars.OUTLET_DATA_VARIABLES,
        state_summary_data_vars.STATE_SUMMARY_DATA_VARIABLES,
        system_data_vars.SYSTEM_DATA_VARIABLES,
    ],
)
def test_variable_flatten_and_reorient_do_not_swallow_keys(variables: Variables):
    flattened_vars = variables.flatten_and_invert()
    reoriented_vars = variables.reorient()

    actual_keys = get_expected_keys(flattened_vars)
    expected_keys = get_expected_keys(variables)

    assert actual_keys == expected_keys
    assert len(actual_keys) == len(get_expected_keys(reoriented_vars))


@pytest.mark.parametrize(
    "variables",
    [
        outlet_data_vars.OUTLET_DATA_VARIABLES,
        state_summary_data_vars.STATE_SUMMARY_DATA_VARIABLES,
        system_data_vars.SYSTEM_DATA_VARIABLES,
    ],
)
def test_to_dict_flatten(variables: Variables):
    flattened_dict = variables.reorient().to_dict(flatten=True)

    assert len(flattened_dict.keys()) == len(get_expected_keys(variables))


def test_to_dict_without_imputation_flags():
    variables = Variables(
        Category1=Variables(Var1="Val1", F_Var1="Val1_ImputationFlag"),
        Category2=Variables(Var1="Val1", F_Var1="Val1_ImputationFlag"),
        Category3=Variables(
            SubCategory1=Variables(Var1="Val1", F_Var1="Val1_ImputationFlag")
        ),
    )

    as_dict = variables.reorient().to_dict(with_imputation_flags=False)
    as_flat_dict = variables.reorient().to_dict(
        flatten=True, with_imputation_flags=False
    )

    assert as_dict == {
        "Category1": {"Val1": "Category1_Val1"},
        "Category2": {"Val1": "Category2_Val1"},
        "Category3": {"SubCategory1": {"Val1": "Category3_SubCategory1_Val1"}},
    }
    assert as_flat_dict == {
        "Category1_Val1": "Category1_Val1",
        "Category2_Val1": "Category2_Val1",
        "Category3_SubCategory1_Val1": "Category3_SubCategory1_Val1",
    }


def test_to_dict_from_dict():
    variables = Variables(
        A0=Variables(B0="A0_B0"), A1=Variables(B1=Variables(C1="A1_B1_C1"))
    )

    assert variables.to_dict() == dict(
        A0=dict(B0="A0_B0"), A1=dict(B1=dict(C1="A1_B1_C1"))
    )
    assert Variables.from_dict(variables.to_dict()) == variables
