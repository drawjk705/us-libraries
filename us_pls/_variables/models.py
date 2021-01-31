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

    def to_dict(
        self, flatten: bool = False, with_imputation_flags: bool = True
    ) -> Dict[str, Any]:
        if not flatten:
            dict_res: Dict[str, Any] = {}

            for k, v in self.items():
                if k.endswith("_ImputationFlag") and not with_imputation_flags:
                    continue
                if isinstance(v, str):
                    dict_res[k] = v
                else:
                    dict_res[k] = v.to_dict(with_imputation_flags=with_imputation_flags)

            return dict_res
        else:
            return self.__to_flat_dict(with_imputation_flags=with_imputation_flags)

    def __to_flat_dict(self, with_imputation_flags: bool) -> Dict[str, str]:
        dict_res: Dict[str, str] = {}

        for v in self.values():
            if isinstance(v, str):
                if v.endswith("_ImputationFlag") and not with_imputation_flags:
                    continue
                dict_res[v] = v
            else:
                dict_res.update(
                    v.__to_flat_dict(with_imputation_flags=with_imputation_flags)
                )

        return dict_res

    def items(self) -> ItemsView[str, Union[str, "Variables"]]:
        return self.__dict__.items()

    def keys(self) -> KeysView[str]:
        return self.__dict__.keys()

    def values(self) -> ValuesView[Union[str, "Variables"]]:
        return self.__dict__.values()

    def flatten_and_invert(self, val_prefix: str = "") -> Dict[str, str]:
        """
        Flattens the variable dictionary for renaming pandas
        DataFrame columns:

        >>> v = Variables(First=Variables(Second=Variables(CODE_1="Value1", CODE_2="Value2)))
        >>> v
        { 'First': { 'Second': { 'CODE_1': 'Value1', 'CODE_2': 'Value2 } } }
        >>> v.flatten()
        { 'CODE_1': 'First_Second_Value1, 'CODE_2': 'First_Second_Value2' }
        """

        flattened_dict: Dict[str, str] = {}

        for k, v in self.items():
            if isinstance(v, str):
                # in this case, we haven't renamed the variable; so don't give
                # it a fancy name
                if k == v:
                    flattened_dict[k] = k
                else:
                    flattened_dict[k] = val_prefix + v
            else:
                flattened_dict.update(
                    v.flatten_and_invert(val_prefix=f"{val_prefix}{k}_")
                )

        return flattened_dict

    def reorient(self, val_prefix: str = "") -> "Variables":
        """
        "Reorients" itself, so that variable names will now point to
        their new column names:

        >>> # before
        >>> v = Variables(First=Variables(Second=Variables(CODE="Value")))
        >>> v.to_dict()
        { 'First': { 'Second': { 'CODE': 'Value' } } }
        >>> # after
        >>> v_reoriented = v.reorient()
        >>> v_reoriented
        { 'First': { 'Second': { 'Value': 'First_Second_Value' } } }
        """

        reoriented = Variables()

        for k, v in self.items():
            # in this case, the key is the original variable name
            if isinstance(v, str):
                if v in reoriented.keys():
                    raise Exception(f"{v} is already in reoriented")

                if k == v:
                    # in this case, we haven't renamed the variable; so don't give
                    # it a fancy name
                    reoriented[v] = k
                else:
                    reoriented[v] = val_prefix + v
                continue

            reoriented[k] = v.reorient(val_prefix=f"{val_prefix}{k}_")

        return reoriented

    def __setitem__(self, k: str, v: Union[str, "Variables"]) -> None:
        setattr(self, k, v)

    def __repr__(self) -> str:
        return self.to_dict().__repr__()

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
