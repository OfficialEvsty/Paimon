from transaction_system.transaction import Transaction
from discord import Embed, Member
from typing import Dict


class TransactionList(Embed):
    def __init__(self, member: Member, dict_transactions: Dict[int, Transaction]):
        super(TransactionList, self).__init__()
        self.title = f"Список транзакций `{member}`"
        limit_reason_characters = 35
        transactions_string = ""
        transactions_limit = 60
        counter = 0
        for t_id in reversed(dict_transactions):
            if counter >= transactions_limit:
                break
            reason = dict_transactions[t_id].reason
            if len(reason) > limit_reason_characters:
                reason = dict_transactions[t_id].reason[:limit_reason_characters] + "..."
            reason = reason.ljust(limit_reason_characters + 3, " ")
            transactions_string += f"`{t_id:>4}` : `{reason}` : `{dict_transactions[t_id].date}`\n"
            counter += 1
        self.description = f">>> {transactions_string}"
