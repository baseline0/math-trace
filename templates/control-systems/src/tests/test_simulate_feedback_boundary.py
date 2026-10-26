"""The feedback simulator accepts only single-input, single-output systems and says so before simulating."""

import numpy as np
import pytest

from ..model import LinearSystem, PIDController, simulate_feedback_system


def _controller():
    return PIDController(1.0, 0.5, 0.1, setpoint=1.0)


def test_rejects_two_inputs():
    system = LinearSystem(np.array([[-1.0]]), np.array([[1.0, 0.0]]), np.array([[1.0]]))

    with pytest.raises(NotImplementedError, match="2 inputs and 1 outputs"):
        simulate_feedback_system(system, _controller(), t_sim=1.0, dt=0.01)


def test_rejects_two_outputs():
    system = LinearSystem(np.array([[-1.0]]), np.array([[1.0]]), np.array([[1.0], [1.0]]))

    with pytest.raises(NotImplementedError, match="1 inputs and 2 outputs"):
        simulate_feedback_system(system, _controller(), t_sim=1.0, dt=0.01)


def test_single_input_single_output_still_simulates():
    system = LinearSystem(np.array([[-1.0]]), np.array([[1.0]]), np.array([[1.0]]))

    t, _x, y, u = simulate_feedback_system(system, _controller(), t_sim=1.0, dt=0.01)

    assert len(t) == len(y) == len(u) == 100
