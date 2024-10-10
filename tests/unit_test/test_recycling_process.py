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
        input_products,
        output_products,
        "recyclin_test",
    )
    r_p.set_influencing_input_process(relative_input_influenced)
    r_p.set_influencing_output_process(relative_output_influences)
    r_p.update_flow()


test_recycling_process_relative_lci()
