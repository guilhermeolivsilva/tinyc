"""Implement Nodes to be used in the Abstract Syntax Tree."""

from typing import Union

class Node:

    """
    Implement a Node for the AST.

    Parameters
    ----------
    id : int
        The ID of the Node.
    kind : str
        The Node kind.
    value : int or None, optional (default = None)
        The value the Node holds, if any. Defaults to None.
    """

    def __init__(self, id: int, kind: str, value: Union[int, None] = None) -> None:
        self.id: int = id
        self.kind: str = kind
        self.value: Union[int, None] = value
        self.parent: Node = None
        self.children: list[Node] = []
        self.position_in_tree: Union[int, None] = None

    def __eq__(self, other: "Node") -> bool:
        """
        Implement the equality comparison between Nodes.

        Notice that this method ignores the `parent` and `children` attributes.

        Parameters
        ----------
        other : Node
            The right hand side Node of the comparison.

        Returns
        -------
        is_equal : bool
            `True` if all the attributes are equal, `False` otherwise.
        """

        is_equal = (
            self.id == other.id
            and self.kind == other.kind
            and self.value == other.value
        )

        return is_equal

    def __str__(self) -> str:
        """
        Implement a string representation of a Node object.

        This method is internally invoked when using `print(node_obj)`.

        Returns
        -------
        _str : str
            The string representation of a Node object.
        """
        _str = f"ID: {self.id}, Kind: {self.kind}, Value: {self.value}"

        if self.parent:
            _str += f", Parent ID: {self.parent.id}"

        if self.position_in_tree is not None:
            _str += f", Position in Tree: {self.position_in_tree}"

        return _str
    
    def set_position_in_tree(self, position_in_tree: int) -> None:
        """
        Set the `position_in_tree` of the Node.

        Parameters
        ----------
        position_in_tree : int
            The new `position_in_tree` to set.
        """

        self.position_in_tree = position_in_tree
    
    def set_kind(self, kind: str) -> None:
        """
        Set the `kind` of the Node.

        Parameters
        ----------
        kind : str
            The new `kind` to set.
        """

        self.kind = kind

    def get_kind(self) -> str:
        """
        Get the `kind` of the Node.

        Returns
        -------
        kind : str
            The `kind` of this node.
        """

        return self.kind

    def add_child(self, child: "Node") -> None:
        """
        Add a Node to the `self.children` list.

        Parameters
        ----------
        child : Node
            The Node to be added.
        """
        self.children.append(child)

    def remove_child(self, child_node: "Node") -> None:
        """
        Remove the `child_node` from the the `self.children` list.

        Parameters
        ----------
        child_node : Node
            The Node to remove.
        """

        if child_node in self.children:
            self.children.remove(child_node)
            child_node.parent = None

    def remove_from_tree(self) -> None:
        """Remove itself from the tree."""

        if self.parent:
            self.parent.remove_child(self)

    def merge(self, merge_target: 'Node', attribute_absortion: dict = {}) -> None:
        """
        Merge the `merge_target` to `self`.

        In this merger, the `merge_target`'s children becomes children of
        `self`, and the `merge_target` is removed from the tree. If
        `absorb_value` is set to `True`, then `self.value` is set to
        `merge_target.value`.

        Parameters
        ----------
        merge_target : Node
            The `Node` to be merged with `self`.
        attribute_absortion : dict
            TODO
        """

        absorb_value = attribute_absortion.get("absorb_value", False)

        if absorb_value:
            self.value = merge_target.value

        for child in merge_target.children:
            child.add_parent(self)

        parent_children_first = attribute_absortion.get(
            "parent_children_first",
            True
        )

        if parent_children_first:
            self.children.extend(merge_target.children)
        else:
            self.children = [*merge_target.children, *self.children]

        merge_target.remove_from_tree()

    def add_parent(self, parent: "Node") -> None:
        """
        Set a Node as this object's parent.

        Parameters
        ----------
        parent : Node
            A Node object to be set as the parent of `this`.
        """
        self.parent = parent
