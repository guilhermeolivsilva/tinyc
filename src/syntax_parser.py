"""Implement a syntax parser to use with the AST."""

from .abstract_syntax_tree import Node


def uses_global_id(func: callable) -> callable:
    """
    Decorate a function to enable it to access the `global_id_manager`.

    The decorated function will increment the `global_id_manager` by 1 after
    being called.

    Parameters
    ----------
    func : function
        The function to be decorated.

    Returns
    -------
    wrapper : function
        The decorated function.
    """

    def wrapper(cls, *args, **kwargs) -> callable:
        """
        Wrap the function to be decorated.

        Returns
        -------
        result : object
            The result of the decorated function.
        """
        try:
            result = func(cls, *args, **kwargs)
        except Exception as e:
            print(f"ERROR: {e}")
            print("Could not run decorated function. The ID counter was not affected.")
        else:
            cls.global_id_manager += 1

        return result

    return wrapper


class SyntaxParser:
    """Syntax Parser that translates input text to AST nodes."""

    def __init__(self) -> None:
        self._global_id_manager: int = 1

    @property
    def global_id_manager(self) -> int:
        return self._global_id_manager

    @global_id_manager.setter
    def global_id_manager(self, value: int) -> None:
        self._global_id_manager = value

    @uses_global_id
    def term(
        self,
        symbol: str or list,
        value: int = None,
        lhs: Node = None,
        rhs: Node = None,
    ) -> Node:
        """
        Generate a `term` for the AST.

        Terms are either a variable, a constant, or a paranthesis expression.

        If a variable or a constant, then the `value` parameter must be set,
        and the `symbol` must be a single string. If a parenthesis expression,
        then the `symbol` parameter must be a `list` of `str`, and the `lhs`
        and `rhs` parameters must be set.

        Parameters
        ----------
        symbol : str or list of str
            The symbol to parse. If a `list`, creates a 
            `parenthesis_expression`. Check the docstring of the 
            `parenthesis_expression` method for more info.
        value : int
            The value to be stored in the Node.
        lhs : Node
            The Node that represents the left hand side term inside the
            parenthesis expression.
        rhs : Node
            The Node that represents the right hand side term inside the
            parenthesis expression.

        Returns
        -------
        term_node : Node
            The new `term` generated Node.
        """

        simple_term_condition = isinstance(symbol, str) and symbol is not None
        parenthesis_term_condition = (
            isinstance(symbol, list) and lhs is not None and rhs is not None
        )

        _err_msg = "Malformed method call."
        _err_msg += "Set either (symbol, value) or (symbol, lhs, rhs)"

        assert simple_term_condition ^ parenthesis_term_condition, _err_msg

        symbol_map = {
            "ID": Node(id=self.global_id_manager, kind="VAR", value=value),
            "INT": Node(id=self.global_id_manager, kind="CST", value=value),
        }

        try:
            term_node = symbol_map[symbol]
        except (KeyError, TypeError):
            term_node = self.parenthesis_expression(symbol, lhs, rhs)

        return term_node

    def parenthesis_expression(self, symbol: list, lhs: Node, rhs: Node) -> Node:
        """
        Generate a `parenthesis_expression` for the AST.

        Parameters
        ----------
        symbol : list
            A list of symbols to parse. Must be as it follows: ["LPAR",
            <symbol>, "RPAR"], where <symbol> is valid symbol from the lexer.
        lhs : Node
            The Node that represents the left hand side term inside the
            parenthesis expression.
        rhs : Node
            The Node that represents the right hand side term inside the
            parenthesis expression.

        Returns
        -------
        parenthesis_expression : Node
            The Node that represents the parenthesis expression.

        Raises
        ------
        AssertionError
            Raised if
            - there is no `LPAR` in the `symbol` list.
            - there is no `RPAR` in the `symbol` list.
            - the `RPAR` comes before the `LPAR` in the `symbol` list.
        """

        lpar, expression_symbol, rpar = symbol

        _err_par_symbol = "Missing or misplaced {} parenthesis symbol ({}PAR)"
        assert lpar == "LPAR", _err_par_symbol.format("left", "L")
        assert rpar == "RPAR", _err_par_symbol.format("right", "R")

        return self.expression(expression_symbol, lhs, rhs)

    @uses_global_id
    def expression(self, symbol: str, lhs: Node, rhs: Node) -> Node:
        """
        Generate a `expression` for the AST.

        A `expression` is a triplet of Nodes consisting of the left and right
        hand side terms, and the `expression` itself.

        Parameters
        ----------
        lhs : Node
            The Node that represents the left hand side term of the operation.
        rhs : Node
            The Node that represents the right hand side term of the operation.

        Returns
        -------
        expression_node : Node
            The new `expression` generated Node.
        """
        if symbol != "ID":
            return self.comparison(lhs=lhs, rhs=rhs)

        expression_node = Node(id=self.global_id_manager, kind="SET", value=-1)

        lhs.add_parent(expression_node)
        rhs.add_parent(expression_node)

        expression_node.add_child(lhs)
        expression_node.add_child(rhs)

        return expression_node

    @uses_global_id
    def sum(self, symbol: str, lhs: Node, rhs: Node) -> Node:
        """
        Generate a `sum` for the AST.

        A `sum` is a triplet of Nodes consisting of the left and right hand
        side terms, and the `sum_node` itself – it might be either an addition
        or a subtraction.

        Parameters
        ----------
        symbol : str
            The symbol to parse. If not "ID" or "INT", creates a
            `parenthesis_expression`.
        lhs : Node
            The Node that represents the left hand side term of the operation.
        rhs : Node
            The Node that represents the right hand side term of the operation.

        Returns
        -------
        sum_node : Node
            The new `sum` generated Node.
        """

        symbol_map = {
            "PLUS": Node(id=self.global_id_manager, kind="ADD", value=-1),
            "MINUS": Node(id=self.global_id_manager, kind="SUB", value=-1),
        }

        sum_node = symbol_map[symbol]

        lhs.add_parent(sum_node)
        rhs.add_parent(sum_node)

        sum_node.add_child(lhs)
        sum_node.add_child(rhs)

        return sum_node

    @uses_global_id
    def comparison(self, lhs: Node, rhs: Node) -> Node:
        """
        Generate a `comparison` for the AST.

        A `comparison` is a triplet of Nodes consisting of the left and right
        hand side terms, and the `comparison` itself.

        TinyC currently only supports the "less than" (`<`) comparison.

        Parameters
        ----------
        lhs : Node
            The Node that represents the left hand side term of the operation.
        rhs : Node
            The Node that represents the right hand side term of the operation.

        Returns
        -------
        comparison_node : Node
            The new `comparison` generated Node.
        """
        comparison_node = Node(id=self.global_id_manager, kind="LT", value=-1)

        lhs.add_parent(comparison_node)
        rhs.add_parent(comparison_node)

        comparison_node.add_child(lhs)
        comparison_node.add_child(rhs)

        return comparison_node
