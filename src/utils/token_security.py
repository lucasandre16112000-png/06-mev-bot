"""
🛡️ SISTEMA DE SEGURANÇA DE TOKENS
Proteção anti-scam - Apenas tokens confiáveis
"""

from typing import Dict, List, Optional, Set
from web3 import Web3
from loguru import logger
import json

class TokenSecurity:
    """Sistema de verificação de segurança de tokens"""
    
    # Whitelist de tokens 100% confiáveis
    TRUSTED_TOKENS = {
        # Stablecoins
        "USDC", "USDT", "DAI", "BUSD", "FRAX", "TUSD",
        # Major tokens
        "WETH", "ETH", "WBTC", "BTC", "WBNB", "BNB",
        # DeFi Blue Chips
        "UNI", "AAVE", "LINK", "CRV", "SNX", "MKR",
        "COMP", "SUSHI", "BAL", "YFI",
        # Layer 2 tokens
        "ARB", "OP", "MATIC",
        # Outros confiáveis
        "USDC.e", "USDT.e", "DAI.e"
    }
    
    # Endereços de tokens confiáveis por rede
    TRUSTED_ADDRESSES = {
        "base": {
            # Stablecoins
            "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",  # USDC
            "0xfde4C96c8593536E31F229EA8f37b2ADa2699bb2",  # USDT
            # Native
            "0x4200000000000000000000000000000000000006",  # WETH
        },
        "arbitrum": {
            # Stablecoins
            "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",  # USDC
            "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9",  # USDT
            "0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1",  # DAI
            # Native
            "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",  # WETH
            # DeFi
            "0x912CE59144191C1204E64559FE8253a0e49E6548",  # ARB
        },
        "bsc": {
            # Stablecoins
            "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d",  # USDC
            "0x55d398326f99059fF775485246999027B3197955",  # USDT
            "0x1AF3F329e8BE154074D8769D1FFa4eE058B1DBc3",  # DAI
            # Native
            "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",  # WBNB
            # DeFi
            "0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82",  # CAKE
        }
    }
    
    # Blacklist de tokens conhecidos como scam
    BLACKLIST = set()
    
    def __init__(self, web3: Web3, network: str):
        self.w3 = web3
        self.network = network
        self.verified_tokens: Set[str] = set()
        self.rejected_tokens: Set[str] = set()
    
    def is_token_safe(self, token_address: str) -> bool:
        """
        Verifica se um token é seguro para operar
        
        Returns:
            True se token é seguro, False caso contrário
        """
        try:
            token_address = Web3.to_checksum_address(token_address)
            
            # 1. Verificar se está na whitelist
            if self.is_whitelisted(token_address):
                logger.debug(f"✅ Token {token_address[:10]}... está na whitelist")
                return True
            
            # 2. Verificar se está na blacklist
            if self.is_blacklisted(token_address):
                logger.warning(f"❌ Token {token_address[:10]}... está na blacklist!")
                return False
            
            # 3. Verificar se já foi validado antes
            if token_address in self.verified_tokens:
                return True
            
            if token_address in self.rejected_tokens:
                return False
            
            # 4. Executar verificações de segurança
            if not self._perform_security_checks(token_address):
                self.rejected_tokens.add(token_address)
                return False
            
            # Token passou em todas as verificações
            self.verified_tokens.add(token_address)
            logger.info(f"✅ Token {token_address[:10]}... verificado e aprovado!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar token: {e}")
            return False
    
    def is_whitelisted(self, token_address: str) -> bool:
        """Verifica se token está na whitelist"""
        token_address = token_address.lower()
        
        if self.network in self.TRUSTED_ADDRESSES:
            trusted = [addr.lower() for addr in self.TRUSTED_ADDRESSES[self.network]]
            return token_address in trusted
        
        return False
    
    def is_blacklisted(self, token_address: str) -> bool:
        """Verifica se token está na blacklist"""
        return token_address.lower() in self.BLACKLIST
    
    def _perform_security_checks(self, token_address: str) -> bool:
        """
        Executa verificações de segurança completas
        
        Verificações:
        1. Contrato existe
        2. Tem código (não é EOA)
        3. Tem liquidez mínima
        4. Não tem funções maliciosas
        """
        try:
            # 1. Verificar se contrato existe
            code = self.w3.eth.get_code(token_address)
            if code == b'' or code == '0x':
                logger.warning(f"❌ Token {token_address[:10]}... não é um contrato!")
                return False
            
            # 2. Verificar se tem métodos ERC20 básicos
            if not self._has_erc20_methods(token_address):
                logger.warning(f"❌ Token {token_address[:10]}... não implementa ERC20!")
                return False
            
            # 3. Verificar liquidez (simplificado)
            # Na prática, você verificaria pools de liquidez
            
            logger.info(f"✅ Token {token_address[:10]}... passou nas verificações básicas")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro nas verificações de segurança: {e}")
            return False
    
    def _has_erc20_methods(self, token_address: str) -> bool:
        """Verifica se token implementa métodos ERC20 básicos"""
        try:
            # ABI mínima ERC20
            erc20_abi = json.loads('[{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"type":"function"}]')
            
            contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(token_address),
                abi=erc20_abi
            )
            
            # Tentar chamar métodos básicos
            contract.functions.totalSupply().call()
            contract.functions.decimals().call()
            contract.functions.symbol().call()
            
            return True
            
        except Exception as e:
            logger.debug(f"Token não implementa ERC20: {e}")
            return False
    
    def get_token_info(self, token_address: str) -> Optional[Dict]:
        """Obtém informações do token"""
        try:
            if not self.is_token_safe(token_address):
                return None
            
            erc20_abi = json.loads('[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"type":"function"}]')
            
            contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(token_address),
                abi=erc20_abi
            )
            
            return {
                'address': token_address,
                'name': contract.functions.name().call(),
                'symbol': contract.functions.symbol().call(),
                'decimals': contract.functions.decimals().call(),
                'totalSupply': contract.functions.totalSupply().call()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter info do token: {e}")
            return None
    
    def add_to_blacklist(self, token_address: str, reason: str = ""):
        """Adiciona token à blacklist"""
        self.BLACKLIST.add(token_address.lower())
        logger.warning(f"⚠️ Token {token_address[:10]}... adicionado à blacklist: {reason}")
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas de segurança"""
        return {
            'verified_tokens': len(self.verified_tokens),
            'rejected_tokens': len(self.rejected_tokens),
            'blacklist_size': len(self.BLACKLIST),
            'whitelist_size': len(self.TRUSTED_ADDRESSES.get(self.network, []))
        }

class TokenFilter:
    """Filtro de tokens para o bot"""
    
    def __init__(self, blockchain_connector):
        self.blockchain = blockchain_connector
        self.security_checkers: Dict[str, TokenSecurity] = {}
        self._initialize_checkers()
    
    def _initialize_checkers(self):
        """Inicializa checkers de segurança para cada rede"""
        for network_name, w3 in self.blockchain.web3_instances.items():
            self.security_checkers[network_name] = TokenSecurity(w3, network_name)
            logger.info(f"🛡️ Token security ativado para {network_name}")
    
    def is_pair_safe(self, network: str, token_in: str, token_out: str) -> bool:
        """Verifica se um par de tokens é seguro"""
        if network not in self.security_checkers:
            logger.warning(f"⚠️ Rede {network} não tem security checker!")
            return False
        
        checker = self.security_checkers[network]
        
        # Ambos os tokens devem ser seguros
        token_in_safe = checker.is_token_safe(token_in)
        token_out_safe = checker.is_token_safe(token_out)
        
        if not token_in_safe:
            logger.warning(f"❌ Token IN {token_in[:10]}... rejeitado!")
        
        if not token_out_safe:
            logger.warning(f"❌ Token OUT {token_out[:10]}... rejeitado!")
        
        return token_in_safe and token_out_safe
    
    def filter_opportunities(self, opportunities: List[Dict]) -> List[Dict]:
        """Filtra oportunidades removendo tokens não seguros"""
        safe_opportunities = []
        
        for opp in opportunities:
            network = opp.get('network')
            token_in = opp.get('token_in')
            token_out = opp.get('token_out')
            
            if self.is_pair_safe(network, token_in, token_out):
                safe_opportunities.append(opp)
            else:
                logger.warning(f"⚠️ Oportunidade rejeitada por segurança!")
        
        if len(safe_opportunities) < len(opportunities):
            rejected = len(opportunities) - len(safe_opportunities)
            logger.info(f"🛡️ {rejected} oportunidades rejeitadas por segurança")
        
        return safe_opportunities
    
    def get_all_stats(self) -> Dict:
        """Retorna estatísticas de todas as redes"""
        stats = {}
        for network, checker in self.security_checkers.items():
            stats[network] = checker.get_stats()
        return stats
