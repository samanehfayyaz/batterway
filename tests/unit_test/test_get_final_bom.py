import pytest
from batterway.datamodel.generic.Product import Product, Unit, Quantity, ProductInstance, BoM

# Define the Unit for kg
kg = Unit("kg", "kg_IRI")

# Define raw materials as Products
nickel = Product("nickel", "nickel.com", Quantity(1.0, kg))
manganese = Product("manganese", "manganese.com", Quantity(1.0, kg))
cobalt = Product("cobalt", "cobalt.com", Quantity(1.0, kg))
steel = Product("steel", "steel.com", Quantity(1.0, kg))

# Define the battery cell and battery
cell_nmc_333 = Product(
    name="cell_type",
    iri="cell_type.com",
    reference_quantity=Quantity(1.0, kg),
    bom=BoM({nickel: Quantity(0.3, kg), manganese: Quantity(0.3, kg), cobalt: Quantity(0.4, kg)})
)

battery_nmc_333 = Product(
    name="battery_type",
    iri="battery_type.com",
    reference_quantity=Quantity(1.0, kg),
    bom=BoM({cell_nmc_333: Quantity(0.8, kg), manganese: Quantity(0.1, kg), steel: Quantity(0.1, kg)})
)

# Create a ProductInstance for testing
battery_instance = ProductInstance(battery_nmc_333, Quantity(10.0, kg))


def test_product_bom():
    """Test the get_final_bom method for Product"""
    final_bom = battery_nmc_333.get_final_bom()

    # Expected BoM for the battery_nmc_333
    expected_bom = {
        nickel: Quantity(0.24, kg),
        manganese: Quantity(0.34, kg),
        cobalt: Quantity(0.32, kg),
        steel: Quantity(0.1, kg)
    }

    # Check if the BoM is correct
    for material, quantity in expected_bom.items():
        assert material in final_bom.product_quantities
        assert final_bom.product_quantities[material].value == pytest.approx(quantity.value)


def test_product_instance_bom():
    """Test the get_final_bom method for ProductInstance"""
    final_bom = battery_instance.get_final_bom()

    # Expected BoM for the battery instance (multiplied by 10)
    expected_bom = {
        nickel: Quantity(2.4, kg),
        manganese: Quantity(3.4, kg),
        cobalt: Quantity(3.2, kg),
        steel: Quantity(1.0, kg)
    }

    # Check if the BoM is correct
    for material, quantity in expected_bom.items():
        assert material in final_bom.product_quantities
        assert final_bom.product_quantities[material].value == pytest.approx(quantity.value)