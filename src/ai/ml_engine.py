"""
🧠 MOTOR DE INTELIGÊNCIA ARTIFICIAL
Sistema de Machine Learning adaptativo para otimizar arbitragem
"""

import os
import pickle
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from loguru import logger
import time
from datetime import datetime

from src.config.config import BotConfig

class MLEngine:
    """Motor de Machine Learning para decisões de arbitragem"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.training_data = []
        self.feature_names = [
            'price_diff_pct',
            'amount_usd',
            'gas_price_gwei',
            'liquidity_score',
            'hour_of_day',
            'day_of_week',
            'network_priority',
            'dex_reliability'
        ]
        self.performance_history = []
        
        # Tentar carregar modelo existente
        self._load_model()
    
    def _load_model(self) -> bool:
        """Carrega modelo salvo se existir"""
        try:
            model_path = "data/ml_models/arbitrage_model.pkl"
            scaler_path = "data/ml_models/scaler.pkl"
            
            if os.path.exists(model_path) and os.path.exists(scaler_path):
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                
                self.is_trained = True
                logger.success("✅ Modelo ML carregado!")
                return True
            
            logger.info("ℹ️ Nenhum modelo encontrado, será treinado com dados novos")
            return False
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao carregar modelo: {e}")
            return False
    
    def _save_model(self):
        """Salva modelo treinado"""
        try:
            os.makedirs("data/ml_models", exist_ok=True)
            
            with open("data/ml_models/arbitrage_model.pkl", 'wb') as f:
                pickle.dump(self.model, f)
            with open("data/ml_models/scaler.pkl", 'wb') as f:
                pickle.dump(self.scaler, f)
            
            logger.info("💾 Modelo salvo!")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar modelo: {e}")
    
    def extract_features(self, opportunity: Dict) -> np.ndarray:
        """Extrai features de uma oportunidade"""
        try:
            now = datetime.now()
            
            # Network priority mapping
            network_priority_map = {
                'base': 0.60,
                'base_sepolia': 0.60,
                'arbitrum': 0.25,
                'arbitrum_sepolia': 0.25,
                'bsc': 0.15,
                'bsc_testnet': 0.15
            }
            
            # DEX reliability (simplificado)
            dex_reliability_map = {
                'uniswap_v3': 0.95,
                'pancakeswap': 0.90,
                'aerodrome': 0.85,
                'camelot': 0.80,
                'sushiswap': 0.75
            }
            
            features = [
                opportunity.get('profit_percentage', 0),  # price_diff_pct
                opportunity.get('amount_in', 0) / 1e6,  # amount_usd
                50.0,  # gas_price_gwei (placeholder)
                0.8,  # liquidity_score (placeholder)
                now.hour,  # hour_of_day
                now.weekday(),  # day_of_week
                network_priority_map.get(opportunity.get('network', ''), 0.5),
                dex_reliability_map.get(opportunity.get('buy_dex', ''), 0.7)
            ]
            
            return np.array(features).reshape(1, -1)
            
        except Exception as e:
            logger.error(f"❌ Erro ao extrair features: {e}")
            return np.zeros((1, len(self.feature_names)))
    
    def predict_success(self, opportunity: Dict) -> Tuple[bool, float]:
        """
        Prediz se uma oportunidade será bem-sucedida
        
        Returns:
            (should_execute, confidence)
        """
        try:
            # Se modelo não está treinado, usar heurística simples
            if not self.is_trained or self.model is None:
                return self._heuristic_decision(opportunity)
            
            # Extrair features
            features = self.extract_features(opportunity)
            
            # Normalizar
            features_scaled = self.scaler.transform(features)
            
            # Predição
            prediction = self.model.predict(features_scaled)[0]
            confidence = self.model.predict_proba(features_scaled)[0][1]
            
            should_execute = (
                prediction == 1 and 
                confidence >= BotConfig.ML_CONFIDENCE_THRESHOLD
            )
            
            return should_execute, confidence
            
        except Exception as e:
            logger.error(f"❌ Erro na predição: {e}")
            return False, 0.0
    
    def _heuristic_decision(self, opportunity: Dict) -> Tuple[bool, float]:
        """Decisão heurística quando modelo não está treinado"""
        try:
            profit_pct = opportunity.get('profit_percentage', 0)
            
            # Regras simples
            if profit_pct >= 2.0:
                return True, 0.9
            elif profit_pct >= 1.5:
                return True, 0.75
            elif profit_pct >= 1.0:
                return True, 0.6
            else:
                return False, 0.3
                
        except:
            return False, 0.0
    
    def record_result(self, opportunity: Dict, success: bool, actual_profit: float):
        """Registra resultado de uma execução para treinamento"""
        try:
            features = self.extract_features(opportunity)
            
            self.training_data.append({
                'features': features.flatten(),
                'success': 1 if success else 0,
                'profit': actual_profit,
                'timestamp': time.time()
            })
            
            # Salvar histórico
            self.performance_history.append({
                'timestamp': time.time(),
                'success': success,
                'profit': actual_profit,
                'profit_pct': opportunity.get('profit_percentage', 0)
            })
            
            # Retreinar se atingiu threshold
            if len(self.training_data) >= BotConfig.ML_MIN_TRAINING_SAMPLES:
                if len(self.training_data) % BotConfig.ML_TRAINING_INTERVAL == 0:
                    logger.info("🔄 Retreinando modelo...")
                    self.train()
            
        except Exception as e:
            logger.error(f"❌ Erro ao registrar resultado: {e}")
    
    def train(self) -> bool:
        """Treina o modelo com dados coletados"""
        try:
            if len(self.training_data) < BotConfig.ML_MIN_TRAINING_SAMPLES:
                logger.warning(f"⚠️ Dados insuficientes para treinar ({len(self.training_data)}/{BotConfig.ML_MIN_TRAINING_SAMPLES})")
                return False
            
            logger.info(f"🎓 Treinando modelo com {len(self.training_data)} amostras...")
            
            # Preparar dados
            X = np.array([d['features'] for d in self.training_data])
            y = np.array([d['success'] for d in self.training_data])
            
            # Split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Normalizar
            self.scaler.fit(X_train)
            X_train_scaled = self.scaler.transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Ensemble: Random Forest + Gradient Boosting
            rf_model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                random_state=42
            )
            
            gb_model = GradientBoostingClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
            
            # Treinar ambos
            rf_model.fit(X_train_scaled, y_train)
            gb_model.fit(X_train_scaled, y_train)
            
            # Avaliar
            rf_score = rf_model.score(X_test_scaled, y_test)
            gb_score = gb_model.score(X_test_scaled, y_test)
            
            logger.info(f"  📊 Random Forest accuracy: {rf_score:.2%}")
            logger.info(f"  📊 Gradient Boosting accuracy: {gb_score:.2%}")
            
            # Usar o melhor
            self.model = rf_model if rf_score >= gb_score else gb_model
            self.is_trained = True
            
            # Salvar
            self._save_model()
            
            logger.success(f"✅ Modelo treinado! Accuracy: {max(rf_score, gb_score):.2%}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao treinar modelo: {e}")
            return False
    
    def get_performance_stats(self) -> Dict:
        """Retorna estatísticas de performance"""
        try:
            if not self.performance_history:
                return {
                    'total_trades': 0,
                    'success_rate': 0.0,
                    'avg_profit': 0.0,
                    'total_profit': 0.0
                }
            
            total = len(self.performance_history)
            successes = sum(1 for h in self.performance_history if h['success'])
            profits = [h['profit'] for h in self.performance_history]
            
            return {
                'total_trades': total,
                'success_rate': (successes / total * 100) if total > 0 else 0.0,
                'avg_profit': np.mean(profits) if profits else 0.0,
                'total_profit': sum(profits),
                'is_trained': self.is_trained,
                'training_samples': len(self.training_data)
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular stats: {e}")
            return {}
    
    def optimize_parameters(self) -> Dict:
        """Otimiza parâmetros baseado em performance histórica"""
        try:
            if len(self.performance_history) < 50:
                return {}
            
            df = pd.DataFrame(self.performance_history)
            
            # Análise de horários mais lucrativos
            df['hour'] = pd.to_datetime(df['timestamp'], unit='s').dt.hour
            hourly_profit = df.groupby('hour')['profit'].mean()
            best_hours = hourly_profit.nlargest(5).index.tolist()
            
            # Análise de profit percentage ótimo
            successful = df[df['success'] == True]
            if len(successful) > 0:
                optimal_min_profit = successful['profit_pct'].quantile(0.25)
            else:
                optimal_min_profit = BotConfig.MIN_PROFIT_PERCENTAGE
            
            recommendations = {
                'best_hours': best_hours,
                'recommended_min_profit_pct': optimal_min_profit,
                'avg_success_rate': df['success'].mean() * 100
            }
            
            logger.info(f"🎯 Recomendações otimizadas: {recommendations}")
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Erro ao otimizar parâmetros: {e}")
            return {}

    def should_execute(self, opportunity: Dict) -> Tuple[bool, float]:
        """
        Alias para predict_success (compatibilidade)
        
        Returns:
            (should_execute, confidence)
        """
        return self.predict_success(opportunity)
