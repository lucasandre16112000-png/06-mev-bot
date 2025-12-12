"""
🔄 MÓDULO DE INTERFACE COM DEXs
Gerencia interações com Uniswap, PancakeSwap, Aerodrome, etc
"""

from typing import Dict, List, Optional, Tuple
from web3 import Web3
from loguru import logger
import json

from src.config.config import (
    UNISWAP_V3_ROUTER,
    PANCAKESWAP_V3_ROUTER,
    AERODROME_ROUTER,
    MAJOR_TOKENS
)
# Tentar usar versão REAL primeiro
try:
    from src.utils.real_token_security import RealTokenSecurity as TokenSecurity
    logger.info("✅ Usando RealTokenSecurity (VERIFICAÇÃO REAL)")
except ImportError:
    from src.utils.advanced_token_security import AdvancedTokenSecurity as TokenSecurity
    logger.warning("⚠️ Usando AdvancedTokenSecurity (VERIFICAÇÃO BÁSICA)")

# ABIs simplificadas
UNISWAP_V3_QUOTER_ABI = json.loads('[{"inputs":[{"internalType":"address","name":"tokenIn","type":"address"},{"internalType":"address","name":"tokenOut","type":"address"},{"internalType":"uint24","name":"fee","type":"uint24"},{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint160","name":"sqrtPriceLimitX96","type":"uint160"}],"name":"quoteExactInputSingle","outputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"}],"stateMutability":"nonpayable","type":"function"}]')

ROUTER_ABI = json.loads('[{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsOut","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"}]')

