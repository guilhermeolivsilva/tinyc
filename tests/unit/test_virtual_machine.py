"""Implement unit tests for the `src.virtual_machine.VirtualMachine` class."""

# Just to annotate functions with fixtures.
from pytest_mock.plugin import MockerFixture

from src.node import Node
from src.virtual_machine import VirtualMachine


def test_init() -> None:
    """Test the instantiation of VirtualMachine objects."""

    code_collection = [("IFETCH", Node(id=1, kind="VAR", value=0))]
    stack_size = 10

    vm = VirtualMachine(code_collection=code_collection, stack_size=stack_size)

    assert len(vm.stack) == stack_size
    assert not any(vm.stack)
    assert all(code in vm.code_collection for code in code_collection)
    assert vm.stack_pointer == vm.program_counter == 0


def test_run() -> None:
    """
    Test the `VirtualMachine.run` method.
    
    This test is omitted because all of its possibilities are covered by the
    following `test_run_...` tests.
    """

    ...


def test_run_ifetch(mocker: MockerFixture) -> None:
    """Test `VirtualMachine.ifetch` through the `run` method."""

    test_value = 23
    test_node = Node(id=1, kind="VAR", value=0)

    vm = VirtualMachine(
        code_collection=[
            ("IFETCH", test_node),
            ("HALT", None)
        ],
        stack_size=1
    )
    vm.variables[0] = test_value

    vm.ifetch = mocker.spy(vm, "ifetch")
    vm.run()

    # Assert the method was called and the `stack` has the expected value
    vm.ifetch.assert_called_once_with(test_node)
    assert vm.stack == [test_value]


def test_run_ipush(mocker: MockerFixture) -> None:
    """Test `VirtualMachine.ipush` through the `run` method."""

    test_value = 23
    test_node = Node(id=1, kind="CST", value=test_value)

    vm = VirtualMachine(
        code_collection=[
            ("IPUSH", test_node),
            ("HALT", None)
        ],
        stack_size=1
    )

    vm.ipush = mocker.spy(vm, "ipush")
    vm.run()

    # Assert the method was called and the `stack` has the expected value
    vm.ipush.assert_called_once_with(test_node)
    assert vm.stack == [test_value]


def test_run_istore(mocker: MockerFixture) -> None:
    """Test `VirtualMachine.istore` through the `run` method."""

    test_value = 23
    test_node = Node(id=1, kind="VAR", value=0)

    vm = VirtualMachine(
        code_collection=[
            ("ISTORE", test_node),
            ("HALT", None)
        ],
        stack_size=1
    )

    vm.stack = [test_value]
    vm.istore = mocker.spy(vm, "istore")
    vm.run()

    # Assert the method was called and the `variables` has the expected value
    vm.istore.assert_called_once_with(test_node)
    assert vm.variables[0] == test_value


def test_run_ipop(mocker: MockerFixture) -> None:
    """Test `VirtualMachine.ipop` through the `run` method."""

    test_value = 23

    vm = VirtualMachine(
        code_collection=[
            ("IPOP", None),
            ("HALT", None)
        ],
        stack_size=1
    )

    # Mock the stack to only contain the `test_value`
    vm.stack.append(test_value)
    vm.stack_pointer = 1
    vm.ipop = mocker.spy(vm, "ipop")
    vm.run()

    # Assert the method was called and the `test_value` has been removed from
    # the stack
    vm.ipop.assert_called_once()
    assert vm.stack_pointer == 0
    assert test_value not in vm.stack


def test_run_iadd(mocker: MockerFixture) -> None:
    """Test `VirtualMachine.iadd` through the `run` method."""

    lhs_value = 23
    lhs = Node(id=1, kind="CST", value=lhs_value)

    rhs_value = 35
    rhs = Node(id=2, kind="CST", value=rhs_value)

    vm = VirtualMachine(
        code_collection=[
            ("IPUSH", lhs),
            ("IPUSH", rhs),
            ("IADD", None),
            ("HALT", None)
        ],
        stack_size=2
    )

    vm.iadd = mocker.spy(vm, "iadd")
    vm.run()

    vm.iadd.assert_called_once()
    assert vm.stack == [lhs_value + rhs_value, rhs_value]


def test_run_isub(mocker: MockerFixture) -> None:
    """Test `VirtualMachine.isub` through the `run` method."""

    lhs_value = 23
    lhs = Node(id=1, kind="CST", value=lhs_value)

    rhs_value = 35
    rhs = Node(id=2, kind="CST", value=rhs_value)

    vm = VirtualMachine(
        code_collection=[
            ("IPUSH", lhs),
            ("IPUSH", rhs),
            ("ISUB", None),
            ("HALT", None)
        ],
        stack_size=2
    )

    vm.isub = mocker.spy(vm, "isub")
    vm.run()

    vm.isub.assert_called_once()
    assert vm.stack == [lhs_value - rhs_value, rhs_value]


def test_run_ilt(mocker: MockerFixture) -> None:
    """Test `VirtualMachine.ilt` through the `run` method."""

    lhs_value = 23
    lhs = Node(id=1, kind="CST", value=lhs_value)

    rhs_value = 35
    rhs = Node(id=2, kind="CST", value=rhs_value)

    vm = VirtualMachine(
        code_collection=[
            ("IPUSH", lhs),
            ("IPUSH", rhs),
            ("ILT", None),
            ("HALT", None)
        ],
        stack_size=2
    )

    vm.ilt = mocker.spy(vm, "ilt")
    vm.run()

    vm.ilt.assert_called_once()
    assert vm.stack == [lhs_value < rhs_value, rhs_value]


