import pytest

from batterway.datamodel.generic.product import BoM, Product, ProductInstance, Quantity
import tests.unit_test.utils_common as UC

# Define the battery cell and battery
cell_nmc_333 = Product(
    name="cell_type",
    iri="cell_type.com",
    reference_quantity=Quantity(1.0, UC.kg),
    bom=BoM({UC.nickel: Quantity(0.3, UC.kg), UC.manganese: Quantity(0.3, UC.kg), UC.cobalt: Quantity(0.4, UC.kg)})
)
leave_no_bom_product = Product(
    name="cell_type",
    iri="cell_type.com",
    reference_quantity=Quantity(1.0, UC.kg)
)
battery_nmc_333 = Product(
    name="battery_type",
    iri="battery_type.com",
    reference_quantity=Quantity(1.1, UC.kg),
    bom=BoM(
        {
            cell_nmc_333: Quantity(0.8, UC.kg),
            UC.manganese: Quantity(0.1, UC.kg),
            UC.steel: Quantity(0.1, UC.kg),
            leave_no_bom_product: Quantity(0.1, UC.kg)
        }
    )
)

# Create a ProductInstance for testing
battery_instance = ProductInstance(battery_nmc_333, Quantity(10.0, UC.kg))


def test_product_bom() -> None:
    """Test the get_final_bom method for Product."""
    final_bom = battery_nmc_333.get_final_bom()

    # Expected BoM for the battery_nmc_333
    expected_bom = {
        UC.nickel: Quantity(0.24, UC.kg),
        UC.manganese: Quantity(0.34, UC.kg),
        UC.cobalt: Quantity(0.32, UC.kg),
        UC.steel: Quantity(0.1, UC.kg)
    }

    # Check if the BoM is correct
    for material, quantity in expected_bom.items():
        assert material in final_bom.product_quantities
        assert final_bom.product_quantities[material].value == pytest.approx(quantity.value)


def test_product_instance_bom() -> None:
    """Test the get_final_bom method for ProductInstance."""
    final_bom = battery_instance.get_final_bom()
    print(final_bom)
    # Expected BoM for the battery instance (multiplied by 10)
    expected_bom = {
        UC.nickel: Quantity(2.4, UC.kg),
        UC.manganese: Quantity(3.4, UC.kg),
        UC.cobalt: Quantity(3.2, UC.kg),
        UC.steel: Quantity(1.0, UC.kg)
    }

    # Check if the BoM is correct
    for material, quantity in expected_bom.items():
        assert material in final_bom.product_quantities
        assert final_bom.product_quantities[material].value == pytest.approx(quantity.value)
