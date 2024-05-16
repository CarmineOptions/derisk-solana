from typing import Type, Literal

import db

# TODO: This is duplicate, and it's used somewhere else in the repo,
# move this somewhere more sensible and use everywhere
MARGINFI = "marginfi"
MANGO = "mango"
KAMINO = "kamino"
SOLEND = "solend"
Protocol = Literal["marginfi", "mango", "kamino", "solend"]

AnyHealthRatioModel = (
    Type[db.MangoHealthRatio]
    | Type[db.SolendHealthRatio]
    | Type[db.MarginfiHealthRatio]
    | Type[db.KaminoHealthRatio]
)

def get_health_ratio_protocol_model(protocol: Protocol) -> AnyHealthRatioModel | None:

	if protocol == MANGO:
		return db.MangoHealthRatio

	if protocol == KAMINO:
		return db.KaminoHealthRatio

	if protocol == MARGINFI:
		return db.MarginfiHealthRatio
		
	if protocol == SOLEND:
		return db.SolendHealthRatio

	return None

