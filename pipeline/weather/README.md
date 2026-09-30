# Weather pipeline

Responsibilities:

- acquire historical observations;
- acquire forecast model forcing;
- normalize units/timestamps;
- interpolate/downscale forcing onto the mountain grid;
- preserve model-run/source metadata.

Historical reconstruction comes before live forecast ingestion.
