import pytest
from mp_api.core.client import MPRestError
from mp_api.matproj import MPRester

key_only_resters = {
    "phonon": "mp-11703",
    "phonon_img": "mp-11703",
    "similarity": "mp-149",
    "doi": "mp-149",
    "wulff": "mp-149",
    "charge_density": "mp-1936745",
    "robocrys": "mp-149",
}

search_only_resters = ["grain_boundary", "bandstructure", "dos", "substrates", "synthesis"]

special_resters = ["phonon_img", "charge_density"]

mpr = MPRester()


@pytest.mark.parametrize("rester", mpr._all_resters)
def test_generic_get_methods(rester):
    name = rester.endpoint.split("/")[-2]
    if name not in key_only_resters:
        doc = rester.query({"limit": 1}, fields=[rester.primary_key])[0]
        assert isinstance(doc, rester.document_model)

        if name not in search_only_resters:
            doc = rester.get_document_by_id(doc.dict()[rester.primary_key], fields=[rester.primary_key])
            assert isinstance(doc, rester.document_model)

    elif name not in special_resters:
        doc = rester.get_document_by_id(key_only_resters[name], fields=[rester.primary_key])
        assert isinstance(doc, rester.document_model)
