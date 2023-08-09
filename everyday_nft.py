#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: Joey Chen

"""

import json
import pandas as pd
from accounts import accounts
from contracts import contracts
from proxy import proxy
import pickle
import time
from web3 import Web3
import requests
from PIL import Image

# =============================================================================
# end points loading
# =============================================================================



def find_wallet_txn():
    
    
    with open("config.json", newline='') as jsonfile:
        config = json.load(jsonfile)

    
    
    address = config['address']
    offset = config['offset']
    page = config['page']
    startblk = config['startblk']
    sort = config['sort']

    
    proxy_api = proxy(str(config['etherscan_key']))
    accounts_api = accounts(str(config['etherscan_key']))
    
     
    endblk = int(proxy_api.eth_block_num(),base = 16)
    
  
    mint_721_txn = accounts_api.get_erc721_transfer_txn_by_wallet(address = address,
                                                    contract_address = "0x0000000000000000000000000000000000000000",
                                                    page = page,
                                                    offset = offset,
                                                    startblk = startblk,
                                                    endblk = endblk,
                                                    sort = sort)
  
    mint_1155_txn = accounts_api.get_erc1155_transfer_txn_by_wallet(address = address,
                                                    contract_address = "0x0000000000000000000000000000000000000000",
                                                    page = page,
                                                    offset = offset,
                                                    startblk = startblk,
                                                    endblk = endblk,
                                                    sort = sort)
    
    mint_721_txn_df = pd.DataFrame(mint_721_txn)
    mint_1155_txn_df = pd.DataFrame(mint_1155_txn)
    
    
    return mint_721_txn_df,mint_1155_txn_df

def classify_link(link):
    if link.startswith('ipfs://'):
        # Convert IPFS URL to https://ipfs.io/ipfs/ form
        ipfs_cid = link[len('ipfs://'):]
        new_link = f'https://ipfs.io/ipfs/{ipfs_cid}'
        return new_link
    elif link.startswith('https://'):
        return  link
    else:
        return ""


def find_txn_img(txn_df):
    
    with open("config.json", newline='') as jsonfile:
        config = json.load(jsonfile)
    
    image = []
    
    web3 = Web3(Web3.HTTPProvider('API'))
    contracts_api = contracts(str(config['etherscan_key']))
    
    
    for i in range(len(txn_df)):
        contract_address = txn_df['contractAddress'][i]
        contract_abi = contracts_api.get_contract_abi(contract_address)
        nft_contract = web3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=contract_abi)
        
        
        token_id = int(txn_df['tokenID'][i])
        token_uri = nft_contract.functions.tokenURI(token_id).call()
        token_uri = classify_link(token_uri)
        
        if token_uri != "":
        
            print(f"Token ID: {token_id}, Token URI: {token_uri}")
            
            response = requests.get(token_uri)
            token_metadata = response.json()
            image_url = token_metadata.get('image')

            image_response = requests.get(image_url)
            image.append(image_response)
            # with open('image.jpg', 'wb') as f:
            #     f.write(image_response.content)
    return image

mint_721_txn_df,mint_1155_txn_df = find_wallet_txn()
image = find_txn_img(mint_721_txn_df)
