from batterway.datamodel.generic.product import BoM, Product, ProductInstance, Quantity, Unit


class ProcessLCI:
    """Container of ratios between input and output products of a process."""

    def __init__(
        self,
        name: str,
        input_relative_lci: dict[tuple[Product, Product], float],
        output_relative_lci: dict[tuple[Product, Product], float],
    ):
        self.name: str = name
        self.input_relative_lci: dict[tuple[Product, Product], float] = input_relative_lci
        self.output_relative_lci: dict[tuple[Product, Product], float] = output_relative_lci

    def __str__(self):
        return f"{self.name} ({self.direction})" + "\n".join(
            [f"{k[0]} / {k[1]} : {v}" for k, v in self.relative_lci.items()]
        )


class Process:
    """A process in a supply chain, represented by its inputs and outputs."""

    def __init__(self, name: str, inputs_products: BoM, output_products: BoM):
        self.name: str = name
        self.inputs: BoM = inputs_products
        self.outputs: BoM = output_products

    def __str__(self):
        return f"{self.name} : \n" + "\n".join(map(str, self.inputs)) + "\n" + "\n".join(map(str, self.outputs))


class RecyclingProcess(Process):
    """A process in a supply chain, represented by its inputs and outputs, with additional information on the relative influence of the inputs on the outputs."""

    def __init__(
        self,
        name: str,
        inputs_products: BoM,
        output_products: BoM,
        ref_input_to_input: dict[tuple[Product, Product], float],
        ref_input_to_output: dict[tuple[Product, Product], float],
    ):
        super().__init__(name, inputs_products, output_products)
        self.ref_input_to_output_relation: dict[tuple[Product, Product], float] = ref_input_to_output
        self.ref_input_to_input_relation: dict[tuple[Product, Product], float] = ref_input_to_input
        self.computed_output_bom: BoM | None = None
        self.computed_input_bom: BoM | None = None
        self.__ensure_coherency()

    def __get_input_final_bom(self) -> BoM:
        return ProductInstance(Product(
            "dummy", "",
            Quantity(self.inputs.quantity_total, Unit("kg", "")),
            self.inputs
        ),
            Quantity(1.0, Unit("kg", "")
                     )
        ).get_final_bom() + self.inputs

    def __ensure_coherency(self) -> bool:
        input_final_bom = self.__get_input_final_bom()
        missing_input_influencing_input = [i_rel[0] for i_rel in self.ref_input_to_input_relation if i_rel[0] not in input_final_bom]
        missing_input_influencing_output = [i_rel[0] for i_rel in self.ref_input_to_output_relation if i_rel[0] not in input_final_bom]
        if len(missing_input_influencing_input):
            print([p.name for p in missing_input_influencing_input])
            err_msg = "Products influencing the input should be present in the input LCI."
            raise ValueError(err_msg)
        if any(missing_input_influencing_output):
            print([p.name for p in missing_input_influencing_input])
            err_msg = "Products influencing the output should be present in the input LCI."
            raise ValueError(err_msg)
        return True

    def __update_flow(self) -> None:
        final_bom = self.__get_input_final_bom()
        print("#" * 20)
        print("#" * 3 + "BOM FOR RELATIVE" + "#" * 3)
        print("#" * 20)
        print(final_bom)
        print("#" * 20)

        updated_in_flow_value = dict()
        updated_in_flow_value = {}
        for (product_influencing, product_influenced), ratio in self.ref_input_to_input_relation.items():
            if product_influencing in final_bom:
                if product_influenced not in updated_in_flow_value:
                    updated_in_flow_value[product_influenced] = ProductInstance(
                        product_influenced, Quantity(0, product_influenced.reference_quantity.unit)
                    )
                updated_in_flow_value[product_influenced] += (
                    final_bom.product_quantities[product_influencing].qty * ratio
                )
        for product_influenced in updated_in_flow_value:
            product_influenced.quantity = Quantity(
                updated_in_flow_value[product_influenced], product_influenced.reference_quantity.unit
            )

        updated_out_flow_value = {}
        for (product_influencing, product_influenced), ratio in self.ref_input_to_output_relation.items():
            if product_influencing in final_bom:
                if product_influenced not in updated_out_flow_value:
                    updated_out_flow_value[product_influenced] = ProductInstance(
                        product_influenced, Quantity(0, product_influenced.reference_quantity.unit)
                    )
                updated_out_flow_value[product_influenced] += (
                    final_bom.product_quantities[product_influencing].qty * ratio
                )

        for product_influenced in updated_out_flow_value:
            product_influenced.quantity = Quantity(
                updated_out_flow_value[product_influenced], product_influenced.reference_quantity.unit
            )

        self.computed_output_bom = BoM(updated_out_flow_value)
        self.computed_input_bom = BoM(updated_in_flow_value)

    def update_fixed_input_lci(self, products_qty: dict[str, float]) -> None:
        self.computed_output_bom = None
        self.computed_input_bom = None
        if not len(products_qty):
            raise ValueError("Empty inputs")
        for product in self.inputs.products:
            self.inputs.set_quantity_of_product(product.name, 0)

        for product, qty in products_qty.items():
            self.inputs.set_quantity_of_product(product, qty)
        print("#"*20)
        print("#"*3+"INPUTS"+"#"*3)
        print(self.inputs)

        self.__update_flow()
        print("#" * 20)
        print("#" * 3 + "UPDATED" + "#" * 3)
        print("#" * 3 + "FLOW" + "#" * 3)
        print("#" * 20)
        print("#" * 3 + "INPUT" + "#" * 3)
        print("#" * 3 + "FLOW" + "#" * 3)
        print(self.computed_input_bom)
        print("#" * 20)
        print("#" * 3 + "OUTPUT" + "#" * 3)
        print("#" * 3 + "FLOW" + "#" * 3)
        print(self.computed_output_bom)


    def __str__(self):
        return super().__str__()


class Route:
    """A sequence of processes in a supply chain."""

    def __init__(self, route_id: str, route_process_sequence: list[tuple[tuple[Product, Process]]]):
        self.route_id: str = route_id
        self.process_sequence = route_process_sequence

    def ensure_consistency(self) -> None:
        output_products = None
        previous_process = None
        for process in self.process_sequence:
            if output_products is not None:
                input_products = [f.product for f in process.inputs]
                if not any(p_output in input_products for p_output in output_products):
                    err_msg = f"No product produced by {previous_process} used by {process}"
                    raise ValueError(err_msg)
            output_products = [f.product for f in process.outputs]
            previous_process = process

    def __str__(self):
        return f"{self.route_id}" + ">=".join([p.name for p in self.process_sequence])


class RecyclingRoute:
    """A sequence of recycling processes in a supply chain."""

    def __init__(self, route_id: str, route_process_sequence: list[RecyclingProcess]):
        self.route_id: str = route_id
        self.process_sequence = route_process_sequence

    def ensure_consistency(self) -> None:
        output_products = None
        previous_process = None
        for process in self.process_sequence:
            if output_products is not None:
                input_products = [f.product for f in process.inputs]
                if not any(p_output in input_products for p_output in output_products):
                    err_msg = f"No product produced by {previous_process} used by {process}"
                    raise ValueError(err_msg)
                if process.ref_input not in input_products:
                    err_msg = f"Missing the reference input of {process} from {previous_process}"
                    raise ValueError(err_msg)
            output_products = [f.product for f in process.outputs]
            previous_process = process
