from pydantic import confloat

ACCEPTANCE_THRESHOLD: confloat(ge=0, le=1) = 0.8
