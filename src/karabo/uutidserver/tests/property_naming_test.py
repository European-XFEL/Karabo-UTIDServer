from karabo.middlelayer.testing import check_device_package_properties

from .. import uutid_server


def test_property_code_guideline():
    """Test that all properties and slots follow common code style"""
    keys = check_device_package_properties(uutid_server)
    msg = ("The key naming does not comply with our coding guidelines. "
           f"Please have a look at (class: paths): {keys}")
    assert not keys, msg
