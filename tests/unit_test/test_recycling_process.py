from batterway.datamodel.generic.process import RecyclingProcess
import tests.unit_test.utils_common as UC
from batterway.datamodel.generic.product import ProductInstance, Quantity


def test_recycling_process_relative_lci():
    input_products = [
        ProductInstance(UC.water,Quantity(1.0,UC.kg))
    ]
    relative_input_influenced = {(UC.water, UC.heat): Quantity(1.0, UC.kg)}

    output_products = []
    relative_output_influences = {
        (UC.water,UC.vapor): Quantity(3.0, UC.kg)
    }
    r_p = RecyclingProcess(
        input_products,
        output_products,
        "recyclin_test",
    )
    r_p.set_influencing_input_process(relative_input_influenced)
    r_p.set_influencing_output_process(relative_output_influences)
    r_p.update_flow()

test_recycling_process_relative_lci()