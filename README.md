# itm_models

Simple wrapper for other Python wrappers of ITM models like MSIS, IRI, and IGRF.

At least for now, this is intended as a simple personal codebase to replace the functionality of pyglow, and provide a uniform xarray-based interface.

If used in a publication, please credit the underlying wrappers appropriately:

- pymsis (https://github.com/SWxTREC/pymsis)
- PyIRI (https://github.com/victoriyaforsythe/PyIRI)
- pyigrf ()


## Installation

Install in editable mode for development:

```bash
git clone https://github.com/bharding512/itm_models.git
cd itm_models
pip install -e .
```


## Usage

See examples directory for more.

```
# Run an altitude profile of MSIS

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import itm_models

ds = itm_models.msis(
    time=pd.to_datetime('2025-07-24 12:59'),
    lat=0,
    lon=0,
    alt=np.linspace(80,300,100),
)

plt.figure()
ds.O.plot(xscale='log', y='alt')
```