def test_run_jmp(mocker: MockerFixture) -> None:
    """Test `VirtualMachine.jmp` through the `run` method."""

    node_to_run = Node(id=1, kind="CST", value=23)
    node_to_ignore = Node(id=2, kind="CST", value=35)
    another_node_to_run = Node(id=3, kind="CST", value=13)

    vm = VirtualMachine(
        code_collection=[
            ("IPUSH", node_to_run),
            ("JMP", another_node_to_run),
            ("IPUSH", node_to_ignore),
            ("IPUSH", another_node_to_run),
            ("HALT", None)
        ],
        stack_size=3
    )

    vm.jmp = mocker.spy(vm, "jmp")

    vm.run()

    vm.jmp.assert_called_once()
    assert vm.stack == [node_to_run.value, another_node_to_run.value, None]


def test_run_jz_true(mocker: MockerFixture) -> None:
    """
    Test `VirtualMachine.jz` through the `run` method.

    In this test, assert that the `jz` method correctly handles `True`
    conditions.
    """

    condition_node = Node(id=1, kind="CST", value=True)
    node_not_to_ignore = Node(id=2, kind="CST", value=35)
    another_node_to_run = Node(id=3, kind="CST", value=13)

    vm = VirtualMachine(
        code_collection = [
            ("IPUSH", condition_node),
            ("JZ", another_node_to_run),
            ("IPUSH", node_not_to_ignore),
            ("IPUSH", another_node_to_run),
            ("HALT", None)
        ],
        stack_size=3
    )

    vm.jz = mocker.spy(vm, "jz")

    vm.run()

    vm.jz.assert_called_once()

    assert vm.stack == [
        condition_node.value,
        node_not_to_ignore.value,
        another_node_to_run.value
    ]


def test_run_jz_false(mocker: MockerFixture) -> None:
    """
    Test `VirtualMachine.jz` through the `run` method.

    In this test, assert that the `jz` method correctly handles `False`
    conditions.
    """

    condition_node = Node(id=1, kind="CST", value=False)
    node_to_ignore = Node(id=2, kind="CST", value=35)
    another_node_to_run = Node(id=3, kind="CST", value=13)

    vm = VirtualMachine(
        code_collection = [
            ("IPUSH", condition_node),
            ("JZ", another_node_to_run),
            ("IPUSH", node_to_ignore),
            ("IPUSH", another_node_to_run),
            ("HALT", None)
        ],
        stack_size=3
    )

    vm.jz = mocker.spy(vm, "jz")

    vm.run()

    vm.jz.assert_called_once()    
    assert vm.stack == [
        condition_node.value,
        another_node_to_run.value,
        None
    ]


def test_run_jnz_true(mocker: MockerFixture) -> None:
    """
    Test `VirtualMachine.jnz` through the `run` method.

    In this test, assert that the `jnz` method correctly handles `True`
    conditions.
    """

    condition_node = Node(id=1, kind="CST", value=True)
    node_to_ignore = Node(id=2, kind="CST", value=35)
    another_node_to_run = Node(id=3, kind="CST", value=13)

    vm = VirtualMachine(
        code_collection = [
            ("IPUSH", condition_node),
            ("JNZ", another_node_to_run),
            ("IPUSH", node_to_ignore),
            ("IPUSH", another_node_to_run),
            ("HALT", None)
        ],
        stack_size=3
    )

    vm.jnz = mocker.spy(vm, "jnz")

    vm.run()

    vm.jnz.assert_called_once()    
    assert vm.stack == [
        condition_node.value,
        another_node_to_run.value,
        None
    ]


def test_run_jnz_false(mocker: MockerFixture) -> None:
    """
    Test `VirtualMachine.jnz` through the `run` method.

    In this test, assert that the `jnz` method correctly handles `False`
    conditions.
    """

    condition_node = Node(id=1, kind="CST", value=False)
    node_not_to_ignore = Node(id=2, kind="CST", value=35)
    another_node_to_run = Node(id=3, kind="CST", value=13)

    vm = VirtualMachine(
        code_collection = [
            ("IPUSH", condition_node),
            ("JNZ", another_node_to_run),
            ("IPUSH", node_not_to_ignore),
            ("IPUSH", another_node_to_run),
            ("HALT", None)
        ],
        stack_size=3
    )

    vm.jnz = mocker.spy(vm, "jnz")

    vm.run()

    vm.jnz.assert_called_once()

    assert vm.stack == [
        condition_node.value,
        node_not_to_ignore.value,
        another_node_to_run.value
    ]


def test_run_empty(mocker: MockerFixture) -> None:
    """Test `VirtualMachine.jnz` through the `run` method."""

    vm = VirtualMachine(
        code_collection=[
            ("EMPTY", Node(id=-1, kind="EMPTY")),
            ("HALT", None)
        ],
        stack_size=1
    )

    vm.empty = mocker.spy(vm, "empty")

    vm.run()

    vm.empty.assert_called_once()
    assert vm.stack == [None]

