import pytest
from grimp.adaptors.graph import ImportGraph
from importlinter.application.app_config import settings
from importlinter.contracts.layers import LayersContract
from importlinter.domain.contract import ContractCheck
from importlinter.domain.helpers import MissingImport

from tests.adapters.graph import FakeGraph
from tests.adapters.printing import FakePrinter


@pytest.mark.parametrize(
    "shortest_chains, is_kept",
    (
        (
            {
                ("high.green", "medium.orange"): ("high.green", "medium.orange"),
                ("high.green", "low.white.gamma"): ("high.green", "low.white.gamma"),
                ("medium.orange", "low.white"): ("medium.orange", "low.white"),
            },
            True,
        ),
        ({("medium.orange", "high.green"): ("medium.orange", "high.green")}, False),
        (
            {("low.white.gamma", "high.yellow.alpha"): ("low.white.gamma", "high.yellow.alpha")},
            False,
        ),
        ({("low.white.gamma", "medium.red"): ("low.white.gamma", "medium.red")}, False),
    ),
)
def test_layer_contract_single_containers(shortest_chains, is_kept):
    graph = FakeGraph(
        root_package_name="mypackage",
        descendants={
            "high": {"green", "blue", "yellow", "yellow.alpha"},
            "medium": {"orange", "red", "orange.beta"},
            "low": {"black", "white", "white.gamma"},
        },
        all_modules=[
            "mypackage",
            "mypackage.high",
            "mypackage.high.green",
            "mypackage.high.blue",
            "mypackage.high.yellow",
            "mypackage.high.yellow.alpha",
            "mypackage.medium",
            "mypackage.medium.orange",
            "mypackage.medium.orange.beta",
            "mypackage.medium.red",
            "mypackage.low",
            "mypackage.low.black",
            "mypackage.low.white",
            "mypackage.low.white.gamma",
        ],
        shortest_chains=shortest_chains,
    )

    contract = LayersContract(
        name="Layer contract",
        session_options={"root_package": "mypackage"},
        contract_options={"containers": ["mypackage"], "layers": ["high", "medium", "low"]},
    )

    contract_check = contract.check(graph=graph)

    assert contract_check.kept == is_kept


@pytest.mark.parametrize(
    "shortest_chains, is_kept",
    (
        (
            {
                ("one.high.green", "one.medium.orange"): ("one.high.green", "one.medium.orange"),
                ("one.high.green", "one.low.white.gamma"): (
                    "one.high.green",
                    "one.low.white.gamma",
                ),
                ("one.medium.orange", "one.low.white"): ("one.medium.orange", "one.low.white"),
                ("two.high.red.alpha", "two.medium.green.beta"): (
                    "two.high.red.alpha",
                    "two.medium.green.beta",
                ),
                ("two.high.red.alpha", "two.low.blue.gamma"): (
                    "two.high.red.alpha",
                    "two.low.blue.gamma",
                ),
                ("two.medium.green.beta", "two.low.blue.gamma"): (
                    "two.medium.green.beta",
                    "two.low.blue.gamma",
                ),
                ("three.high.white", "three.medium.purple"): (
                    "three.high.white",
                    "three.medium.purple",
                ),
                ("three.high.white", "three.low.cyan"): ("three.high.white", "three.low.cyan"),
                ("three.medium.purple", "three.low.cyan"): (
                    "three.medium.purple",
                    "three.low.cyan",
                ),
            },
            True,
        ),
        (
            {
                ("two.medium.green.beta", "one.high.green"): (
                    "two.medium.green.beta",
                    "one.high.green",
                )
            },
            True,
        ),
        (
            {("three.low.cyan", "two.high.red.alpha"): ("three.low.cyan", "two.high.red.alpha")},
            True,
        ),
        (
            {
                ("two.medium.green.beta", "two.high.red.alpha"): (
                    "two.medium.green.beta",
                    "two.high.red.alpha",
                )
            },
            False,
        ),
    ),
)
def test_layer_contract_multiple_containers(shortest_chains, is_kept):
    graph = FakeGraph(
        root_package_name="mypackage",
        descendants={
            "one.high": {"green", "blue", "yellow", "yellow.alpha"},
            "one.medium": {"orange", "red", "orange.beta"},
            "one.low": {"black", "white", "white.gamma"},
            "two.high": {"red", "red.alpha"},
            "two.medium": {"green", "green.beta"},
            "two.low": {"blue", "blue.gamma"},
            "three.high": {"white"},
            "three.medium": {"purple"},
            "three.low": {"cyan"},
        },
        all_modules=[
            "mypackage",
            "mypackage.one",
            "mypackage.one.high",
            "mypackage.one.high.green",
            "mypackage.one.high.blue",
            "mypackage.one.high.yellow",
            "mypackage.one.high.yellow.alpha",
            "mypackage.one.medium",
            "mypackage.one.medium.orange",
            "mypackage.one.medium.orange.beta",
            "mypackage.one.medium.red",
            "mypackage.one.low",
            "mypackage.one.low.black",
            "mypackage.one.low.white",
            "mypackage.one.low.white.gamma",
            "mypackage.two",
            "mypackage.two.high",
            "mypackage.two.high.red",
            "mypackage.two.high.red.alpha",
            "mypackage.two.medium",
            "mypackage.two.medium.green",
            "mypackage.two.medium.green.beta",
            "mypackage.two.low",
            "mypackage.two.low.blue",
            "mypackage.two.low.blue.gamma",
            "mypackage.three",
            "mypackage.three.high",
            "mypackage.three.high.white",
            "mypackage.three.medium",
            "mypackage.three.medium.purple",
            "mypackage.three.low",
            "mypackage.three.low.cyan",
        ],
        shortest_chains=shortest_chains,
    )

    contract = LayersContract(
        name="Layer contract",
        session_options={"root_package": "mypackage"},
        contract_options={
            "containers": ["mypackage.one", "mypackage.two", "mypackage.three"],
            "layers": ["high", "medium", "low"],
        },
    )

    contract_check = contract.check(graph=graph)

    assert contract_check.kept == is_kept


