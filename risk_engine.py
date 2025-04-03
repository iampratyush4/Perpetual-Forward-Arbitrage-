class RiskEngine:
    def __init__(self, initial_equity=100000):
        self.equity = initial_equity
    
    def calculate_position_size(self, basis: float, max_alloc: float):
        edge = abs(basis) - 0.0015  # Minimum profit threshold
        win_prob = 0.6  # Assumed 60% success rate
        if edge <= 0:
            return 0
        kelly_fraction = (win_prob * edge - (1 - win_prob)) / edge
        return min(self.equity * kelly_fraction, self.equity * max_alloc)