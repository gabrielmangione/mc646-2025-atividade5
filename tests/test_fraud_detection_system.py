# tests/test_fraud_detection_system.py

import pytest
from datetime import datetime, timedelta
from src.fraud.FraudDetectionSystem import FraudDetectionSystem
from src.fraud.Transaction import Transaction
from src.fraud.FraudCheckResult import FraudCheckResult

# Classe que agrupa todos os testes para o sistema de detecção de fraude
class TestFraudDetectionSystem:

    def setup_method(self):
        """
        Este método é executado antes de cada teste, garantindo que cada um 
        comece com uma nova instância do sistema.
        """
        self.system = FraudDetectionSystem()
        self.now = datetime.now()

    def test_caso_1_valor_elevado(self):
        """
        Testa a regra de fraude para transações com valor superior a 10.000.
        """
        # Parâmetros
        current_transaction = Transaction(
            amount=15000.00,
            timestamp=self.now,
            location="Brasil"
        )
        previous_transactions = []
        blacklisted_locations = []

        # Execução e Verificação
        result = self.system.check_for_fraud(current_transaction, previous_transactions, blacklisted_locations)

        assert result.is_fraudulent is True
        assert result.verification_required is True
        assert result.is_blocked is False
        assert result.risk_score == 50

    def test_caso_2_transacoes_excessivas(self):
        """
        Testa a regra de bloqueio por mais de 10 transações na última hora.
        O teste é configurado com 11 transações recentes para ativar a regra.
        """
        # Parâmetros
        current_transaction = Transaction(
            amount=500.00,
            timestamp=self.now,
            location="Brasil"
        )
        # Cria 11 transações nos últimos 59 minutos
        previous_transactions = [
            Transaction( 50.0, self.now - timedelta(minutes=i*5), "Brasil") for i in range(1, 12)
        ]
        # Adiciona uma transação antiga que não deve ser contada
        previous_transactions.append(
            Transaction(100.0, self.now - timedelta(minutes=601), "Brasil")
        )
        blacklisted_locations = []

        # Execução e Verificação
        result = self.system.check_for_fraud(current_transaction, previous_transactions, blacklisted_locations)

        assert result.is_blocked is True
        assert result.risk_score == 30
        # A regra de transações excessivas por si só não marca como fraude
        assert result.is_fraudulent is False 
        
    def test_caso_3_localizacao_recente_sem_fraude(self):
        """
        Testa o cenário onde há uma transação recente (< 30 min), mas na mesma localização,
        o que não deve ser considerado fraude.
        """
        # Parâmetros
        current_transaction = Transaction(
            amount=500.00,
            timestamp=self.now,
            location="Brasil"
        )
        previous_transactions = [
            Transaction(
                amount=200.00,
                timestamp=self.now - timedelta(minutes=15),
                location="Brasil"
            )
        ]
        blacklisted_locations = []

        # Execução e Verificação
        result = self.system.check_for_fraud(current_transaction, previous_transactions, blacklisted_locations)

        assert result.is_fraudulent is False
        assert result.is_blocked is False
        assert result.verification_required is False
        assert result.risk_score == 0

    def test_caso_4_mudanca_rapida_localizacao(self):
        """
        Testa a regra de fraude por mudança rápida de localização (transação em
        local diferente em menos de 30 minutos).
        """
        # Parâmetros
        current_transaction = Transaction(
            amount=500.00,
            timestamp=self.now,
            location="Brasil"
        )
        previous_transactions = [
            Transaction(
                amount=200.00,
                timestamp=self.now - timedelta(minutes=15),
                location="EUA"
            )
        ]
        blacklisted_locations = []

        # Execução e Verificação
        result = self.system.check_for_fraud(current_transaction, previous_transactions, blacklisted_locations)

        assert result.is_fraudulent is True
        assert result.verification_required is True
        assert result.is_blocked is False
        assert result.risk_score == 20

    def test_caso_5_localizacao_em_blacklist(self):
        """
        Testa a regra de bloqueio imediato e score máximo para transações em
        locais na lista de restrição.
        """
        # Parâmetros
        current_transaction = Transaction(
            amount=500.00,
            timestamp=self.now,
            location="Brasil"
        )
        previous_transactions = []
        blacklisted_locations = ["Brasil", "País de Alto Risco"]

        # Execução e Verificação
        result = self.system.check_for_fraud(current_transaction, previous_transactions, blacklisted_locations)

        assert result.is_blocked is True
        assert result.risk_score == 100
        # A regra da blacklist por si só não marca como fraude, apenas bloqueia
        assert result.is_fraudulent is False