class DEXInterface:
    """Interface para interagir com DEXs"""
    
    def __init__(self, web3: Web3, network: str):
        self.w3 = web3
        self.network = network
        self.dexs = self._initialize_dexs()
        self.token_security = TokenSecurity(web3, network)
        logger.info(f"🛡️ Sistema anti-scam ativado para {network}")
        
    def _initialize_dexs(self) -> Dict:
        """Inicializa contratos das DEXs"""
        dexs = {}
        
        try:
            # Uniswap V3
            if self.network in UNISWAP_V3_ROUTER:
                router_address = UNISWAP_V3_ROUTER[self.network]
                dexs['uniswap_v3'] = {
                    'name': 'Uniswap V3',
                    'router': router_address,
                    'type': 'v3'
                }
            
            # PancakeSwap
            if self.network in PANCAKESWAP_V3_ROUTER:
                router_address = PANCAKESWAP_V3_ROUTER[self.network]
                dexs['pancakeswap'] = {
                    'name': 'PancakeSwap',
                    'router': router_address,
                    'contract': self.w3.eth.contract(
                        address=Web3.to_checksum_address(router_address),
                        abi=ROUTER_ABI
                    ),
                    'type': 'v2'
                }
            
            # Aerodrome (Base)
            if self.network in AERODROME_ROUTER:
                router_address = AERODROME_ROUTER[self.network]
                dexs['aerodrome'] = {
                    'name': 'Aerodrome',
                    'router': router_address,
                    'type': 'v2'
                }
            
            logger.info(f"✅ {len(dexs)} DEXs inicializadas em {self.network}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar DEXs: {e}")
        
        return dexs
    
    def get_price(self, dex_name: str, token_in: str, token_out: str, amount_in: int) -> Optional[int]:
        """Obtém preço de um token em uma DEX"""
        try:
            if dex_name not in self.dexs:
                return None
            
            dex = self.dexs[dex_name]
            
            if dex['type'] == 'v2':
                return self._get_price_v2(dex, token_in, token_out, amount_in)
            elif dex['type'] == 'v3':
                return self._get_price_v3(dex, token_in, token_out, amount_in)
            
            return None
            
        except Exception as e:
            logger.debug(f"Erro ao obter preço em {dex_name}: {e}")
            return None
    
    def _get_price_v2(self, dex: dict, token_in: str, token_out: str, amount_in: int) -> Optional[int]:
        """Obtém preço em DEX V2 (Uniswap V2, PancakeSwap)"""
        try:
            if 'contract' not in dex:
                return None
            
            path = [
                Web3.to_checksum_address(token_in),
                Web3.to_checksum_address(token_out)
            ]
            
            amounts = dex['contract'].functions.getAmountsOut(amount_in, path).call()
            return amounts[1]  # amount_out
            
        except Exception as e:
            logger.debug(f"Erro V2: {e}")
            return None
    
    def _get_price_v3(self, dex: dict, token_in: str, token_out: str, amount_in: int) -> Optional[int]:
        """Obtém preço em DEX V3 (Uniswap V3)"""
        # Implementação simplificada - na prática usaria quoter contract
        return None
    
    def find_arbitrage_opportunity(
        self,
        token_in: str,
        token_out: str,
        amount_in: int
    ) -> Optional[Dict]:
        """Encontra oportunidade de arbitragem entre DEXs"""
        try:
            # 🛡️ PROTEÇÃO ANTI-SCAM: Verificar se tokens são seguros
            token_in_safe, reason_in = self.token_security.is_token_safe(token_in)
            token_out_safe, reason_out = self.token_security.is_token_safe(token_out)
            
            if not token_in_safe:
                logger.debug(f"❌ Token IN rejeitado: {reason_in}")
                return None
            
            if not token_out_safe:
                logger.debug(f"❌ Token OUT rejeitado: {reason_out}")
                return None
            prices = {}
            
            # Obter preços em todas as DEXs
            for dex_name in self.dexs.keys():
                price = self.get_price(dex_name, token_in, token_out, amount_in)
                if price:
                    prices[dex_name] = price
            
            if len(prices) < 2:
                return None
            
            # Encontrar melhor compra (menor preço = mais tokens recebidos)
            buy_dex = max(prices.items(), key=lambda x: x[1])
            # Encontrar melhor venda (maior preço = mais tokens recebidos na volta)
            sell_dex = min(prices.items(), key=lambda x: x[1])
            
            if buy_dex[0] == sell_dex[0]:
                return None
            
            # Calcular lucro potencial
            amount_out_buy = buy_dex[1]
            amount_out_sell = self.get_price(sell_dex[0], token_out, token_in, amount_out_buy)
            
            if not amount_out_sell:
                return None
            
            profit = amount_out_sell - amount_in
            profit_percentage = (profit / amount_in) * 100
            
            if profit <= 0:
                return None
            
            return {
                'buy_dex': buy_dex[0],
                'sell_dex': sell_dex[0],
                'token_in': token_in,
                'token_out': token_out,
                'amount_in': amount_in,
                'amount_out_buy': amount_out_buy,
                'amount_out_sell': amount_out_sell,
                'profit': profit,
                'profit_percentage': profit_percentage,
                'network': self.network
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar arbitragem: {e}")
            return None
    
    def scan_all_pairs(self, amount_usd: int = 10000) -> List[Dict]:
        """Escaneia todos os pares de tokens buscando oportunidades"""
        opportunities = []
        
        try:
            # Obter tokens da rede
            tokens = MAJOR_TOKENS
            network_tokens = {}
            
            for symbol, addresses in tokens.items():
                if self.network in addresses:
                    network_tokens[symbol] = addresses[self.network]
            
            # Testar todos os pares
            token_list = list(network_tokens.items())
            
            for i, (symbol_in, addr_in) in enumerate(token_list):
                for symbol_out, addr_out in token_list[i+1:]:
                    # Converter USD para amount baseado no token
                    amount_in = self.w3.to_wei(amount_usd, 'mwei')  # Assumindo 6 decimals
                    
                    opp = self.find_arbitrage_opportunity(addr_in, addr_out, amount_in)
                    
                    if opp:
                        opp['symbol_in'] = symbol_in
                        opp['symbol_out'] = symbol_out
                        opportunities.append(opp)
            
            if opportunities:
                logger.info(f"🎯 {len(opportunities)} oportunidades encontradas!")
            
        except Exception as e:
            logger.error(f"❌ Erro ao escanear pares: {e}")
        
        return opportunities

class MultiDEXScanner:
    """Scanner de múltiplas DEXs em múltiplas redes"""
    
    def __init__(self, blockchain_connector):
        self.blockchain = blockchain_connector
        self.dex_interfaces: Dict[str, DEXInterface] = {}
        self._initialize_interfaces()
    
    def _initialize_interfaces(self):
        """Inicializa interfaces para todas as redes"""
        for network_name, w3 in self.blockchain.web3_instances.items():
            self.dex_interfaces[network_name] = DEXInterface(w3, network_name)
            logger.info(f"✅ DEX interface criada para {network_name}")
    
    def scan_all_networks(self, amount_usd: int = 10000) -> List[Dict]:
        """Escaneia todas as redes buscando oportunidades"""
        all_opportunities = []
        
        for network_name, dex_interface in self.dex_interfaces.items():
            logger.info(f"🔍 Escaneando {network_name}...")
            opportunities = dex_interface.scan_all_pairs(amount_usd)
            all_opportunities.extend(opportunities)
        
        # Ordenar por lucro
        all_opportunities.sort(key=lambda x: x['profit_percentage'], reverse=True)
        
        return all_opportunities
    
    def get_best_opportunity(self, min_profit_usd: float = 50, min_profit_pct: float = 1.0) -> Optional[Dict]:
        """Retorna a melhor oportunidade que atende aos critérios"""
        opportunities = self.scan_all_networks()
        
        for opp in opportunities:
            profit_usd = self.blockchain.get_web3(opp['network']).from_wei(opp['profit'], 'mwei')
            
            if profit_usd >= min_profit_usd and opp['profit_percentage'] >= min_profit_pct:
                return opp
        
        return None
