import asyncio
import datetime
import random
import time
import logging
import aiohttp

from aiohttp import ServerDisconnectedError
from eth_account.messages import encode_defunct
from web3 import Web3
from cfg import concurrent_tasks, total_count, ref_id
from proxies import proxy_list
from setup_logger import setup_logger

logger = setup_logger('Crypto Mayor', 'crypto_mayor.log', logging.INFO)

w3 = Web3()

async def create_new_eth_account():
    account = w3.eth.account.create()
    private_key = account.privateKey.hex()
    address = account.address
    return private_key, address

async def create_signature(private_key):
    now = datetime.datetime.now()
    timestamp = int(time.mktime(now.timetuple()) * 1000)
    message = f'cm-{timestamp}'
    message_bytes = message.encode('utf-8')
    decoded = encode_defunct(primitive=message_bytes)
    signature = w3.eth.account.sign_message(decoded, private_key=private_key)
    return signature.signature.hex(), message

async def generate_ref_id_bytes(address):
    address_bytes = address.encode('utf-8')
    bytes = b'\x08\xeb\x0f\x12,\n*'+address_bytes
    return bytes

async def connect_and_send(url, ref_id_bytes, proxy_url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(url, proxy=proxy_url) as ws:
                await ws.send_bytes(ref_id_bytes)
                logger.debug(ref_id_bytes)
                response = await ws.receive()
                if response.type == aiohttp.WSMsgType.BINARY:
                    logger.debug(f"Response: {response.data.hex()}")
                elif response.type == aiohttp.WSMsgType.TEXT:
                    logger.debug(f"Response: {response.data}")
                else:
                    logger.error("Received non-binary/text message")
                logger.info('SUCCESS +1 ref')
    except ServerDisconnectedError:
        logger.error('Server disconnected!')
        pass

async def main(ref_id, proxy):
    private_key, address = await create_new_eth_account()
    logger.debug(f"New Ethereum account created:\nPrivate Key: {private_key}\nAddress: {address}")
    signature, sd = await create_signature(private_key)
    url = f"wss://gamews.cryptomayor.net/game/coins?user_id={address}&s={signature}&sd={sd}"
    ref_id_bytes = await generate_ref_id_bytes(ref_id)
    logger.debug(ref_id_bytes)
    proxy_url = f'http://{proxy}'
    await connect_and_send(url, ref_id_bytes, proxy_url)

async def async_main(ref_id, total_count, concurrent_tasks):
    while total_count > 0:
        tasks_to_run = min(total_count, concurrent_tasks)
        tasks = [main(ref_id, random.choice(proxy_list)) for _ in range(tasks_to_run)]
        await asyncio.gather(*tasks)
        total_count -= tasks_to_run

if __name__ == '__main__':
    asyncio.run(async_main(ref_id, total_count, concurrent_tasks))
