# Modelling notes

## POC philosophy

The first model should be simple enough that we can explain why every terrain cell changed.

A sophisticated physical model is useful only after the input pipeline and validation method are trustworthy.

## Suggested v0 state equation

For each grid cell and timestep:

1. estimate precipitation at the cell;
2. classify rain / mixed / snow;
3. convert snowfall water equivalent to fresh-snow depth;
4. apply simple settlement/compaction;
5. estimate wind erosion on exposed terrain;
6. redistribute a bounded portion toward plausible lee/deposition terrain;
7. apply temperature/radiation-driven melt or surface change;
8. update state and uncertainty.

This is not intended to reproduce full snow stratigraphy.

## Terrain influence

Candidate terrain predictors:

- elevation;
- aspect relative to wind;
- local slope;
- curvature;
- topographic position;
- upwind fetch;
- local shelter;
- forest/open terrain;
- horizon shading;
- potential solar radiation.

## Wind redistribution

The first algorithm should conserve snow mass across the model domain as far as practical.

Avoid a naive rule such as “east aspect receives more snow in west wind.” Terrain geometry matters:

- exposed windward convexities can scour;
- lee slopes can deposit;
- gullies collect;
- ridges can accelerate flow;
- forests alter transport.

The POC can still use a parameterised approximation, but output must include the wind-redistribution contribution separately so it can be inspected.

## Forecasting

The same model function should accept:

- historical forcing;
- current observations;
- deterministic forecast forcing;
- eventually ensemble forecast members.

This lets one code path support reconstruction and forecasting.

## Validation

Do not validate by asking whether the rendered mountain “looks plausible.”

Use measurable comparisons where possible:

- station snow-depth/SWE observations;
- reported new-snow amounts;
- documented wind slabs;
- observed avalanche aspect/elevation;
- satellite snow/no-snow extent where useful.

A successful POC does not require exact centimetre-scale snow depth. It should demonstrate that the model produces physically plausible **relative spatial changes** and responds sensibly to weather forcing.

## Uncertainty

A future UI should prefer ranges/confidence over false precision.

Potential uncertainty components:

- meteorological forecast uncertainty;
- precipitation downscaling;
- snow/rain phase;
- wind redistribution;
- sparse observations;
- vegetation classification;
- model parameter uncertainty.
