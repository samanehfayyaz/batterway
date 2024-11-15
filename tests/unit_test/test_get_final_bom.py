import pytest

import tests.unit_test.utils_common as uc
from batterway.datamodel.generic.product import BoM, Product, ProductInstance, Quantity

# Define the battery cell and battery
cell_nmc_333 = Product(
    name="cell_type",
    iri="cell_type.com",
    reference_quantity=Quantity(1.0, uc.kg),
    bom=BoM(
        {
            uc.nickel: ProductInstance(uc.nickel, Quantity(0.3, uc.kg)),
            uc.manganese: ProductInstance(uc.manganese, Quantity(0.3, uc.kg)),
            uc.cobalt: ProductInstance(uc.cobalt, Quantity(0.4, uc.kg)),
        }
    ),
)
leaf_no_bom_product = Product(name="cell_type", iri="cell_type.com", reference_quantity=Quantity(1.0, uc.kg))
battery_nmc_333 = Product(
    name="battery_type",
    iri="battery_type.com",
    reference_quantity=Quantity(1.1, uc.kg),
    bom=BoM(
        {
            cell_nmc_333: ProductInstance(cell_nmc_333, Quantity(0.8, uc.kg)),
            uc.manganese: ProductInstance(uc.manganese, Quantity(0.1, uc.kg)),
            uc.steel: ProductInstance(uc.steel, Quantity(0.1, uc.kg)),
            leaf_no_bom_product: ProductInstance(leaf_no_bom_product, Quantity(0.1, uc.kg)),
        }
    ),
)

# Create a ProductInstance for testing
battery_instance = ProductInstance(battery_nmc_333, Quantity(10.0, uc.kg))


def test_product_bom() -> None:
    """Test the get_final_bom method for Product."""
    final_bom = battery_nmc_333.get_final_bom()

    # Expected BoM for the battery_nmc_333
    expected_bom = {
        uc.nickel: Quantity(0.24, uc.kg),
        uc.manganese: Quantity(0.34, uc.kg),
        uc.cobalt: Quantity(0.32, uc.kg),
        uc.steel: Quantity(0.1, uc.kg),
    }

    # Check if the BoM is correct
    for material, quantity in expected_bom.items():
        assert material in final_bom.product_quantities
        print(quantity)
        print(final_bom.product_quantities[material])
        assert final_bom.product_quantities[material].qty.value == pytest.approx(quantity.value)


def test_product_instance_bom() -> None:
    """Test the get_final_bom method for ProductInstance."""
    final_bom = battery_instance.get_final_bom()
    print(final_bom)
    # Expected BoM for the battery instance (multiplied by 10)
    expected_bom = {
        uc.nickel: Quantity(2.4, uc.kg),
        uc.manganese: Quantity(3.4, uc.kg),
        uc.cobalt: Quantity(3.2, uc.kg),
        uc.steel: Quantity(1.0, uc.kg),
    }

    # Check if the BoM is correct
    for material, quantity in expected_bom.items():
        assert material in final_bom.product_quantities
        assert final_bom.product_quantities[material].qty.value == pytest.approx(quantity.value)


test_product_bom()
test_product_instance_bom()
