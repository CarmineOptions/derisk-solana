from typing import Type, Literal, Tuple

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
	| Type[db.MangoHealthRatioEA]
	| Type[db.SolendHealthRatioEA]
	| Type[db.MarginfiHealthRatioEA]
	| Type[db.KaminoHealthRatioEA]
)


def get_health_ratio_protocol_model(
		protocol: Protocol
) -> Tuple[AnyHealthRatioModel, AnyHealthRatioModel] | Tuple[None, None]:
	"""
	"""
	if protocol == MANGO:
		return db.MangoHealthRatio, db.MangoHealthRatioEA

	if protocol == KAMINO:
		return db.KaminoHealthRatio, db.KaminoHealthRatioEA

	if protocol == MARGINFI:
		return db.MarginfiHealthRatio, db.MarginfiHealthRatioEA

	if protocol == SOLEND:
		return db.SolendHealthRatio, db.SolendHealthRatioEA

	return None, None
