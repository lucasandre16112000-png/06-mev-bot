"""
🧠 MOTOR DE IA AVANÇADO - VERSÃO TURBINADA
Sistema de Machine Learning com Deep Learning e Reinforcement Learning
Aprende sozinho e se aprimora continuamente
"""

import os
import pickle
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json

# Machine Learning tradicional
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# XGBoost (mais poderoso)
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("⚠️ XGBoost não disponível. Instale com: pip install xgboost")

# Deep Learning (opcional - para análise avançada)
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False
    print("ℹ️ PyTorch não disponível. Funcionalidade de Deep Learning desabilitada.")

from loguru import logger
from src.config.config import BotConfig

class ReinforcementLearningAgent:
    """
    Agente de Reinforcement Learning para otimização de decisões
    Aprende através de recompensas (lucros) e punições (perdas)
    """
    
    def __init__(self, state_size: int = 10, action_size: int = 2):
        self.state_size = state_size
        self.action_size = action_size  # 0 = não executar, 1 = executar
        
        # Q-Learning parameters
        self.learning_rate = 0.001
        self.gamma = 0.95  # Discount factor
        self.epsilon = 1.0  # Exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        
        # Q-table (estado -> ação -> valor)
        self.q_table = {}
        
        # Memória de experiências
        self.memory = []
        self.max_memory = 10000
    
    def get_state_key(self, state: np.ndarray) -> str:
        """Converte estado em chave para Q-table"""
        # Discretizar estado para usar como chave
        discretized = np.round(state, 2)
        return str(discretized.tolist())
    
    def get_q_value(self, state: np.ndarray, action: int) -> float:
        """Obtém valor Q para estado-ação"""
        state_key = self.get_state_key(state)
        if state_key not in self.q_table:
            self.q_table[state_key] = [0.0] * self.action_size
        return self.q_table[state_key][action]
    
    def set_q_value(self, state: np.ndarray, action: int, value: float):
        """Define valor Q para estado-ação"""
        state_key = self.get_state_key(state)
        if state_key not in self.q_table:
            self.q_table[state_key] = [0.0] * self.action_size
        self.q_table[state_key][action] = value
    
    def choose_action(self, state: np.ndarray) -> int:
        """Escolhe ação usando epsilon-greedy"""
        # Exploração vs Exploração
        if np.random.random() < self.epsilon:
            return np.random.randint(self.action_size)
        
        # Escolher melhor ação
        q_values = [self.get_q_value(state, a) for a in range(self.action_size)]
        return np.argmax(q_values)
    
    def learn(self, state: np.ndarray, action: int, reward: float, next_state: np.ndarray):
        """Atualiza Q-values baseado em experiência"""
        # Q-Learning update rule
        current_q = self.get_q_value(state, action)
        
        # Melhor Q-value do próximo estado
        next_q_values = [self.get_q_value(next_state, a) for a in range(self.action_size)]
        max_next_q = max(next_q_values)
        
        # Nova estimativa
        new_q = current_q + self.learning_rate * (reward + self.gamma * max_next_q - current_q)
        
        self.set_q_value(state, action, new_q)
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        # Armazenar experiência
        self.memory.append({
            'state': state,
            'action': action,
            'reward': reward,
            'next_state': next_state
        })
        
        if len(self.memory) > self.max_memory:
            self.memory.pop(0)
    
    def save(self, path: str):
        """Salva agente"""
        data = {
            'q_table': self.q_table,
            'epsilon': self.epsilon,
            'memory': self.memory[-1000:]  # Salvar últimas 1000 experiências
        }
        with open(path, 'wb') as f:
            pickle.dump(data, f)
    
    def load(self, path: str):
        """Carrega agente"""
        if os.path.exists(path):
            with open(path, 'rb') as f:
                data = pickle.load(f)
                self.q_table = data['q_table']
                self.epsilon = data['epsilon']
                self.memory = data.get('memory', [])
            return True
        return False


