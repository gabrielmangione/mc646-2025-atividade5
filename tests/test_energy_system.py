import pytest
from datetime import datetime
from src.energy.DeviceSchedule import DeviceSchedule
from src.energy.EnergyManagementSystem import SmartEnergyManagementSystem
from src.energy.EnergyManagementResult import EnergyManagementResult


class TestEnergyManagementSystem:

    def test_normal_mode_pure(self):
        """Baseline: verifies normal operation without any special conditions."""
        system = SmartEnergyManagementSystem()
        schedule = DeviceSchedule(device_name="TV", scheduled_time=datetime(2024, 10, 1, 18, 0))

        result = system.manage_energy(
            current_price=0.15,
            price_threshold=0.20,
            device_priorities={"Luzes": 2, "Aquecimento": 1},
            current_time=datetime(2024, 10, 1, 10, 0),  # diferente do schedule
            current_temperature=22.0,
            desired_temperature_range=[20.0, 24.0],
            energy_usage_limit=40,
            total_energy_used_today=10,
            scheduled_devices=[schedule]    
        )

        assert result.energy_saving_mode is False
        assert result.temperature_regulation_active is False

    def test_night_mode_only_security_and_fridge_on(self):
        """Test that during night mode only security systems and refrigerator remain on."""
        # Arrange
        system = SmartEnergyManagementSystem()

        # Act
        result = system.manage_energy(
            current_price=0.10,
            price_threshold=0.20,
            device_priorities={"Security": 1, "Refrigerator": 1, "Luzes": 2},
            current_time=datetime(2024, 10, 1, 23, 30),
            current_temperature=22.0,
            desired_temperature_range=[20.0, 24.0],
            energy_usage_limit=30,
            total_energy_used_today=5,
            scheduled_devices=[]
        )

        # Assert
        assert result.device_status["Security"] is True
        assert result.device_status["Refrigerator"] is True
        assert result.device_status["Luzes"] is False

    def test_energy_saving_mode_with_scheduled_device(self):
        """Test energy saving mode combined with scheduled device activation."""
        system = SmartEnergyManagementSystem()
        schedule = DeviceSchedule(device_name="Forno", scheduled_time=datetime(2024, 10, 1, 18, 0))
        
        result = system.manage_energy(
            current_price=0.25,  
            price_threshold=0.20,
            device_priorities={"Aquecimento": 1, "Luzes": 2, "Forno": 3},
            current_time=datetime(2024, 10, 1, 18, 0),  # coincide com agendamento
            current_temperature=22.0,
            desired_temperature_range=[20.0, 24.0],
            energy_usage_limit=50,
            total_energy_used_today=20,
            scheduled_devices=[schedule]
        )

        
        assert result.energy_saving_mode is True
        assert result.device_status["Aquecimento"] is True
        assert result.device_status["Luzes"] is False        
        assert result.device_status["Forno"] is True         

    def test_temperature_regulation_heating_on(self):
        """Test that heating turns on when current temperature is below desired range."""
        # Arrange
        system = SmartEnergyManagementSystem()

        # Act
        result = system.manage_energy(
            current_price=0.15,
            price_threshold=0.20,
            device_priorities={"Aquecimento": 1, "Luzes": 2, "TV": 3}, 
            current_time=datetime(2024, 10, 1, 10, 0),
            current_temperature=18.0,
            desired_temperature_range=[20.0, 24.0],
            energy_usage_limit=40,
            total_energy_used_today=40,
            scheduled_devices=[]
        )

        # Assert
        assert result.temperature_regulation_active is True
        assert result.device_status["Heating"] is True


    def test_temperature_regulation_cooling_on(self):
        """Test that cooling turns on when current temperature is above desired range."""
        # Arrange
        system = SmartEnergyManagementSystem()

        # Act
        result = system.manage_energy(
            current_price=0.15,
            price_threshold=0.20,
            device_priorities={"Aquecimento": 1, "Luzes": 1}, # todos os dispositivos com prioridade 1, forçando a aresta 17-18 e 18-16
            current_time=datetime(2024, 10, 1, 15, 0),
            current_temperature=26.0,
            desired_temperature_range=[20.0, 24.0],
            energy_usage_limit=30,
            total_energy_used_today=31,
            scheduled_devices=[]
        )

        # Assert
        assert result.temperature_regulation_active is True
        assert result.device_status["Cooling"] is True

    def test_normal_mode_with_energy_limit(self):
        """Test normal mode behavior and energy limit enforcement combined."""
        system = SmartEnergyManagementSystem()
        
        result = system.manage_energy(
            current_price=0.15,
            price_threshold=0.20,
            device_priorities={"Aquecimento": 1, "Luzes": 2, "TV": 3},
            current_time=datetime(2024, 10, 1, 12, 0),
            current_temperature=22.0,
            desired_temperature_range=[20.0, 24.0],
            energy_usage_limit=30,
            total_energy_used_today=31,  
            scheduled_devices=[]
        )

        
        assert result.energy_saving_mode is False
        assert result.device_status["Aquecimento"] is True  
        assert result.device_status["Luzes"] is False        
        assert result.device_status["TV"] is False           

    def test_price_exactly_at_threshold(self):
        """Testa quando o preço é exatamente igual ao threshold."""
        system = SmartEnergyManagementSystem()
        result = system.manage_energy(
            current_price=0.20,  
            price_threshold=0.20,
            device_priorities={"Luzes": 2, "Aquecimento": 1},
            current_time=datetime(2024, 10, 1, 10, 0),
            current_temperature=22.0,
            desired_temperature_range=[20.0, 24.0],
            energy_usage_limit=40,
            total_energy_used_today=10,
            scheduled_devices=[]
        )
        assert result.energy_saving_mode is False  

    def test_modo_noturno_ass_6am(self):
        """Testa às 6h da manhã - limite do modo noturno."""
        system = SmartEnergyManagementSystem()
        result = system.manage_energy(
            current_price=0.10,
            price_threshold=0.20,
            device_priorities={"Security": 1, "Luzes": 2},
            current_time=datetime(2024, 10, 1, 6, 0), 
            current_temperature=22.0,
            desired_temperature_range=[20.0, 24.0],
            energy_usage_limit=30,
            total_energy_used_today=5,
            scheduled_devices=[]
        )
        
        assert result.device_status["Luzes"] is True

    def test_temperatura_exatamente_no_lmimte_inferior(self):
        """Testa temperatura exatamente no limite inferior."""
        system = SmartEnergyManagementSystem()
        result = system.manage_energy(
            current_price=0.15,
            price_threshold=0.20,
            device_priorities={"Luzes": 2},
            current_time=datetime(2024, 10, 1, 10, 0),
            current_temperature=20.0,  
            desired_temperature_range=[20.0, 24.0],
            energy_usage_limit=40,
            total_energy_used_today=10,
            scheduled_devices=[]
        )
        assert result.device_status.get("Heating", False) is False  

    def test_temperatura_exatamente_no_lmimte_superior(self):
        """Testa temperatura exatamente no limite superior."""
        system = SmartEnergyManagementSystem()
        result = system.manage_energy(
            current_price=0.15,
            price_threshold=0.20,
            device_priorities={"Luzes": 2},
            current_time=datetime(2024, 10, 1, 10, 0),
            current_temperature=24.0,  
            desired_temperature_range=[20.0, 24.0],
            energy_usage_limit=40,
            total_energy_used_today=10,
            scheduled_devices=[]
        )
        assert result.device_status.get("Cooling", False) is False  

    def test_temperatura_para_desligar_Heating_e_Cooling(self):
        """Testa que Heating e Cooling são desligados quando temperatura está ok."""
        system = SmartEnergyManagementSystem()
        
        result = system.manage_energy(
            current_price=0.15,
            price_threshold=0.20,
            device_priorities={"Luzes": 2, "Heating": 1, "Cooling": 1},
            current_time=datetime(2024, 10, 1, 10, 0),
            current_temperature=22.0,  # dentro da faixa
            desired_temperature_range=[20.0, 24.0],
            energy_usage_limit=40,
            total_energy_used_today=10,
            scheduled_devices=[]
        )
       
        assert "Heating" in result.device_status
        assert "Cooling" in result.device_status
        assert result.device_status["Heating"] is False
        assert result.device_status["Cooling"] is False

    def test_energia_exatamente_no_limite(self):
        """Testa quando energia usada é exatamente igual ao limite."""
        system = SmartEnergyManagementSystem()
        result = system.manage_energy(
            current_price=0.15,
            price_threshold=0.20,
            device_priorities={"Aquecimento": 1, "Luzes": 2},
            current_time=datetime(2024, 10, 1, 12, 0),
            current_temperature=22.0,
            desired_temperature_range=[20.0, 24.0],
            energy_usage_limit=30,
            total_energy_used_today=30,  
            scheduled_devices=[]
        )
        
        assert result.device_status["Luzes"] is False

    def test_reducao_de_energia_para_abaixo_do_limite(self):
        """Testa que o loop para quando fica abaixo do limite."""
        system = SmartEnergyManagementSystem()
        result = system.manage_energy(
            current_price=0.15,
            price_threshold=0.20,
            device_priorities={"Device1": 2, "Device2": 3, "Device3": 4, "Priority1": 1},
            current_time=datetime(2024, 10, 1, 12, 0),
            current_temperature=22.0,
            desired_temperature_range=[20.0, 24.0],
            energy_usage_limit=30,
            total_energy_used_today=33,  # 3 acima do limite
            scheduled_devices=[]
        )
        
        assert result.device_status["Device1"] is False
        assert result.device_status["Device2"] is False
        assert result.device_status["Device3"] is False
        assert result.total_energy_used == 30  # exatamente no limite