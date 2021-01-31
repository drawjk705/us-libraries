from typing import Any, Dict, ItemsView, KeysView, Union, ValuesView


class Variables:
    def __init__(self, **kwargs: Union[str, "Variables"]) -> None:
        self.__dict__.update(kwargs)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Variables":
        variables = Variables()
        for k, v in d.items():
            if isinstance(v, dict):
                variables[k] = Variables.from_dict(v)
            else:
                variables[k] = v

        return variables

    def items(self) -> ItemsView[str, Union[str, "Variables"]]:
        return self.__dict__.items()

    def keys(self) -> KeysView[str]:
        return self.__dict__.keys()

    def values(self) -> ValuesView[Union[str, "Variables"]]:
        return self.__dict__.values()

    def flatten(self, val_prefix: str = "") -> Dict[str, str]:
        """
        Flattens the variable dictionary for renaming pandas
        DataFrame columns:

        >>> v = Variables(First=Variables(Second=Variables(CODE_1="Value1", CODE_2="Value2)))
        >>> v.flatten()
        { 'CODE_1': 'First_Second_Value1, 'CODE_2': 'First_Second_Value2' }
        """

        flattened_dict: Dict[str, str] = {}

        for k, v in self.items():
            # in this case, the key is the original variable name
            if isinstance(v, str):
                # in this case, we haven't renamed the variable; so don't give
                # it a fancy name
                if k == v:
                    flattened_dict[k] = k
                else:
                    flattened_dict[k] = val_prefix + v
                continue

            flattened_dict.update(v.flatten(val_prefix=f"{val_prefix}{k}_"))

        return flattened_dict

    def invert(self, val_prefix: str = "") -> "Variables":
        """
        "Inverts" itself, so that variable names will now point to
        their new column names:

        >>> v = Variables(First=Variables(Second=Variables(CODE="Value")))
        >>> v_inverted = v.invert()
        >>> v.First.Second.Value
        First_Second_Value
        """

        inverted = Variables()

        for k, v in self.items():
            # in this case, the key is the original variable name
            if isinstance(v, str):
                if k == v:
                    # in this case, we haven't renamed the variable; so don't give
                    # it a fancy name
                    inverted[v] = k
                else:
                    inverted[v] = val_prefix + v
                continue

            inverted[k] = v.invert(val_prefix=f"{val_prefix}{k}_")

        return inverted

    def __setitem__(self, k: str, v: Union[str, "Variables"]) -> None:
        setattr(self, k, v)

    def __repr__(self) -> str:
        return self.__dict__.__repr__()

    def __str__(self) -> str:
        return self.__repr__()

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Variables):
            return False

        if len(o.items()) != len(self.items()):
            return False

        for k, v in self.items():
            if v != getattr(o, k, None):
                return False

        return True