if PYTORCH_AVAILABLE:
    class NeuralNetworkPredictor(nn.Module):
        """
        Rede Neural para predição de sucesso de arbitragem
        Mais poderosa que modelos tradicionais para padrões complexos
        """
        
        def __init__(self, input_size: int = 15):
            super(NeuralNetworkPredictor, self).__init__()
            
            self.network = nn.Sequential(
                nn.Linear(input_size, 128),
                nn.ReLU(),
                nn.Dropout(0.3),
                nn.Linear(128, 64),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(64, 32),
                nn.ReLU(),
                nn.Linear(32, 1),
                nn.Sigmoid()
            )
        
        def forward(self, x):
            return self.network(x)
else:
    # Classe dummy se PyTorch não estiver disponível
    NeuralNetworkPredictor = None


class AdvancedMLEngine:
    """Motor de IA Avançado com múltiplos modelos e aprendizado contínuo"""
    
    def __init__(self):
        # Modelos tradicionais
        self.rf_model = None
        self.gb_model = None
        self.xgb_model = None
        
        # Deep Learning
        self.nn_model = None
        self.nn_optimizer = None
        self.nn_criterion = None
        
        # Reinforcement Learning
        self.rl_agent = ReinforcementLearningAgent()
        
        # Scalers
        self.scaler = RobustScaler()  # Mais robusto a outliers
        self.is_trained = False
        
        # Dados de treinamento
        self.training_data = []
        
        # Features expandidas
        self.feature_names = [
            # Básicas
            'price_diff_pct',
            'amount_usd',
            'gas_price_gwei',
            'liquidity_score',
            
            # Temporais
            'hour_of_day',
            'day_of_week',
            'is_weekend',
            'time_since_last_trade',
            
            # Rede/DEX
            'network_priority',
            'dex_reliability_buy',
            'dex_reliability_sell',
            
            # Avançadas
            'volatility_score',
            'market_momentum',
            'gas_trend',
            'success_rate_last_hour'
        ]
        
        # Histórico de performance
        self.performance_history = []
        self.hourly_stats = {}
        self.last_trade_time = None
        
        # Configurações de ensemble
        self.model_weights = {
            'rf': 0.25,
            'gb': 0.25,
            'xgb': 0.30,
            'nn': 0.20
        }
        
        # Auto-tuning
        self.best_params = {}
        self.tuning_history = []
        
        # Carregar modelos salvos
        self._load_all_models()
    
    def _load_all_models(self):
        """Carrega todos os modelos salvos"""
        try:
            model_dir = "data/ml_models"
            os.makedirs(model_dir, exist_ok=True)
            
            # Modelos tradicionais
            if os.path.exists(f"{model_dir}/rf_model.pkl"):
                with open(f"{model_dir}/rf_model.pkl", 'rb') as f:
                    self.rf_model = pickle.load(f)
                logger.info("✅ Random Forest carregado")
            
            if os.path.exists(f"{model_dir}/gb_model.pkl"):
                with open(f"{model_dir}/gb_model.pkl", 'rb') as f:
                    self.gb_model = pickle.load(f)
                logger.info("✅ Gradient Boosting carregado")
            
            if XGBOOST_AVAILABLE and os.path.exists(f"{model_dir}/xgb_model.pkl"):
                with open(f"{model_dir}/xgb_model.pkl", 'rb') as f:
                    self.xgb_model = pickle.load(f)
                logger.info("✅ XGBoost carregado")
            
            # Scaler
            if os.path.exists(f"{model_dir}/scaler.pkl"):
                with open(f"{model_dir}/scaler.pkl", 'rb') as f:
                    self.scaler = pickle.load(f)
            
            # Neural Network
            if PYTORCH_AVAILABLE and os.path.exists(f"{model_dir}/nn_model.pth"):
                self.nn_model = NeuralNetworkPredictor(len(self.feature_names))
                self.nn_model.load_state_dict(torch.load(f"{model_dir}/nn_model.pth"))
                self.nn_model.eval()
                logger.info("✅ Neural Network carregada")
            
            # RL Agent
            self.rl_agent.load(f"{model_dir}/rl_agent.pkl")
            
            # Histórico
            if os.path.exists(f"{model_dir}/training_data.pkl"):
                with open(f"{model_dir}/training_data.pkl", 'rb') as f:
                    self.training_data = pickle.load(f)
                logger.info(f"✅ {len(self.training_data)} amostras de treino carregadas")
            
            if any([self.rf_model, self.gb_model, self.xgb_model, self.nn_model]):
                self.is_trained = True
                logger.success("✅ Modelos ML carregados com sucesso!")
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao carregar modelos: {e}")
    
    def _save_all_models(self):
        """Salva todos os modelos"""
        try:
            model_dir = "data/ml_models"
            os.makedirs(model_dir, exist_ok=True)
            
            if self.rf_model:
                with open(f"{model_dir}/rf_model.pkl", 'wb') as f:
                    pickle.dump(self.rf_model, f)
            
            if self.gb_model:
                with open(f"{model_dir}/gb_model.pkl", 'wb') as f:
                    pickle.dump(self.gb_model, f)
            
            if self.xgb_model:
                with open(f"{model_dir}/xgb_model.pkl", 'wb') as f:
                    pickle.dump(self.xgb_model, f)
            
            with open(f"{model_dir}/scaler.pkl", 'wb') as f:
                pickle.dump(self.scaler, f)
            
            if PYTORCH_AVAILABLE and self.nn_model:
                torch.save(self.nn_model.state_dict(), f"{model_dir}/nn_model.pth")
            
            self.rl_agent.save(f"{model_dir}/rl_agent.pkl")
            
            with open(f"{model_dir}/training_data.pkl", 'wb') as f:
                pickle.dump(self.training_data[-10000:], f)  # Últimas 10k amostras
            
            logger.info("💾 Todos os modelos salvos!")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar modelos: {e}")
    
    def extract_features(self, opportunity: Dict) -> np.ndarray:
        """Extrai features AVANÇADAS de uma oportunidade"""
        try:
            now = datetime.now()
            
            # Network priority
            network_priority_map = {
                'base': 0.60, 'base_sepolia': 0.60,
                'arbitrum': 0.25, 'arbitrum_sepolia': 0.25,
                'bsc': 0.15, 'bsc_testnet': 0.15
            }
            
            # DEX reliability
            dex_reliability_map = {
                'uniswap_v3': 0.95, 'pancakeswap': 0.90,
                'aerodrome': 0.85, 'camelot': 0.80, 'sushiswap': 0.75
            }
            
            # Calcular features avançadas
            time_since_last = 0
            if self.last_trade_time:
                time_since_last = (now - self.last_trade_time).total_seconds() / 60
            
            # Volatilidade (baseada em histórico recente)
            volatility = self._calculate_volatility()
            
            # Momentum de mercado
            momentum = self._calculate_market_momentum()
            
            # Tendência de gas
            gas_trend = self._calculate_gas_trend()
            
            # Taxa de sucesso última hora
            success_rate = self._get_recent_success_rate(hours=1)
            
            features = [
                opportunity.get('profit_percentage', 0),  # price_diff_pct
                opportunity.get('amount_in', 0) / 1e6,  # amount_usd
                50.0,  # gas_price_gwei (placeholder)
                0.8,  # liquidity_score (placeholder)
                now.hour,  # hour_of_day
                now.weekday(),  # day_of_week
                1 if now.weekday() >= 5 else 0,  # is_weekend
                time_since_last,  # time_since_last_trade
                network_priority_map.get(opportunity.get('network', ''), 0.5),
                dex_reliability_map.get(opportunity.get('buy_dex', ''), 0.7),
                dex_reliability_map.get(opportunity.get('sell_dex', ''), 0.7),
                volatility,  # volatility_score
                momentum,  # market_momentum
                gas_trend,  # gas_trend
                success_rate  # success_rate_last_hour
            ]
            
            return np.array(features).reshape(1, -1)
            
        except Exception as e:
            logger.error(f"❌ Erro ao extrair features: {e}")
            return np.zeros((1, len(self.feature_names)))
    
    def predict_success(self, opportunity: Dict) -> Tuple[bool, float]:
        """
        Predição AVANÇADA usando ensemble de modelos + RL
        
        Returns:
            (should_execute, confidence)
        """
        try:
            # Extrair features
            features = self.extract_features(opportunity)
            
            # Se não treinado, usar heurística
            if not self.is_trained:
                return self._heuristic_decision(opportunity)
            
            # Normalizar
            features_scaled = self.scaler.transform(features)
            
            # ENSEMBLE: Combinar predições de múltiplos modelos
            predictions = []
            confidences = []
            
            # Random Forest
            if self.rf_model:
                rf_pred = self.rf_model.predict_proba(features_scaled)[0][1]
                predictions.append(rf_pred)
                confidences.append(self.model_weights['rf'])
            
            # Gradient Boosting
            if self.gb_model:
                gb_pred = self.gb_model.predict_proba(features_scaled)[0][1]
                predictions.append(gb_pred)
                confidences.append(self.model_weights['gb'])
            
            # XGBoost
            if XGBOOST_AVAILABLE and self.xgb_model:
                xgb_pred = self.xgb_model.predict_proba(features_scaled)[0][1]
                predictions.append(xgb_pred)
                confidences.append(self.model_weights['xgb'])
            
            # Neural Network
            if PYTORCH_AVAILABLE and self.nn_model:
                with torch.no_grad():
                    nn_input = torch.FloatTensor(features_scaled)
                    nn_pred = self.nn_model(nn_input).item()
                    predictions.append(nn_pred)
                    confidences.append(self.model_weights['nn'])
            
            # Weighted ensemble
            if predictions:
                total_weight = sum(confidences)
                ensemble_confidence = sum(p * w for p, w in zip(predictions, confidences)) / total_weight
            else:
                ensemble_confidence = 0.5
            
            # Reinforcement Learning: ajuste final
            rl_action = self.rl_agent.choose_action(features_scaled[0])
            
            # Se RL diz não executar, reduzir confiança
            if rl_action == 0:
                ensemble_confidence *= 0.8
            
            # Decisão final
            should_execute = (
                ensemble_confidence >= BotConfig.ML_CONFIDENCE_THRESHOLD and
                rl_action == 1
            )
            
            logger.info(f"🧠 IA: Confiança={ensemble_confidence:.2%}, RL={rl_action}, Decisão={'EXECUTAR' if should_execute else 'PULAR'}")
            
            return should_execute, ensemble_confidence
            
        except Exception as e:
            logger.error(f"❌ Erro na predição: {e}")
            return False, 0.0
    
    def record_result(self, opportunity: Dict, success: bool, actual_profit: float):
        """Registra resultado e APRENDE com ele"""
        try:
            features = self.extract_features(opportunity)
            
            # Registrar para treinamento supervisionado
            self.training_data.append({
                'features': features.flatten(),
                'success': 1 if success else 0,
                'profit': actual_profit,
                'timestamp': datetime.now().timestamp()
            })
            
            # Reinforcement Learning: aprender com recompensa
            reward = actual_profit if success else -abs(actual_profit)
            
            # Normalizar recompensa (-1 a 1)
            normalized_reward = np.tanh(reward / 100)
            
            # Estado atual
            current_state = features.flatten()
            
            # Próximo estado (simplificado - em produção seria o estado após a ação)
            next_state = current_state.copy()
            
            # Ação tomada (1 = executou, 0 = não executou)
            action = 1 if success else 0
            
            # RL aprende
            self.rl_agent.learn(current_state, action, normalized_reward, next_state)
            
            # Atualizar histórico
            self.performance_history.append({
                'timestamp': datetime.now().timestamp(),
                'success': success,
                'profit': actual_profit,
                'profit_pct': opportunity.get('profit_percentage', 0)
            })
            
            self.last_trade_time = datetime.now()
            
            # Auto-retreinar periodicamente
            if len(self.training_data) >= BotConfig.ML_MIN_TRAINING_SAMPLES:
                if len(self.training_data) % BotConfig.ML_TRAINING_INTERVAL == 0:
                    logger.info("🔄 Auto-retreinamento iniciado...")
                    self.train()
            
        except Exception as e:
            logger.error(f"❌ Erro ao registrar resultado: {e}")
    
    def train(self) -> bool:
        """Treina TODOS os modelos"""
        try:
            if len(self.training_data) < BotConfig.ML_MIN_TRAINING_SAMPLES:
                logger.warning(f"⚠️ Dados insuficientes: {len(self.training_data)}/{BotConfig.ML_MIN_TRAINING_SAMPLES}")
                return False
            
            logger.info(f"🎓 Treinando IA com {len(self.training_data)} amostras...")
            
            # Preparar dados
            X = np.array([d['features'] for d in self.training_data])
            y = np.array([d['success'] for d in self.training_data])
            
            # Split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Normalizar
            self.scaler.fit(X_train)
            X_train_scaled = self.scaler.transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            scores = {}
            
            # 1. Random Forest com GridSearch
            logger.info("  🌲 Treinando Random Forest...")
            rf_params = {
                'n_estimators': [100, 200],
                'max_depth': [10, 20, None],
                'min_samples_split': [2, 5]
            }
            rf_grid = GridSearchCV(RandomForestClassifier(random_state=42), rf_params, cv=3, n_jobs=-1)
            rf_grid.fit(X_train_scaled, y_train)
            self.rf_model = rf_grid.best_estimator_
            scores['rf'] = self.rf_model.score(X_test_scaled, y_test)
            logger.info(f"    ✅ RF Accuracy: {scores['rf']:.2%}")
            
            # 2. Gradient Boosting
            logger.info("  📈 Treinando Gradient Boosting...")
            self.gb_model = GradientBoostingClassifier(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
            self.gb_model.fit(X_train_scaled, y_train)
            scores['gb'] = self.gb_model.score(X_test_scaled, y_test)
            logger.info(f"    ✅ GB Accuracy: {scores['gb']:.2%}")
            
            # 3. XGBoost (se disponível)
            if XGBOOST_AVAILABLE:
                logger.info("  🚀 Treinando XGBoost...")
                self.xgb_model = xgb.XGBClassifier(
                    n_estimators=200,
                    max_depth=6,
                    learning_rate=0.1,
                    random_state=42,
                    use_label_encoder=False,
                    eval_metric='logloss'
                )
                self.xgb_model.fit(X_train_scaled, y_train)
                scores['xgb'] = self.xgb_model.score(X_test_scaled, y_test)
                logger.info(f"    ✅ XGB Accuracy: {scores['xgb']:.2%}")
            
            # 4. Neural Network (se disponível)
            if PYTORCH_AVAILABLE:
                logger.info("  🧠 Treinando Neural Network...")
                self.nn_model = NeuralNetworkPredictor(X_train_scaled.shape[1])
                self.nn_optimizer = optim.Adam(self.nn_model.parameters(), lr=0.001)
                self.nn_criterion = nn.BCELoss()
                
                # Treinar
                epochs = 50
                batch_size = 32
                
                for epoch in range(epochs):
                    self.nn_model.train()
                    for i in range(0, len(X_train_scaled), batch_size):
                        batch_X = torch.FloatTensor(X_train_scaled[i:i+batch_size])
                        batch_y = torch.FloatTensor(y_train[i:i+batch_size]).reshape(-1, 1)
                        
                        self.nn_optimizer.zero_grad()
                        outputs = self.nn_model(batch_X)
                        loss = self.nn_criterion(outputs, batch_y)
                        loss.backward()
                        self.nn_optimizer.step()
                
                # Avaliar
                self.nn_model.eval()
                with torch.no_grad():
                    test_outputs = self.nn_model(torch.FloatTensor(X_test_scaled))
                    predictions = (test_outputs.numpy() > 0.5).astype(int).flatten()
                    scores['nn'] = accuracy_score(y_test, predictions)
                logger.info(f"    ✅ NN Accuracy: {scores['nn']:.2%}")
            
            self.is_trained = True
            
            # Salvar tudo
            self._save_all_models()
            
            # Estatísticas
            best_model = max(scores.items(), key=lambda x: x[1])
            logger.success(f"✅ Treinamento completo! Melhor modelo: {best_model[0].upper()} ({best_model[1]:.2%})")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro no treinamento: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _heuristic_decision(self, opportunity: Dict) -> Tuple[bool, float]:
        """Decisão heurística quando não treinado"""
        profit_pct = opportunity.get('profit_percentage', 0)
        
        if profit_pct >= 2.0:
            return True, 0.9
        elif profit_pct >= 1.5:
            return True, 0.75
        elif profit_pct >= 1.0:
            return True, 0.6
        else:
            return False, 0.3
    
    def _calculate_volatility(self) -> float:
        """Calcula volatilidade baseada em histórico recente"""
        if len(self.performance_history) < 10:
            return 0.5
        
        recent = self.performance_history[-20:]
        profits = [h['profit_pct'] for h in recent]
        return float(np.std(profits)) / 10.0
    
    def _calculate_market_momentum(self) -> float:
        """Calcula momentum do mercado"""
        if len(self.performance_history) < 5:
            return 0.5
        
        recent = self.performance_history[-10:]
        success_rate = sum(1 for h in recent if h['success']) / len(recent)
        return float(success_rate)
    
    def _calculate_gas_trend(self) -> float:
        """Calcula tendência de gas prices"""
        # Placeholder - em produção, analisar histórico de gas
        return 0.5
    
    def _get_recent_success_rate(self, hours: int = 1) -> float:
        """Taxa de sucesso nas últimas N horas"""
        if not self.performance_history:
            return 0.5
        
        cutoff = datetime.now().timestamp() - (hours * 3600)
        recent = [h for h in self.performance_history if h['timestamp'] >= cutoff]
        
        if not recent:
            return 0.5
        
        return sum(1 for h in recent if h['success']) / len(recent)
    
    def get_performance_stats(self) -> Dict:
        """Estatísticas de performance"""
        if not self.performance_history:
            return {
                'total_trades': 0,
                'success_rate': 0.0,
                'avg_profit': 0.0,
                'total_profit': 0.0,
                'is_trained': self.is_trained,
                'training_samples': len(self.training_data),
                'rl_epsilon': self.rl_agent.epsilon
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
            'training_samples': len(self.training_data),
            'rl_epsilon': self.rl_agent.epsilon,
            'best_hour': self._get_best_trading_hour(),
            'volatility': self._calculate_volatility(),
            'momentum': self._calculate_market_momentum()
        }
    
    def _get_best_trading_hour(self) -> int:
        """Retorna a melhor hora para trading"""
        if len(self.performance_history) < 24:
            return 12
        
        hourly_profits = {}
        for h in self.performance_history:
            hour = datetime.fromtimestamp(h['timestamp']).hour
            if hour not in hourly_profits:
                hourly_profits[hour] = []
            hourly_profits[hour].append(h['profit'])
        
        best_hour = max(hourly_profits.items(), key=lambda x: np.mean(x[1]))
        return best_hour[0]
    
    def should_execute(self, opportunity: Dict) -> Tuple[bool, float]:
        """Alias para predict_success"""
        return self.predict_success(opportunity)
