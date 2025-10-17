import pytest
from datetime import datetime, timedelta
from src.flight.FlightBookingSystem import FlightBookingSystem

class TestFlightBookingSystem:
    """Tests for FlightBookingSystem ensuring full edge coverage of the control-flow graph."""

    def setup_method(self):
        """Set up initial configuration for each test."""
        self.system = FlightBookingSystem()
        self.base_time = datetime(2024, 1, 15, 10, 0, 0)  # Base datetime for tests

    def test_passengers_exceed_available_seats(self):
        """
        Test to cover edge 1->2: passengers > available_seats
        Should return confirmation=False when there are not enough seats.
        """
        result = self.system.book_flight(
            passengers=5,
            booking_time=self.base_time,
            available_seats=3,
            current_price=100.0,
            previous_sales=50,
            is_cancellation=False,
            departure_time=self.base_time + timedelta(hours=48),
            reward_points_available=0
        )
        
        assert result.confirmation is False
        assert result.total_price == 0.0
        assert result.refund_amount == 0.0
        assert result.points_used is False

    def test_booking_with_last_minute_fee_and_group_discount_and_points(self):
        """
        Test to cover multiple edges in sequence:
        - 1->3: passengers <= available_seats
        - 3->4: hours_to_departure < 24 (last-minute fee)
        - 5->6: passengers > 4 (group discount)
        - 7->8: reward_points_available > 0 (use points)
        - 9->11: final_price >= 0 (normal price)
        - 11->13: is_cancellation = False (normal booking)
        """
        result = self.system.book_flight(
            passengers=6,
            booking_time=self.base_time,
            available_seats=10,
            current_price=200.0,
            previous_sales=30,
            is_cancellation=False,
            departure_time=self.base_time + timedelta(hours=12),
            reward_points_available=50
        )
        
        # Expected calculation:
        # price_factor = (30/100) * 0.8 = 0.24
        # final_price = 200 * 0.24 * 6 = 288
        # + 100 (last-minute fee) = 388
        # * 0.95 (group discount) = 368.6
        # - 50 * 0.01 (points) = 368.1
        
        assert result.confirmation is True
        assert abs(result.total_price - 368.1) < 0.01
        assert result.refund_amount == 0.0
        assert result.points_used is True

    def test_booking_without_last_minute_fee_no_group_discount_no_points(self):
        """
        Test to cover the 'default' path with no special conditions:
        - 3->5: hours_to_departure >= 24 (no last-minute fee)
        - 5->7: passengers <= 4 (no group discount)
        - 7->9: reward_points_available <= 0 (no points)
        """
        result = self.system.book_flight(
            passengers=2,
            booking_time=self.base_time,
            available_seats=10,
            current_price=150.0,
            previous_sales=60,
            is_cancellation=False,
            departure_time=self.base_time + timedelta(hours=48),
            reward_points_available=0
        )
        
        # Expected calculation:
        # price_factor = (60/100) * 0.8 = 0.48
        # final_price = 150 * 0.48 * 2 = 144
        
        assert result.confirmation is True
        assert abs(result.total_price - 144.0) < 0.01
        assert result.refund_amount == 0.0
        assert result.points_used is False

    def test_booking_with_negative_price_adjustment(self):
        """
        Test to cover edge 9->10: final_price < 0
        Should adjust the price to 0 if it becomes negative due to points.
        """
        result = self.system.book_flight(
            passengers=1,
            booking_time=self.base_time,
            available_seats=10,
            current_price=10.0,
            previous_sales=10,
            is_cancellation=False,
            departure_time=self.base_time + timedelta(hours=48),
            reward_points_available=2000
        )
        
        # Expected calculation:
        # price_factor = (10/100) * 0.8 = 0.08
        # final_price = 10 * 0.08 * 1 = 0.8
        # - 2000 * 0.01 = -19.2 (negative)
        # Adjusted to 0
        
        assert result.confirmation is True
        assert result.total_price == 0.0
        assert result.refund_amount == 0.0
        assert result.points_used is True

    def test_cancellation_with_full_refund(self):
        """
        Test to cover cancellation edges:
        - 11->12: is_cancellation = True
        - 12->14: hours_to_departure >= 48 (full refund)
        - 14->17: return
        """
        result = self.system.book_flight(
            passengers=3,
            booking_time=self.base_time,
            available_seats=10,
            current_price=100.0,
            previous_sales=40,
            is_cancellation=True,
            departure_time=self.base_time + timedelta(hours=72),
            reward_points_available=0
        )
        
        # Expected original price calculation:
        # price_factor = (40/100) * 0.8 = 0.32
        # final_price = 100 * 0.32 * 3 = 96
        # refund_amount = 96 (full refund)
        
        assert result.confirmation is False
        assert result.total_price == 0.0
        assert abs(result.refund_amount - 96.0) < 0.01
        assert result.points_used is False

    def test_cancellation_with_partial_refund(self):
        """
        Test to cover cancellation edges:
        - 11->12: is_cancellation = True
        - 12->15: hours_to_departure < 48 (partial refund)
        - 15->17: return
        """
        result = self.system.book_flight(
            passengers=2,
            booking_time=self.base_time,
            available_seats=10,
            current_price=80.0,
            previous_sales=50,
            is_cancellation=True,
            departure_time=self.base_time + timedelta(hours=24),
            reward_points_available=0
        )
        
        # Expected original price calculation:
        # price_factor = (50/100) * 0.8 = 0.4
        # final_price = 80 * 0.4 * 2 = 64
        # refund_amount = 64 * 0.5 = 32 (partial refund)
        
        assert result.confirmation is False
        assert result.total_price == 0.0
        assert abs(result.refund_amount - 32.0) < 0.01
        assert result.points_used is False