def test_layer_contract_populates_metadata():
    graph = FakeGraph(
        root_package_name="mypackage",
        descendants={
            "high": {"green", "blue", "yellow", "yellow.alpha"},
            "medium": {"orange", "red", "orange.beta"},
            "low": {"black", "white", "white.gamma"},
        },
        all_modules=[
            "mypackage",
            "mypackage.high",
            "mypackage.high.green",
            "mypackage.high.blue",
            "mypackage.high.yellow",
            "mypackage.high.yellow.alpha",
            "mypackage.medium",
            "mypackage.medium.orange",
            "mypackage.medium.orange.beta",
            "mypackage.medium.red",
            "mypackage.low",
            "mypackage.low.black",
            "mypackage.low.white",
            "mypackage.low.white.gamma",
        ],
        shortest_chains={
            ("low.white.gamma", "high.yellow.alpha"): (
                "low.white.gamma",
                "utils.foo",
                "utils.bar",
                "high.yellow.alpha",
            ),
            ("medium.orange.beta", "high.blue"): ("medium.orange.beta", "high.blue"),
            ("low.black", "medium.red"): ("low.black", "utils.baz", "medium.red"),
        },
        import_details=[
            {
                "importer": "mypackage.low.white.gamma",
                "imported": "mypackage.utils.foo",
                "line_number": 3,
                "line_contents": "",
            },
            {
                "importer": "mypackage.utils.foo",
                "imported": "mypackage.utils.bar",
                "line_number": 1,
                "line_contents": "",
            },
            {
                "importer": "mypackage.utils.foo",
                "imported": "mypackage.utils.bar",
                "line_number": 101,
                "line_contents": "",
            },
            {
                "importer": "mypackage.utils.bar",
                "imported": "mypackage.high.yellow.alpha",
                "line_number": 13,
                "line_contents": "",
            },
            {
                "importer": "mypackage.medium.orange.beta",
                "imported": "mypackage.high.blue",
                "line_number": 2,
                "line_contents": "",
            },
            {
                "importer": "mypackage.low.black",
                "imported": "mypackage.utils.baz",
                "line_number": 2,
                "line_contents": "",
            },
            {
                "importer": "mypackage.utils.baz",
                "imported": "mypackage.medium.red",
                "line_number": 3,
                "line_contents": "",
            },
        ],
    )

    contract = LayersContract(
        name="Layer contract",
        session_options={"root_package": "mypackage"},
        contract_options={"containers": ["mypackage"], "layers": ["high", "medium", "low"]},
    )

    contract_check = contract.check(graph=graph)

    assert contract_check.kept is False

    assert contract_check.metadata == {
        "invalid_chains": [
            {
                "higher_layer": "mypackage.high",
                "lower_layer": "mypackage.medium",
                "chains": [
                    [
                        {
                            "importer": "mypackage.medium.orange.beta",
                            "imported": "mypackage.high.blue",
                            "line_numbers": (2,),
                        }
                    ]
                ],
            },
            {
                "higher_layer": "mypackage.high",
                "lower_layer": "mypackage.low",
                "chains": [
                    [
                        {
                            "importer": "mypackage.low.white.gamma",
                            "imported": "mypackage.utils.foo",
                            "line_numbers": (3,),
                        },
                        {
                            "importer": "mypackage.utils.foo",
                            "imported": "mypackage.utils.bar",
                            "line_numbers": (1, 101),
                        },
                        {
                            "importer": "mypackage.utils.bar",
                            "imported": "mypackage.high.yellow.alpha",
                            "line_numbers": (13,),
                        },
                    ]
                ],
            },
            {
                "higher_layer": "mypackage.medium",
                "lower_layer": "mypackage.low",
                "chains": [
                    [
                        {
                            "importer": "mypackage.low.black",
                            "imported": "mypackage.utils.baz",
                            "line_numbers": (2,),
                        },
                        {
                            "importer": "mypackage.utils.baz",
                            "imported": "mypackage.medium.red",
                            "line_numbers": (3,),
                        },
                    ]
                ],
            },
        ]
    }


