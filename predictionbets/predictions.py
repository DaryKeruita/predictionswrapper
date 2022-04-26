from abc import ABC, abstractmethod
from typing import Optional

from eth_account import Account
from web3 import Web3
from web3.types import TxReceipt

from predictionbets.abis.candlegenie import CANDLE_GENIE_ADDRESS, CANDLE_GENIE_ABI
from predictionbets.abis.dogebets import DOGE_BETS_ABI, DOGE_BETS_ADDRESS
from predictionbets.abis.pancakeswap import PANCAKE_ADDRESS, PANCAKESWAP_ABI

GAS = 400000
GAS_PRICE = 5000000000


class Prediction(ABC):
    @abstractmethod
    def is_paused(self) -> bool:
        pass

    @abstractmethod
    def current_epoch(self) -> int:
        pass

    @abstractmethod
    def user_rounds_count(self, user_address: str) -> int:
        pass

    @abstractmethod
    def bet_bull(self, epoch: int, amount_bnb: int) -> TxReceipt:
        pass

    @abstractmethod
    def bet_bear(self, epoch: int, amount_bnb: int) -> TxReceipt:
        pass

    @abstractmethod
    def user_claim(self, private_key: str) -> Optional[TxReceipt]:
        pass


class DogeBet(Prediction):
    def __init__(self, w3: Web3, private_key: str):
        super().__init__()
        self.private_key = private_key
        self.public_key = Web3.toChecksumAddress(Account.from_key(self.private_key).address)
        self.w3 = w3
        self.w3Contract = w3.eth.contract(address=DOGE_BETS_ADDRESS, abi=DOGE_BETS_ABI)
        self.referral_address = Web3.toChecksumAddress('0x45B2e613aED338BFeAD42351ED213e9761162dAd')

    def is_paused(self):
        return self.w3Contract.functions.IsPaused().call()

    def current_epoch(self) -> int:
        return self.w3Contract.functions.currentEpoch().call()

    def user_rounds_count(self, user_address: str) -> int:
        return self.w3Contract.functions.GetUserRoundsLength(self.public_key).call()

    def bet_bull(self, epoch: int, amount_bnb: int, w3=None) -> TxReceipt:
        txn = self.w3Contract.functions.user_BetBull(epoch, self.referral_address).buildTransaction({
            'from': self.public_key,
            'nonce': w3.eth.getTransactionCount(self.public_key),
            'value': amount_bnb,
            'gas': GAS,
            'gasPrice': GAS_PRICE,
        })
        signed_txn = w3.eth.account.signTransaction(txn, private_key=self.private_key)
        w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        return Web3.toHex(Web3.sha3(signed_txn.rawTransaction))

    def bet_bear(self, epoch: int, amount_bnb: int) -> TxReceipt:
        txn = self.w3Contract.functions.user_BetBear(epoch, self.referral_address).buildTransaction({
            'from': self.public_key,
            'nonce': self.w3.eth.getTransactionCount(self.public_key),
            'value': amount_bnb,
            'gas': GAS,
            'gasPrice': GAS_PRICE,
        })
        signed_txn = self.w3.eth.account.signTransaction(txn, private_key=self.private_key)
        self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        return Web3.toHex(Web3.sha3(signed_txn.rawTransaction))

    def fetch_claimable(self, _range=20):
        end = self.current_epoch() - 1
        start = end - _range
        epochs = []
        for epoch in range(start, end):
            claimable = self.w3Contract.functions.Claimable(epoch, self.public_key).call()
            if claimable:
                epochs.append(epoch)
        return epochs

    def user_claim(self, private_key: str) -> Optional[TxReceipt]:
        claimable_rounds = self.fetch_claimable()
        if claimable_rounds:
            txn = self.w3Contract.functions.user_Claim(claimable_rounds).buildTransaction({
                'from': self.public_key,
                'nonce': self.w3.eth.getTransactionCount(self.public_key)
            })
            signed_txn = self.w3.eth.account.signTransaction(txn, private_key=self.private_key)
            self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
            return self.w3.eth.waitForTransactionReceipt(signed_txn.hash)
        return None


