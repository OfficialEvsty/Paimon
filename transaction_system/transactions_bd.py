from transaction_system.transaction import Transaction
from item_system.generator import Generator
from discord import Member, Interaction
from data.database import Database
from item_system.item import Item
from typing import Dict, List
import datetime
import discord
import asyncpg


async def get_transactions(member: Member, days: int) -> Dict[int, Transaction]:
    guild = member.guild.id
    user_id = member.id
    current_date = datetime.date.today().strftime('%Y%m%d')
    get_transactions_query = f"SELECT id, reason, date FROM transactions WHERE guild = {guild} " \
                             f"AND user_id = {user_id} AND date >= ('{current_date}'::date - '{days} day'::interval);"
    conn = await asyncpg.connect(Database.str_connection)
    result = await conn.fetch(get_transactions_query)
    transactions = {}
    for action_info in result:
        transactions[action_info[0]] = Transaction(member, action_info[1], date=action_info[2])
    return transactions


async def get_transaction(interaction: Interaction, transaction_id: int) -> Transaction:
    conn = await asyncpg.connect(Database.str_connection)
    get_input_items_by_transaction_id_query = f"SELECT type FROM items_input WHERE transaction_id = {transaction_id};"
    get_output_items_by_transaction_id_query = f"SELECT type FROM items_output WHERE transaction_id = {transaction_id};"
    get_transaction_by_id_query = f"SELECT id, user_id, reason, money, date FROM transactions WHERE id = {transaction_id}"
    input_items_result = await conn.fetch(get_input_items_by_transaction_id_query)
    input_items = put_items_in_dict([item_record[0] for item_record in input_items_result])
    output_items_result = await conn.fetch(get_output_items_by_transaction_id_query)
    output_items = put_items_in_dict([item_record[0] for item_record in output_items_result])
    transaction_result = await conn.fetch(get_transaction_by_id_query)
    member_id = transaction_result[0][1]
    transaction_reason = transaction_result[0][2]
    transaction_money = transaction_result[0][3]
    transaction_date = transaction_result[0][4]
    try:
        member = await interaction.guild.fetch_member(member_id)
    except discord.NotFound:
        return await interaction.followup.send("Пользователя нет на сервере.", delete_after=5)
    return Transaction(member, transaction_reason, transaction_money, input_items, output_items, transaction_date)



# This method writes transaction's data in database.
async def save(action: Transaction):
    member_id = action.member.id
    guild = action.member.guild.id
    reason = action.reason
    money = "NULL" if action.money is None else action.money
    date = datetime.date.today().strftime('%Y%m%d')
    conn = await asyncpg.connect(Database.str_connection)
    save_transaction_query = f"INSERT INTO transactions (guild, user_id, reason, money, date) VALUES " \
                             f"({guild}, {member_id}, '{reason}', {money}, '{date}') RETURNING id;"
    result = await conn.fetch(save_transaction_query)
    transaction_id = result[0][0]
    await save_input_items(transaction_id, action.received_items, conn)
    await save_output_items(transaction_id, action.given_items, conn)
    await clear_old_transactions(conn)
    await conn.close()


def pull_items_from_dict(items: Dict[int, List[Item]]) -> List[bytes]:
    if items is None:
        raise TypeError()
    list_items = []
    for slot in items.values():
        list_items.extend(slot)
    type_ids = [item.type for item in list_items]
    return type_ids


def put_items_in_dict(item_types: List[bytes]) -> Dict[int, List[Item]]:
    items_list = Generator.create_items_without_id(item_types)
    items_dict: Dict[int, List[Item]] = {}
    counter = 0
    for item in items_list:
        for slot in items_dict.values():
            if slot[0].stackable and slot[0].type == item.type:
                slot.append(item)
        items_dict[counter] = [item]
        counter += 1
    return items_dict


async def save_input_items(transaction_id: int, items: Dict[int, List[Item]], conn: asyncpg.Connection):
    try:
        type_ids = pull_items_from_dict(items)
    except TypeError:
        return
    for type_id in type_ids:
        insert_type_id_in_inputs_query = f"INSERT INTO items_input (type, transaction_id) " \
                                         f"VALUES ({type_id}, {transaction_id});"
        await conn.fetch(insert_type_id_in_inputs_query)


async def save_output_items(transaction_id: int, items: Dict[int, List[Item]], conn: asyncpg.Connection):
    try:
        type_ids = pull_items_from_dict(items)
    except TypeError:
        return
    for type_id in type_ids:
        insert_type_id_in_outputs_query = f"INSERT INTO items_output (type, transaction_id) " \
                                         f"VALUES ({type_id}, {transaction_id});"
        await conn.fetch(insert_type_id_in_outputs_query)


async def clear_old_transactions(conn: asyncpg.Connection):
    interval = 7
    current_date = datetime.date.today().strftime('%Y%m%d')
    clear_old_transactions_query = "DO $$ " \
                                   "BEGIN " \
                                        f"DELETE FROM items_input USING transactions " \
                                            f"WHERE transaction_id = transactions.id " \
                                            f"AND transactions.date " \
                                            f"< ('{current_date}'::date - '{interval} days'::interval);" \
                                        f"DELETE FROM items_output USING transactions " \
                                            f"WHERE transaction_id = transactions.id " \
                                            f"AND transactions.date " \
                                            f"< ('{current_date}'::date - '{interval} days'::interval);" \
                                        f"DELETE FROM transactions " \
                                            f"WHERE transactions.date " \
                                            f"< ('{current_date}'::date - '{interval} days'::interval);" \
                                   f"END $$;"
    await conn.fetch(clear_old_transactions_query)