@pytest.mark.parametrize(
    "ignore_imports, invalid_chain",
    (
        (
            # Ignore from each chain - should be valid.
            [
                "mypackage.utils.baz -> mypackage.medium.orange",
                "mypackage.low.white.gamma -> mypackage.utils.foo",
            ],
            None,
        ),
        (
            # Ignore only one chain - should return the other.
            ["mypackage.low.white.gamma -> mypackage.utils.foo"],
            ["low.black", "utils.baz", "medium.orange"],
        ),
        (
            # Multiple ignore from same path - should allow it.
            [
                "mypackage.low.white.gamma -> mypackage.utils.foo",
                "mypackage.utils.bar -> mypackage.high.yellow.alpha",
            ],
            ["low.black", "utils.baz", "medium.orange"],
        ),
        (
            # Ignore from nonexistent module - should error.
            ["mypackage.nonexistent.foo -> mypackage.utils.foo"],
            MissingImport(),
        ),
        (
            # Ignore from nonexistent module - should error.
            ["mypackage.utils.foo -> mypackage.nonexistent.foo"],
            MissingImport(),
        ),
    ),
)
def test_ignore_imports(ignore_imports, invalid_chain):
    graph = FakeGraph(
        root_package_name="mypackage",
        descendants={
            "high": {"green", "blue", "yellow", "yellow.alpha"},
            "medium": {"orange"},
            "low": {"black", "white", "white.gamma"},
        },
        all_modules=[
            "mypackage",
            "mypackage.high",
            "mypackage.high.green",
            "mypackage.high.blue",
            "mypackage.high.yellow",
            "mypackage.high.yellow.alpha",
            "mypackage.medium",
            "mypackage.medium.orange",
            "mypackage.medium.orange.beta",
            "mypackage.medium.red",
            "mypackage.low",
            "mypackage.low.black",
            "mypackage.low.white",
            "mypackage.low.white.gamma",
        ],
        shortest_chains={
            ("low.white.gamma", "high.yellow.alpha"): (
                "low.white.gamma",
                "utils.foo",
                "utils.bar",
                "high.yellow.alpha",
            ),
            ("low.black", "medium.orange"): ("low.black", "utils.baz", "medium.orange"),
        },
        import_details=[
            {
                "importer": "mypackage.utils.baz",
                "imported": "mypackage.medium.orange",
                "line_number": 1,
                "line_contents": "-",
            },
            {
                "importer": "mypackage.low.white.gamma",
                "imported": "mypackage.utils.foo",
                "line_number": 1,
                "line_contents": "-",
            },
            {
                "importer": "mypackage.utils.bar",
                "imported": "mypackage.high.yellow.alpha",
                "line_number": 1,
                "line_contents": "-",
            },
        ],
    )

    contract = LayersContract(
        name="Layer contract",
        session_options={"root_package": "mypackage"},
        contract_options={
            "containers": ["mypackage"],
            "layers": ["high", "medium", "low"],
            "ignore_imports": ignore_imports,
        },
    )

    if isinstance(invalid_chain, Exception):
        with pytest.raises(invalid_chain.__class__):
            contract.check(graph=graph)
        return
    else:
        contract_check = contract.check(graph=graph)

    if invalid_chain:
        assert False is contract_check.kept
        assert len(contract_check.metadata["invalid_chains"]) == 1
        chains_metadata = contract_check.metadata["invalid_chains"][0]
        assert len(chains_metadata["chains"]) == 1
        chain_metadata = chains_metadata["chains"][0]
        actual_chain = [chain_metadata[0]["importer"]]
        for direct_import in chain_metadata:
            actual_chain.append(direct_import["imported"])
        package = graph.root_package_name
        assert [f"{package}.{n}" for n in invalid_chain] == actual_chain
    else:
        assert True is contract_check.kept