class PancakeSwap(Prediction):
    def __init__(self, w3: Web3, private_key: str):
        super().__init__()
        self.private_key = private_key
        self.public_key = Web3.toChecksumAddress(Account.from_key(self.private_key).address)
        self.w3 = w3
        self.w3Contract = w3.eth.contract(address=PANCAKE_ADDRESS, abi=PANCAKESWAP_ABI)
        self.referral_address = Web3.toChecksumAddress('0x45B2e613aED338BFeAD42351ED213e9761162dAd')

    def is_paused(self):
        return self.w3Contract.functions.paused(self.public_key).call()

    def current_epoch(self) -> int:
        return self.w3Contract.functions.currentEpoch(self.public_key).call()

    def user_rounds_count(self, user_address: str) -> int:
        return self.w3Contract.functions.getUserRoundsLength(self.public_key).call()

    def bet_bull(self, epoch: int, amount_bnb: int) -> TxReceipt:
        txn = self.w3Contract.functions.betBull(epoch).buildTransaction({
            'from': self.public_key,
            'nonce': self.w3.eth.getTransactionCount(self.public_key),
            'value': amount_bnb,
            'gas': GAS,
            'gasPrice': GAS_PRICE,
        })
        signed_txn = self.w3.eth.account.signTransaction(txn, private_key=self.private_key)
        self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        return Web3.toHex(Web3.sha3(signed_txn.rawTransaction))

    def bet_bear(self, epoch: int, amount_bnb: int) -> TxReceipt:
        txn = self.w3Contract.functions.betBear(epoch).buildTransaction({
            'from': self.public_key,
            'nonce': self.w3.eth.getTransactionCount(self.public_key),
            'value': amount_bnb,
            'gas': GAS,
            'gasPrice': GAS_PRICE,
        })
        signed_txn = self.w3.eth.account.signTransaction(txn, private_key=self.private_key)
        self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        return Web3.toHex(Web3.sha3(signed_txn.rawTransaction))

    def fetch_claimable(self, _range=20):
        end = self.current_epoch() - 1
        start = end - _range
        epochs = []
        for epoch in range(start, end):
            claimable = self.w3Contract.functions.claimable(epoch, self.public_key).call()
            if claimable:
                epochs.append(epoch)
        return epochs

    def user_claim(self, private_key: str) -> Optional[TxReceipt]:
        claimable_rounds = self.fetch_claimable()
        if claimable_rounds:
            txn = self.w3Contract.functions.claim(claimable_rounds).buildTransaction({
                'from': self.public_key,
                'nonce': self.w3.eth.getTransactionCount(self.public_key)
            })
            signed_txn = self.w3.eth.account.signTransaction(txn, private_key=self.private_key)
            self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
            return self.w3.eth.waitForTransactionReceipt(signed_txn.hash)
        return None


class CandleGenie(Prediction):
    def __init__(self, w3: Web3, private_key: str):
        super().__init__()
        self.private_key = private_key
        self.public_key = Web3.toChecksumAddress(Account.from_key(self.private_key).address)
        self.w3 = w3
        self.w3Contract = w3.eth.contract(address=CANDLE_GENIE_ADDRESS, abi=CANDLE_GENIE_ABI)
        self.referral_address = Web3.toChecksumAddress('0x45B2e613aED338BFeAD42351ED213e9761162dAd')

    def is_paused(self):
        return self.w3Contract.functions.paused().call()

    def current_epoch(self) -> int:
        return self.w3Contract.functions.currentEpoch().call()

    def user_rounds_count(self, user_address: str) -> int:
        return self.w3Contract.functions.getUserRoundsLength(self.public_key).call()

    def bet_bull(self, epoch: int, amount_bnb: int) -> TxReceipt:
        txn = self.w3Contract.functions.BetBull(epoch).buildTransaction({
            'from': self.public_key,
            'nonce': self.w3.eth.getTransactionCount(self.public_key),
            'value': amount_bnb,
            'gas': GAS,
            'gasPrice': GAS_PRICE,
        })
        signed_txn = self.w3.eth.account.signTransaction(txn, private_key=self.private_key)
        self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        return Web3.toHex(Web3.sha3(signed_txn.rawTransaction))

    def bet_bear(self, epoch: int, amount_bnb: int) -> TxReceipt:
        txn = self.w3Contract.functions.BetBear(epoch).buildTransaction({
            'from': self.public_key,
            'nonce': self.w3.eth.getTransactionCount(self.public_key),
            'value': amount_bnb,
            'gas': GAS,
            'gasPrice': GAS_PRICE,
        })
        signed_txn = self.w3.eth.account.signTransaction(txn, private_key=self.private_key)
        self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        return Web3.toHex(Web3.sha3(signed_txn.rawTransaction))

    def fetch_claimable(self, _range=20):
        end = self.current_epoch() - 1
        start = end - _range
        epochs = []
        for epoch in range(start, end):
            claimable = self.w3Contract.functions.claimable(epoch, self.public_key).call()
            if claimable:
                epochs.append(epoch)
        return epochs

    def user_claim(self, private_key: str) -> Optional[TxReceipt]:
        claimable_rounds = self.fetch_claimable()
        if claimable_rounds:
            txn = self.w3Contract.functions.ClaimReferred(claimable_rounds, self.referral_address).buildTransaction({
                'from': self.public_key,
                'nonce': self.w3.eth.getTransactionCount(self.public_key)
            })
            signed_txn = self.w3.eth.account.signTransaction(txn, private_key=self.private_key)
            self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
            return Web3.toHex(Web3.sha3(signed_txn.rawTransaction))
        return None
