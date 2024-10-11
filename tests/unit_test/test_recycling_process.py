import tests.unit_test.utils_common as UC
from batterway.datamodel.generic.process import RecyclingProcess
from batterway.datamodel.generic.product import BoM, ProductInstance, Quantity


def test_recycling_process_relative_lci():
    input_products = BoM(
        {
            UC.water: ProductInstance(UC.water, Quantity(1.0, UC.kg)),
            UC.nmc111: ProductInstance(UC.nmc111, Quantity(1.0, UC.kg)),
        }
    )

    relative_input_influenced = {(UC.water, UC.heat): Quantity(1.0, UC.kg)}

    output_products = BoM({})
    relative_output_influences = {(UC.water, UC.vapor): Quantity(3.0, UC.kg)}
    r_p = RecyclingProcess(
        "recycling_test", input_products, output_products, relative_input_influenced, relative_output_influences
    )
    r_p.update_fixed_input_lci({})


test_recycling_process_relative_lci()


def test_chocolate_recycling_process():
    input_products = BoM(
        {
            UC.cookie: ProductInstance(UC.cookie, Quantity(1.0, UC.kg)),
            UC.schwarze_kuchen: ProductInstance(UC.schwarze_kuchen, Quantity(1.0, UC.kg)),
            UC.brownie: ProductInstance(UC.brownie, Quantity(1.0, UC.kg)),
        }
    )
    output_products = BoM({})
    relative_input_influenced = {
        (UC.chocolate, UC.heat): Quantity(1.0, UC.kg),
        (UC.black_wheat, UC.heat): Quantity(10.0, UC.kg),
    }
    relative_output_influences = {
        (UC.water, UC.vapor): Quantity(1.0, UC.kg),
        (UC.water, UC.vapor): Quantity(1.0, UC.kg),
    }
    r_p = RecyclingProcess(
        "recyclin_test", input_products, output_products, relative_input_influenced, relative_output_influences
    )
