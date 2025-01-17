import os
import typing

import pytest
from emmet.core.symmetry import CrystalSystem

from mp_api.client.routes.materials.materials import MaterialsRester


@pytest.fixture
def rester():
    rester = MaterialsRester()
    yield rester
    rester.session.close()


excluded_params = [
    "sort_fields",
    "chunk_size",
    "num_chunks",
    "all_fields",
    "fields",
    "exclude_elements",  # temp until server timeout increase
    "num_elements",  # temp until server timeout increase
    "num_sites",  # temp until server timeout increase
    "density",  # temp until server timeout increase
]

sub_doc_fields = []  # type: list

alt_name_dict = {
    "material_ids": "material_id",
    "formula": "material_id",
    "crystal_system": "symmetry",
    "spacegroup_number": "symmetry",
    "spacegroup_symbol": "symmetry",
    "exclude_elements": "material_id",
    "num_elements": "nelements",
    "num_sites": "nsites",
}  # type: dict

custom_field_tests = {
    "material_ids": ["mp-149"],
    "formula": "Si",
    "chemsys": "Si-O",
    "elements": ["Si", "O"],
    "task_ids": ["mp-149"],
    "crystal_system": CrystalSystem.cubic,
    "spacegroup_number": 38,
    "spacegroup_symbol": "Amm2",
}  # type: dict


@pytest.mark.skipif(
    os.environ.get("MP_API_KEY", None) is None, reason="No API key found."
)
def test_client(rester):
    search_method = rester.search

    if search_method is not None:
        # Get list of parameters
        param_tuples = list(typing.get_type_hints(search_method).items())

        # Query API for each numeric and boolean parameter and check if returned
        for entry in param_tuples:
            param = entry[0]
            if param not in excluded_params:
                param_type = entry[1].__args__[0]
                q = None

                if param_type == typing.Tuple[int, int]:
                    project_field = alt_name_dict.get(param, None)
                    q = {
                        param: (-10, 10),
                        "chunk_size": 1,
                        "num_chunks": 1,
                    }
                elif param_type == typing.Tuple[float, float]:
                    project_field = alt_name_dict.get(param, None)
                    q = {
                        param: (-10.12, 10.12),
                        "chunk_size": 1,
                        "num_chunks": 1,
                    }
                elif param_type is bool:
                    project_field = alt_name_dict.get(param, None)
                    q = {
                        param: False,
                        "chunk_size": 1,
                        "num_chunks": 1,
                    }
                elif param in custom_field_tests:
                    project_field = alt_name_dict.get(param, None)
                    q = {
                        param: custom_field_tests[param],
                        "chunk_size": 1,
                        "num_chunks": 1,
                    }

                doc = search_method(**q)[0].dict()

                for sub_field in sub_doc_fields:
                    if sub_field in doc:
                        doc = doc[sub_field]

                assert (
                    doc[project_field if project_field is not None else param]
                    is not None
                )
