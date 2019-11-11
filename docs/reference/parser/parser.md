## *Class* `FrofTransformer(Transformer)`


Lark Transformer for Frof syntax.

You can probably ignore this, unless you're fiddling with the language.


## *Class* `FrofParser`


A parser for the .frof syntax.

Contains minimal logic; see FrofTransformer for more details.


## *Function* `__init__(self) -> None`


Create a new Parser.

### Arguments
    None

### Returns
    None



## *Function* `parse(self, frof: str) -> nx.DiGraph`


Parse a .frof syntax tree.

### Arguments
> - **frof** (`str`: `None`): The contents to parse

### Return
> - **nx.DiGraph** (`None`: `None`): The parsed job network

