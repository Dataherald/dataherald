from overrides import override

from dataherald.config import System
from dataherald.context_store import ContextStore


class DefaultContextStore(ContextStore):

    def __init__(self, system: System):
        super().__init__(system)

    @override
    def retrieve_context_for_question(self, nl_question: str) -> str:
        return "Question: 'How much did an apartment cost in Los Angeles in May 2022?' \n SQL: select * from redfin_median_sale_price rmsp where location_name = 'Los Angeles' and property_type='Condo/Co-op' and period_start='2022-05-01'"
    


    
