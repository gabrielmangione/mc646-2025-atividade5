import pytest
from datetime import datetime
from src.energy.DeviceSchedule import DeviceSchedule
from src.energy.EnergyManagementSystem import SmartEnergyManagementSystem
from src.energy.EnergyManagementResult import EnergyManagementResult


class TestDeviceSchedule:
    """Test suite for the DeviceSchedule class."""
    
    def test_device_schedule_initialization(self):
        """Test that DeviceSchedule can be initialized with device name and scheduled time."""
        # Arrange
        device_name = "Smart Thermostat"
        scheduled_time = datetime(2025, 10, 2, 14, 30, 0)
        
        # Act
        device_schedule = DeviceSchedule(device_name, scheduled_time)
        
        # Assert
        assert device_schedule.device_name == device_name
        assert device_schedule.scheduled_time == scheduled_time
    
    def test_device_schedule_repr(self):
        """Test the string representation of DeviceSchedule."""
        # Arrange
        device_name = "LED Light"
        scheduled_time = datetime(2025, 10, 2, 18, 0, 0)
        device_schedule = DeviceSchedule(device_name, scheduled_time)
        
        # Act
        repr_string = repr(device_schedule)
        
        # Assert
        expected_repr = f"DeviceSchedule(device_name='LED Light', scheduled_time='{scheduled_time}')"
        assert repr_string == expected_repr
    
    def test_normal_energy_mode(self):
        """Test that the system does not enter energy saving mode or temperature regulation when conditions are normal."""
        # Arrange
        system = SmartEnergyManagementSystem()

        # Act   
        result = system.manage_energy(
            current_price=0.15,
            price_threshold=0.20,
            device_priorities={"Luzes": 2, "Aquecimento": 1},
            current_time=datetime(2024, 10, 1, 12, 0),
            current_temperature=22.0,
            desired_temperature_range=[20.0, 24.0],
            energy_usage_limit=30,
            total_energy_used_today=10,
            scheduled_devices=[]
        )

        # Assert
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

    def test_energy_saving_mode_turns_off_low_priority_devices(self):
        """Test that energy saving mode turns off low priority devices when price exceeds threshold."""
        # Arrange
        system = SmartEnergyManagementSystem()

        # Act
        result = system.manage_energy(
            current_price=0.25,
            price_threshold=0.20,
            device_priorities={"Aquecimento": 1, "Luzes": 2},
            current_time=datetime(2024, 10, 1, 14, 0),
            current_temperature=22.0,
            desired_temperature_range=[20.0, 24.0],
            energy_usage_limit=50,
            total_energy_used_today=20,
            scheduled_devices=[]
        )

        # Assert 
        assert result.energy_saving_mode is True
        assert result.device_status["Aquecimento"] is True
        assert result.device_status["Luzes"] is False

    def test_temperature_regulation_heating_on(self):
        """Test that heating turns on when current temperature is below desired range."""
        # Arrange
        system = SmartEnergyManagementSystem()

        # Act
        result = system.manage_energy(
            current_price=0.15,
            price_threshold=0.20,
            device_priorities={},
            current_time=datetime(2024, 10, 1, 10, 0),
            current_temperature=18.0,
            desired_temperature_range=[20.0, 24.0],
            energy_usage_limit=40,
            total_energy_used_today=15,
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
            device_priorities={},
            current_time=datetime(2024, 10, 1, 15, 0),
            current_temperature=26.0,
            desired_temperature_range=[20.0, 24.0],
            energy_usage_limit=40,
            total_energy_used_today=15,
            scheduled_devices=[]
        )

        # Assert
        assert result.temperature_regulation_active is True
        assert result.device_status["Cooling"] is True

    def test_energy_usage_limit_turns_off_low_priority_first(self):
        """Test that exceeding energy usage limit turns off low priority devices first."""
        # Arrange
        system = SmartEnergyManagementSystem()

        # Act
        result = system.manage_energy(
            current_price=0.10,
            price_threshold=0.20,
            device_priorities={"Aquecimento": 1, "Luzes": 2, "TV": 3},
            current_time=datetime(2024, 10, 1, 17, 0),
            current_temperature=22.0,
            desired_temperature_range=[20.0, 24.0],
            energy_usage_limit=30,
            total_energy_used_today=31,
            scheduled_devices=[]
        )
        assert result.device_status["TV"] is False
        assert result.device_status["Luzes"] is False

    def test_scheduled_device_turns_on_at_correct_time(self):
        """Test that a scheduled device turns on at its scheduled time."""
        # Arrange
        system = SmartEnergyManagementSystem()
        schedule = DeviceSchedule(device_name="Forno", scheduled_time=datetime(2024, 10, 1, 18, 0))
        
        # Act
        result = system.manage_energy(
            current_price=0.25,
            price_threshold=0.20,
            device_priorities={"Forno": 3},
            current_time=datetime(2024, 10, 1, 18, 0),
            current_temperature=22.0,
            desired_temperature_range=[20.0, 24.0],
            energy_usage_limit=50,
            total_energy_used_today=20,
            scheduled_devices=[schedule]
        )

        # Assert
        assert result.device_status["Forno"] is True

