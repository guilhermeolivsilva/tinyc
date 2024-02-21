"""Implement a virtual machine that computes generated code."""

from src.node import Node


class VirtualMachine:
    """
    Virtual Machine that computes instructions from the `CodeGenerator`.

    Parameters
    ----------
    code_collection : list
        List of tuples generated by the `CodeGenerator`.
    """

    def __init__(self, code_collection: list, stack_size: int) -> None:
        halt_instruction = ("HALT", None)
        if halt_instruction not in code_collection:
            code_collection.append(halt_instruction)

        self.variables = { i: 0 for i in range(0, 26) }
        self.stack = [None for _ in range(0, stack_size)]
        self.code_collection = code_collection
        self.stack_pointer = 0
        self.program_counter = 0

    def run(self) -> None:
        """Run the program on the virtual machine."""

        while True:
            instruction, node = self.code_collection[self.program_counter]

            self.program_counter += 1

            if instruction == "HALT":
                break

            instruction_handler = getattr(self, instruction.lower())
            instruction_handler(node)

    def ifetch(self, node: Node) -> None:
        """Fetch the contents of a variable and push it to the stack."""

        self.stack[self.stack_pointer] = self.variables[node.value]
        self.stack_pointer += 1

    def istore(self, node: Node) -> None:
        """Store the (n-1)th element of the stack in a variable."""

        self.variables[node.value] = self.stack[self.stack_pointer - 1]
        self.stack_pointer -= 1

    def iadd(self, **kwargs) -> None:
        """Add the contents of the (n-1)th and (n-2)th elements of the stack."""

        self.stack[self.stack_pointer - 2] += self.stack[self.stack_pointer - 1]
        self.stack_pointer -= 1

    def isub(self, **kwargs) -> None:
        """Subtract the contents of the (n-1)th and (n-2)th elements of the stack."""

        self.stack[self.stack_pointer - 2] -= self.stack[self.stack_pointer - 1]
        self.stack_pointer -= 1
