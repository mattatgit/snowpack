# Data directory

Raw external datasets are intentionally excluded from version control.

Suggested local layout:

```
data/
  raw/
    gsi/
    jma/
    jan/
  interim/
  processed/
```

Each acquisition step should have a script or documented command so the dataset can be reproduced from its original source.

Do not commit licensed/raw third-party datasets unless their terms clearly permit redistribution.