@pytest.mark.parametrize(
    "include_parentheses, should_raise_exception", ((False, True), (True, False))
)
def test_optional_layers(include_parentheses, should_raise_exception):
    graph = ImportGraph()
    for module in (
        "mypackage",
        "mypackage.foo",
        "mypackage.foo.high",
        "mypackage.foo.high.blue",
        "mypackage.foo.low",
        "mypackage.foo.low.alpha",
    ):
        graph.add_module(module)

    contract = LayersContract(
        name="Layer contract",
        session_options={"root_package": "mypackage"},
        contract_options={
            "containers": ["mypackage.foo"],
            "layers": ["high", "(medium)" if include_parentheses else "medium", "low"],
        },
    )

    if should_raise_exception:
        with pytest.raises(
            ValueError,
            match=(
                "Missing layer in container 'mypackage.foo': "
                "module mypackage.foo.medium does not exist."
            ),
        ):
            contract.check(graph=graph)
    else:
        contract.check(graph=graph)


def test_render_broken_contract():
    settings.configure(PRINTER=FakePrinter())
    contract = LayersContract(
        name="Layers contract",
        session_options={"root_package": "mypackage"},
        contract_options={"containers": ["mypackage"], "layers": ["high", "medium", "low"]},
    )
    check = ContractCheck(
        kept=False,
        metadata={
            "invalid_chains": [
                {
                    "higher_layer": "mypackage.high",
                    "lower_layer": "mypackage.low",
                    "chains": [
                        [
                            {
                                "importer": "mypackage.low.blue",
                                "imported": "mypackage.utils.red",
                                "line_numbers": (8, 16),
                            },
                            {
                                "importer": "mypackage.utils.red",
                                "imported": "mypackage.utils.yellow",
                                "line_numbers": (1,),
                            },
                            {
                                "importer": "mypackage.utils.yellow",
                                "imported": "mypackage.high.green",
                                "line_numbers": (3,),
                            },
                        ],
                        [
                            {
                                "importer": "mypackage.low.purple",
                                "imported": "mypackage.high.brown",
                                "line_numbers": (9,),
                            }
                        ],
                    ],
                },
                {
                    "higher_layer": "mypackage.medium",
                    "lower_layer": "mypackage.low",
                    "chains": [
                        [
                            {
                                "importer": "mypackage.low.blue",
                                "imported": "mypackage.medium.yellow",
                                "line_numbers": (6,),
                            }
                        ]
                    ],
                },
                {
                    "higher_layer": "mypackage.high",
                    "lower_layer": "mypackage.medium",
                    "chains": [
                        [
                            {
                                "importer": "mypackage.medium",
                                "imported": "mypackage.high.cyan.alpha",
                                "line_numbers": (2,),
                            }
                        ]
                    ],
                },
            ]
        },
    )

    contract.render_broken_contract(check)

    settings.PRINTER.pop_and_assert(
        """
        mypackage.low is not allowed to import mypackage.high:

        -   mypackage.low.blue -> mypackage.utils.red (l.8, l.16)
            mypackage.utils.red -> mypackage.utils.yellow (l.1)
            mypackage.utils.yellow -> mypackage.high.green (l.3)

        -   mypackage.low.purple -> mypackage.high.brown (l.9)


        mypackage.low is not allowed to import mypackage.medium:

        -   mypackage.low.blue -> mypackage.medium.yellow (l.6)


        mypackage.medium is not allowed to import mypackage.high:

        -   mypackage.medium -> mypackage.high.cyan.alpha (l.2)


        """
    )


@pytest.mark.parametrize(
    "container",
    (
        "notingraph",
        "notingraph.foo",
        "notinpackage",  # In graph, but not in package.
        "notinpackage.foo",
        "notinpackage.foo.one",
        "mypackagebeginscorrectly",
    ),
)
def test_invalid_container(container):
    graph = ImportGraph()
    for module in (
        "mypackage",
        "mypackage.foo",
        "mypackage.foo.high",
        "mypackage.foo.medium",
        "mypackage.foo.low",
        "notinpackage",
        "mypackagebeginscorrectly",
    ):
        graph.add_module(module)

    contract = LayersContract(
        name="Layer contract",
        session_options={"root_package": "mypackage"},
        contract_options={
            "containers": ["mypackage.foo", container],
            "layers": ["high", "medium", "low"],
        },
    )

    with pytest.raises(
        ValueError,
        match=(
            f"Invalid container '{container}': a container must either be a subpackage of "
            "mypackage, or mypackage itself."
        ),
    ):
        contract.check(graph=graph)
